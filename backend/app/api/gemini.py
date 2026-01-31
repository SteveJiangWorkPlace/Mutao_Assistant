from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import google.generativeai as genai
import json
import asyncio
from datetime import datetime

router = APIRouter(prefix="/gemini", tags=["gemini"])

# 请求模型
class GeminiRequest(BaseModel):
    prompt: str
    api_key: str
    model_name: str = "gemini-2.5-pro"
    temperature: float = 0.7
    max_output_tokens: int = 2000

class PSWriteRequest(BaseModel):
    """PS写作请求参数"""
    school: str
    major: str
    courses: str
    extracurricular: str
    api_key: str
    model_name: str = "gemini-2.5-pro"
    temperature: float = 0.7
    max_output_tokens: int = 2000

class PSWriteStreamRequest(BaseModel):
    """PS写作流式请求参数"""
    school: str
    major: str
    courses: str
    extracurricular: str
    api_key: str
    model_name: str = "gemini-2.5-pro"
    temperature: float = 0.7
    max_output_tokens: int = 4000

def build_ps_write_prompt(school: str, major: str, courses: str, extracurricular: str) -> str:
    """构建PS写作提示词（从TypeScript迁移）"""
    return f"""你是一个留学申请顾问，需要根据申请者的背景信息，分析其课外经历与申请专业的匹配度，并提供专业领域的前沿研究方向和热点分析。

申请者信息：
- 目标学校：{school or '未填写'}
- 申请专业：{major or '未填写'}
- 相关课程信息：{courses or '未填写'}
- 课外经历：{extracurricular or '未填写'}

任务要求：
1. 从课外经历中提取与申请专业最相关的细分领域（申请者可能感兴趣的研究方向）
2. 针对这个细分领域，调研前沿的学术文献、行业报告或最新新闻
3. 分析该领域当前的热点问题、技术挑战或待解决的研究问题
4. 输出3个具体的研究方向，按照与申请者背景的匹配度从高到低排序

输出格式要求（请严格遵守）：
- 只输出纯文本，不要使用任何Markdown符号（如**、*、-、#等）
- 不要包含任何AI执行工作流的提示或解释性语言
- 每个研究方向按以下格式输出：
  [一句话概括主题，使用中文，加粗显示]（注意：实际输出时不要使用**符号，直接加粗文字）
  具体理由：详细说明为什么这个方向与申请者背景匹配，以及该方向的具体内容
  参考文献：列出参考的前沿学术文献、行业报告或新闻来源（使用斜体，但不要用*符号，直接斜体文字）

示例输出格式：
机器学习在医疗影像诊断中的应用
具体理由：申请者在课外经历中参与了医学影像处理项目，掌握了深度学习基础。当前医疗AI领域快速发展，该方向结合了申请者的计算机背景和医疗兴趣。
参考文献：Nature Medicine 2023年关于AI辅助诊断的综述；MIT Technology Review 2024年医疗AI行业报告

注意：实际输出时不要使用**或*等格式符号，直接使用加粗和斜体文字（用户会在富文本环境中查看）。"""

# 清理Markdown符号函数（从TypeScript迁移）
def clean_markdown(text: str) -> str:
    """清理Markdown符号"""
    # 分步清理所有Markdown符号
    cleaned = text
    # 移除粗体和斜体
    cleaned = cleaned.replace("**", "").replace("*", "")
    # 移除标题
    import re
    cleaned = re.sub(r'^#{1,6}\s+(.*)$', r'\1', cleaned, flags=re.MULTILINE)
    # 移除列表
    cleaned = re.sub(r'^[*-+]\s+(.*)$', r'\1', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'^\d+\.\s+(.*)$', r'\1', cleaned, flags=re.MULTILINE)
    # 移除代码块
    cleaned = re.sub(r'`{3}[\s\S]*?`{3}', '', cleaned)
    cleaned = cleaned.replace("`", "")
    # 移除引用块
    cleaned = re.sub(r'^>\s+(.*)$', r'\1', cleaned, flags=re.MULTILINE)
    # 移除水平线
    cleaned = re.sub(r'^[-*_]{3,}$', '', cleaned, flags=re.MULTILINE)
    # 移除链接和图片
    cleaned = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', cleaned)
    cleaned = re.sub(r'!\[(.*?)\]\(.*?\)', r'\1', cleaned)
    # 移除HTML标签
    cleaned = re.sub(r'<[^>]*>', '', cleaned)
    # 移除多余空行
    cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
    # 移除行首尾空格
    cleaned = re.sub(r'^\s+|\s+$', '', cleaned, flags=re.MULTILINE)

    return cleaned.strip()

