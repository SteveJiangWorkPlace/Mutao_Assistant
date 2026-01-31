import google.generativeai as genai
import os
import asyncio
from typing import Optional
import httpx
from app.core.config import get_settings

class GeminiService:
    def __init__(self, api_key: str, use_proxy: bool = True):
        """
        初始化Gemini服务

        Args:
            api_key: Gemini API密钥
            use_proxy: 是否使用代理（本地开发需要）
        """
        self.api_key = api_key

        # 配置代理（本地开发）
        if use_proxy:
            settings = get_settings()
            if settings.http_proxy:
                os.environ['HTTP_PROXY'] = settings.http_proxy
                os.environ['HTTPS_PROXY'] = settings.https_proxy or settings.http_proxy
                # 为httpx配置代理
                self.proxies = {
                    'http://': settings.http_proxy,
                    'https://': settings.https_proxy or settings.http_proxy
                }
            else:
                self.proxies = None
        else:
            self.proxies = None

        # 配置Gemini
        genai.configure(api_key=api_key, transport='rest')

        # 使用指定的模型
        self.model_name = 'gemini-2.0-flash-exp'  # 可以使用gemini-2.5-pro，但需要API权限
        self.model = genai.GenerativeModel(self.model_name)

        # 重试配置
        self.max_retries = 3
        self.retry_delay = 1  # 秒

    async def generate_content_with_retry(self, prompt: str, max_retries: Optional[int] = None) -> str:
        """
        生成内容，带有重试机制

        Args:
            prompt: 提示词
            max_retries: 最大重试次数，默认使用类配置

        Returns:
            生成的文本内容

        Raises:
            Exception: 所有重试都失败后抛出异常
        """
        max_retries = max_retries or self.max_retries

        for attempt in range(max_retries + 1):
            try:
                # 使用异步生成内容
                response = await self.model.generate_content_async(prompt)
                return response.text
            except Exception as e:
                if attempt == max_retries:
                    raise Exception(f"Gemini API调用失败，重试{max_retries}次后仍失败: {str(e)}")

                # 等待后重试
                await asyncio.sleep(self.retry_delay * (attempt + 1))

                # 如果是认证错误，直接抛出，不需要重试
                if "API_KEY_INVALID" in str(e) or "PERMISSION_DENIED" in str(e):
                    raise Exception(f"Gemini API密钥无效: {str(e)}")
                elif "quota" in str(e).lower() or "rate limit" in str(e).lower():
                    raise Exception(f"Gemini API配额或速率限制: {str(e)}")

    async def generate_enhanced_research(self, prompt: str) -> str:
        """生成增强版调研结果"""
        try:
            return await self.generate_content_with_retry(prompt)
        except Exception as e:
            raise Exception(f"调研生成失败: {str(e)}")

    async def generate_personal_statement(self, prompt: str) -> str:
        """生成个人陈述"""
        try:
            return await self.generate_content_with_retry(prompt)
        except Exception as e:
            raise Exception(f"个人陈述生成失败: {str(e)}")

    async def test_connection(self) -> bool:
        """测试API连接"""
        try:
            test_prompt = "请回复'连接成功'"
            response = await self.generate_content_with_retry(test_prompt, max_retries=1)
            return '连接成功' in response
        except:
            return False

