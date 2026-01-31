import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """应用配置"""
    # API配置 - 从环境变量GEMINI_API_KEY读取
    GEMINI_API_KEY: str = ""

    # 应用配置
    debug: bool = False
    session_ttl_minutes: int = 30
    max_retry_attempts: int = 3

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "env_prefix": "",  # 无前缀，直接使用变量名
    }

def get_settings() -> Settings:
    """获取配置实例"""
    return Settings()