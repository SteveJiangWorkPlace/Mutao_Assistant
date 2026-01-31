#!/usr/bin/env python3
"""
Mutao Assistant 后端启动脚本
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式启用热重载
        log_level="info"
    )