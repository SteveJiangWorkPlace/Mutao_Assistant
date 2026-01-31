from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import List

from app.models.schemas import (
    PSWriteRequest, PSGenerationRequest, PersonalStatement,
    ResearchOptionsResponse, ErrorResponse, ResearchOption
)
from app.services.gemini import GeminiService
from app.services.selection import SelectionService
from app.services.cache import ResearchCache
from app.services.prompts import (
    format_enhanced_research_prompt,
    format_personal_statement_prompt,
    validate_enhanced_research_prompt,
    validate_personal_statement_prompt
)
from app.services.parser import (
    parse_research_options,
    parse_research_options_with_domain_texts,
    parse_personal_statement,
    enhance_research_option_with_scoring,
    validate_and_score_references
)
from app.core.config import get_settings

settings = get_settings()

router = APIRouter(prefix="/api/ps-write", tags=["ps-write"])

# 初始化服务
selection_service = SelectionService()
research_cache = ResearchCache(ttl_hours=24, max_entries=1000)

@router.post("/generate-with-selection", response_model=ResearchOptionsResponse)
async def generate_research_options(request: PSWriteRequest):
    """
    生成调研选项供用户选择

    - 接收用户背景信息
    - 调用Gemini生成3个细分领域调研
    - 创建会话并返回会话ID和调研选项
    """
    try:
        # 从环境变量获取API密钥
        api_key = settings.GEMINI_API_KEY
        if not api_key or len(api_key) < 10:
            raise HTTPException(
                status_code=500,
                detail="服务器未配置Gemini API密钥，请联系管理员设置GEMINI_API_KEY环境变量"
            )

        # 检查缓存
        cached_research = research_cache.get_cached_research(
            school=request.school,
            major=request.major,
            courses=request.courses,
            extracurricular=request.extracurricular
        )

        if cached_research:
            # 使用缓存结果
            research_options = cached_research
            cache_hit = True
        else:
            # 缓存未命中，调用Gemini API
            cache_hit = False

            # 初始化Gemini服务
            gemini = GeminiService(api_key=api_key)

            # 测试连接（可选）
            # if not await gemini.test_connection():
            #     raise HTTPException(status_code=401, detail="Gemini API密钥无效或连接失败")

            # 构建提示词
            prompt = format_enhanced_research_prompt(
                school=request.school,
                major=request.major,
                courses=request.courses,
                extracurricular=request.extracurricular
            )

            # 生成调研结果
            research_text = await gemini.generate_enhanced_research(prompt)

            # 解析调研结果（获取选项和原始文本）
            try:
                research_options, domain_texts = parse_research_options_with_domain_texts(research_text)
            except ValueError as e:
                # 如果解析失败，记录原始文本并返回错误
                raise HTTPException(
                    status_code=500,
                    detail=f"解析调研结果失败: {str(e)}。原始文本: {research_text[:500]}..."
                )

            # 验证解析结果
            if len(research_options) != 3:
                raise HTTPException(
                    status_code=500,
                    detail=f"期望3个调研选项，但解析出{len(research_options)}个"
                )

            # 增强调研选项（使用评分算法和参考文献验证）
            enhanced_options = []
            for i, option in enumerate(research_options):
                domain_text = domain_texts[i] if i < len(domain_texts) else ""
                enhanced_option = enhance_research_option_with_scoring(
                    option=option,
                    original_text=domain_text,
                    user_courses=request.courses,
                    user_extracurricular=request.extracurricular
                )
                enhanced_options.append(enhanced_option)

            # 更新为增强后的选项
            research_options = enhanced_options

            # 缓存增强后的结果
            research_cache.cache_research(
                school=request.school,
                major=request.major,
                courses=request.courses,
                extracurricular=request.extracurricular,
                research_options=research_options
            )

        # 注意：缓存命中的情况下，research_options已经是增强后的选项

        # 创建会话
        session_id = selection_service.create_session(research_options)

        # 添加缓存命中信息到消息
        message = "请从以上3个选项中选择一个作为文书写作方向"
        if cache_hit:
            message += " (结果来自缓存)"

        return ResearchOptionsResponse(
            session_id=session_id,
            research_options=research_options,
            message=message
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成调研选项时出错: {str(e)}"
        )

