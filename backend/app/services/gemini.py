import google.genai as genai
import asyncio
import sys
from typing import Optional

class GeminiService:
    def __init__(self, api_key: str):
        """
        初始化Gemini服务

        Args:
            api_key: Gemini API密钥
        """
        self.api_key = api_key

        # 配置Gemini
        sys.stderr.write(f"[DEBUG] 配置genai，api_key长度: {len(api_key)}\n")
        self.client = genai.Client(api_key=api_key)
        sys.stderr.write("[DEBUG] genai.Client创建完成\n")

        # 使用指定的模型
        self.model_name = 'gemini-2.5-pro'  # 强制使用2.5-pro模型，需要API权限
        sys.stderr.write(f"[DEBUG] GeminiService初始化，模型名称: {self.model_name}\n")

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
        sys.stderr.write(f"[DEBUG] generate_content_with_retry调用，模型: {self.model_name}, 尝试次数: {max_retries}\n")

        for attempt in range(max_retries + 1):
            try:
                sys.stderr.write(f"[DEBUG] 尝试 {attempt+1}/{max_retries+1}: 调用generate_content_async\n")
                # 使用异步生成内容
                response = await self.client.aio.models.generate_content(model=self.model_name, contents=prompt)
                sys.stderr.write(f"[DEBUG] 生成成功，响应长度: {len(response.text)}\n")
                return response.text
            except Exception as e:
                sys.stderr.write(f"[DEBUG] 尝试 {attempt+1} 失败: {type(e).__name__}: {str(e)}\n")
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
            sys.stderr.write(f"[DEBUG] generate_enhanced_research调用，使用模型: {self.model_name}\n")
            return await self.generate_content_with_retry(prompt)
        except Exception as e:
            sys.stderr.write(f"[DEBUG] generate_enhanced_research失败: {str(e)}\n")
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

