import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置"""
    # API配置
    gemini_api_key: str  # 保留，但实际通过前端传递

    # 应用配置
    debug: bool = True
    session_ttl_minutes: int = 30
    max_retry_attempts: int = 3

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def get_settings() -> Settings:
    """获取配置实例"""
    return Settings()