@router.post("/generate-ps", response_model=PersonalStatement)
async def generate_personal_statement(request: PSGenerationRequest):
    """
    基于用户选择生成个人陈述

    - 验证用户选择的有效性
    - 调用Gemini生成5段式个人陈述
    - 返回格式化后的个人陈述
    """
    try:
        # 验证选择索引
        selection_index = request.selection.selection_index
        if not (0 <= selection_index < 3):
            raise HTTPException(
                status_code=400,
                detail="选择索引必须在0-2范围内"
            )

        # 获取选择的选项
        research_options = request.selection.research_options
        if selection_index >= len(research_options):
            raise HTTPException(
                status_code=400,
                detail=f"选择索引{selection_index}超出选项范围({len(research_options)}个选项)"
            )

        selected_option = research_options[selection_index]

        # 从环境变量获取API密钥
        api_key = settings.GEMINI_API_KEY
        if not api_key or len(api_key) < 10:
            raise HTTPException(
                status_code=500,
                detail="服务器未配置Gemini API密钥，请联系管理员设置GEMINI_API_KEY环境变量"
            )

        # 初始化Gemini服务
        gemini = GeminiService(api_key=api_key)

        # 构建个人陈述提示词
        prompt = format_personal_statement_prompt(
            school=request.school,
            major=request.major,
            courses=request.courses,
            extracurricular=request.extracurricular,
            selected_domain=selected_option.title
        )

        # 生成个人陈述
        ps_text = await gemini.generate_personal_statement(prompt)

        # 解析段落
        paragraphs = parse_personal_statement(ps_text)

        return PersonalStatement(
            paragraphs=paragraphs,
            selected_domain=selected_option.title,
            generated_at=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成个人陈述时出错: {str(e)}"
        )

@router.get("/test-gemini")
async def test_gemini_integration():
    """
    测试Gemini集成

    - 测试环境变量中的API密钥有效性
    - 测试Gemini连接
    """
    try:
        # 从环境变量获取API密钥
        api_key = settings.GEMINI_API_KEY
        if not api_key or len(api_key) < 10:
            raise HTTPException(
                status_code=500,
                detail="服务器未配置Gemini API密钥，请联系管理员设置GEMINI_API_KEY环境变量"
            )

        gemini = GeminiService(api_key=api_key)
        is_connected = await gemini.test_connection()

        if is_connected:
            return {
                "status": "success",
                "message": "Gemini API连接成功",
                "model": gemini.model_name
            }
        else:
            raise HTTPException(
                status_code=401,
                detail="Gemini API连接测试失败"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gemini测试失败: {str(e)}"
        )

@router.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """
    获取会话信息

    - 验证会话是否存在
    - 返回会话中的调研选项
    """
    session = selection_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail="会话不存在或已过期"
        )

    research_options = selection_service.get_research_options(session_id)
    return {
        "session_id": session_id,
        "created_at": session['created_at'].isoformat(),
        "research_options": [opt.dict() for opt in research_options] if research_options else []
    }

@router.get("/test-prompt-format")
async def test_prompt_format():
    """
    测试提示词格式

    - 验证两个核心提示词的格式是否正确
    - 检查占位符和必要部分
    """
    # 测试增强版调研提示词
    test_school = "清华大学"
    test_major = "计算机科学"
    test_courses = "数据结构、算法设计、人工智能"
    test_extracurricular = "参与开源项目开发，实习于科技公司"
    test_selected_domain = "人工智能伦理"

    enhanced_prompt = format_enhanced_research_prompt(
        school=test_school,
        major=test_major,
        courses=test_courses,
        extracurricular=test_extracurricular
    )

    personal_statement_prompt = format_personal_statement_prompt(
        school=test_school,
        major=test_major,
        courses=test_courses,
        extracurricular=test_extracurricular,
        selected_domain=test_selected_domain
    )

    # 验证提示词
    enhanced_errors = validate_enhanced_research_prompt(enhanced_prompt)
    ps_errors = validate_personal_statement_prompt(personal_statement_prompt)

    return {
        "enhanced_research_prompt": {
            "length": len(enhanced_prompt),
            "errors": enhanced_errors,
            "has_errors": len(enhanced_errors) > 0,
            "preview": enhanced_prompt[:200] + "..." if len(enhanced_prompt) > 200 else enhanced_prompt
        },
        "personal_statement_prompt": {
            "length": len(personal_statement_prompt),
            "errors": ps_errors,
            "has_errors": len(ps_errors) > 0,
            "preview": personal_statement_prompt[:200] + "..." if len(personal_statement_prompt) > 200 else personal_statement_prompt
        },
        "timestamp": datetime.now().isoformat()
    }

@router.get("/cache-stats")
async def get_cache_stats():
    """
    获取缓存统计信息

    - 缓存条目数量
    - 缓存命中率（需要记录访问统计）
    - 缓存配置信息
    """
    stats = research_cache.get_cache_stats()
    return {
        "cache_stats": stats,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/validate-references")
async def validate_references_test(references: List[str]):
    """
    测试参考文献验证

    - 验证参考文献格式和质量
    - 返回评分和错误信息
    """
    try:
        valid_refs, score, errors = validate_and_score_references(references)

        return {
            "original_count": len(references),
            "valid_count": len(valid_refs),
            "quality_score": score,
            "valid_references": valid_refs,
            "validation_errors": errors,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"参考文献验证失败: {str(e)}"
        )

@router.get("/clear-cache")
async def clear_research_cache():
    """
    清空调研缓存

    - 用于测试和调试
    """
    research_cache.clear_cache()
    return {
        "message": "缓存已清空",
        "timestamp": datetime.now().isoformat()
    }