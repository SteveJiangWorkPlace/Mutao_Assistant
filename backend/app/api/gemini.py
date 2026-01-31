from fastapi import APIRouter, HTTPException
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


@router.get("/test")
async def test_gemini_endpoint():
    """测试Gemini API端点"""
    return {
        "message": "Gemini API端点运行正常",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "generate": "POST /api/gemini/ps-write/generate"
        }
    }