@router.post("/generate")
async def generate_content(request: GeminiRequest):
    """普通文本生成端点"""
    try:
        # 强制使用gemini-2.5-pro模型
        forced_model_name = "gemini-2.5-pro"
        print(f"强制使用模型: {forced_model_name} (请求模型: {request.model_name})")

        # 配置Gemini API
        genai.configure(api_key=request.api_key)
        model = genai.GenerativeModel(forced_model_name)

        # 生成内容
        response = model.generate_content(
            request.prompt,
            generation_config={
                "temperature": request.temperature,
                "max_output_tokens": request.max_output_tokens,
            }
        )

        result = response.text if response.text else "未收到有效回复"

        return {
            "result": result,
            "model_used": forced_model_name,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")

@router.post("/ps-write/generate")
async def generate_ps_analysis(request: PSWriteRequest):
    """PS写作分析生成（非流式）"""
    try:
        # 构建提示词
        prompt = build_ps_write_prompt(
            request.school, request.major, request.courses, request.extracurricular
        )

        # 强制使用gemini-2.5-pro模型
        forced_model_name = "gemini-2.5-pro"
        print(f"PS写作强制使用模型: {forced_model_name} (请求模型: {request.model_name})")

        # 配置Gemini API
        genai.configure(api_key=request.api_key)
        model = genai.GenerativeModel(forced_model_name)

        # 生成内容
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": request.temperature,
                "max_output_tokens": request.max_output_tokens,
            }
        )

        result = response.text if response.text else "未收到有效回复"

        return {
            "result": result,
            "model_used": forced_model_name,
            "prompt_length": len(prompt),
            "response_length": len(result),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PS分析生成失败: {str(e)}")

async def generate_stream_response(prompt: str, api_key: str, model_name: str, temperature: float, max_tokens: int):
    """生成流式响应（核心逻辑）"""
    try:
        # 强制使用gemini-2.5-pro模型
        forced_model_name = "gemini-2.5-pro"
        print(f"强制使用模型: {forced_model_name} (请求模型: {model_name})")

        # 配置Gemini API
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(forced_model_name)

        # 流式生成
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            },
            stream=True
        )

        BUFFER_SIZE = 200  # 字符阈值
        UPDATE_INTERVAL = 0.05  # 50ms
        buffer = ""
        last_update = asyncio.get_event_loop().time()

        for chunk in response:
            if chunk.text:
                buffer += chunk.text
                current_time = asyncio.get_event_loop().time()

                # 达到阈值或时间间隔时发送
                if len(buffer) >= BUFFER_SIZE or (current_time - last_update) >= UPDATE_INTERVAL:
                    cleaned_buffer = buffer.replace("**", "").replace("*", "")
                    yield f"data: {json.dumps({'content': cleaned_buffer})}\n\n"
                    buffer = ""
                    last_update = current_time

        # 发送剩余缓冲
        if buffer:
            cleaned_buffer = buffer.replace("**", "").replace("*", "")
            yield f"data: {json.dumps({'content': cleaned_buffer})}\n\n"

        yield "data: [DONE]\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

@router.post("/stream")
async def stream_content(request: GeminiRequest):
    """流式文本生成端点"""
    return StreamingResponse(
        generate_stream_response(
            request.prompt,
            request.api_key,
            request.model_name,
            request.temperature,
            request.max_output_tokens
        ),
        media_type="text/event-stream"
    )

@router.post("/ps-write/stream")
async def stream_ps_analysis(request: PSWriteStreamRequest):
    """PS写作流式分析生成"""
    # 构建提示词
    prompt = build_ps_write_prompt(
        request.school, request.major, request.courses, request.extracurricular
    )

    return StreamingResponse(
        generate_stream_response(
            prompt,
            request.api_key,
            request.model_name,
            request.temperature,
            request.max_output_tokens
        ),
        media_type="text/event-stream"
    )

# 其他模块的提示词构建函数（预留接口）
def build_ps_review_prompt(text: str) -> str:
    """构建PS修改提示词（预留）"""
    return f"PS修改功能待实现，原文: {text[:100]}..."

def build_cv_write_prompt(experience: str) -> str:
    """构建CV写作提示词（预留）"""
    return f"CV写作功能待实现，经历: {experience[:100]}..."

def build_rl_write_prompt(info: str) -> str:
    """构建RL写作提示词（预留）"""
    return f"推荐信写作功能待实现，信息: {info[:100]}..."

@router.get("/modules")
async def get_available_modules():
    """获取可用模块列表"""
    return {
        "modules": [
            {"id": "ps-write", "name": "Personal Statement 写作工具", "description": "撰写个人陈述，突出学术背景、研究兴趣和职业目标"},
            {"id": "ps-review", "name": "Personal Statement 修改工具", "description": "优化和润色个人陈述，提高可读性和说服力"},
            {"id": "rl-write", "name": "Recommendation Letter 写作工具", "description": "撰写推荐信，展示申请人的能力和成就"},
            {"id": "cv-write", "name": "Curriculum Vitae 写作工具", "description": "创建专业的简历，突出教育背景、工作经验和技能"}
        ]
    }