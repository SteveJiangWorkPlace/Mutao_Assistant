from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

from app.api import ps_write

# 创建FastAPI应用
app = FastAPI(
    title="Mutao Assistant API",
    description="PS写作工具后端API",
    version="1.0.0"
)

# 自定义异常
class GeminiAPIError(Exception):
    """Gemini API调用异常"""
    pass

class InvalidAPIKeyError(Exception):
    """无效API密钥异常"""
    pass

# 全局异常处理器
@app.exception_handler(GeminiAPIError)
async def gemini_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Gemini API错误: {str(exc)}"}
    )

@app.exception_handler(InvalidAPIKeyError)
async def invalid_api_key_exception_handler(request, exc):
    return JSONResponse(
        status_code=401,
        content={"detail": f"API密钥无效: {str(exc)}"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(ps_write.router)

@app.get("/")
async def root():
    return {"message": "Mutao Assistant API 运行中"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }