from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime
from typing import List
import json
import asyncio

from app.models.schemas import PSWriteRequest
from app.services.gemini import GeminiService
from app.services.prompts import format_enhanced_research_prompt

router = APIRouter(prefix="/api/gemini", tags=["gemini"])

@router.post("/ps-write/generate")
async def generate_content(request: PSWriteRequest):
    """
    生成内容（非流式版本）

    与前端保持兼容的API端点
    """
    try:
        # 验证API密钥
        if not request.api_key or len(request.api_key) < 10:
            raise HTTPException(
                status_code=400,
                detail="请提供有效的Gemini API密钥"
            )

        # 初始化Gemini服务
        gemini = GeminiService(api_key=request.api_key)

        # 构建提示词
        prompt = format_enhanced_research_prompt(
            school=request.school,
            major=request.major,
            courses=request.courses,
            extracurricular=request.extracurricular
        )

        # 生成内容
        result = await gemini.generate_enhanced_research(prompt)

        return {
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成内容时出错: {str(e)}"
        )

@router.post("/ps-write/stream")
async def stream_content(request: PSWriteRequest):
    """
    流式生成内容

    返回Server-Sent Events (SSE)格式的流式响应
    """
    try:
        # 验证API密钥
        if not request.api_key or len(request.api_key) < 10:
            raise HTTPException(
                status_code=400,
                detail="请提供有效的Gemini API密钥"
            )

        # 初始化Gemini服务
        gemini = GeminiService(api_key=request.api_key)

        # 构建提示词
        prompt = format_enhanced_research_prompt(
            school=request.school,
            major=request.major,
            courses=request.courses,
            extracurricular=request.extracurricular
        )

        async def generate_stream():
            """生成流式响应"""
            try:
                # 使用流式生成
                async for chunk in gemini.generate_content_stream(prompt):
                    # 格式化为SSE格式
                    data = json.dumps({"content": chunk})
                    yield f"data: {data}\n\n"

                # 发送完成信号
                yield "data: [DONE]\n\n"

            except Exception as e:
                # 发送错误信息
                error_data = json.dumps({"error": str(e)})
                yield f"data: {error_data}\n\n"

        # 返回流式响应
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # 禁用Nginx缓冲
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"流式生成失败: {str(e)}"
        )

@router.get("/test")
async def test_gemini_endpoint():
    """测试Gemini API端点"""
    return {
        "message": "Gemini API端点运行正常",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "generate": "POST /api/gemini/ps-write/generate",
            "stream": "POST /api/gemini/ps-write/stream"
        }
    }