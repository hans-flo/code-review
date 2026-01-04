from abc import ABC, abstractmethod
import os
from typing import Optional
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class LLMProvider(ABC):
    """LLM 제공자 추상 클래스 - 모델 교체 용이성을 위한 Strategy Pattern"""

    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """비동기로 답변 생성"""
        ...


class OllamaClient(LLMProvider):
    """Ollama 로컬 LLM 클라이언트"""

    def __init__(self, model_name: str = "qwen2.5-coder:14b"):
        from ollama import AsyncClient
        self.model_name = model_name
        self.client = AsyncClient()

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = await self.client.chat(
            model=self.model_name,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ]
        )
        return response['message']['content']


class OpenAIClient(LLMProvider):
    """OpenAI API 클라이언트 (신규 SDK 우선, 없으면 구버전 fallback)"""

    def __init__(self, model_name: str = "gpt-4o-mini", api_key: Optional[str] = None):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("API key is required. Set OPENAI_API_KEY in .env file or pass api_key parameter.")

        self._mode = "legacy"
        self.client = None

        try:
            from openai import AsyncOpenAI  # type: ignore
            self._mode = "v1"
            self.client = AsyncOpenAI(api_key=api_key)
        except ImportError:
            import openai  # type: ignore
            openai.api_key = api_key
            self.client = openai

        self.model_name = model_name

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        if self._mode == "v1":
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
            )
            return response.choices[0].message.content

        # legacy (동기 클라이언트를 쓰므로 스레드 풀에서 실행)
        import asyncio

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.ChatCompletion.create(
                model=self.model_name,
                messages=messages,
            ),
        )
        return response["choices"][0]["message"]["content"]


class GeminiClient(LLMProvider):
    """Google Gemini API 클라이언트"""

    def __init__(self, model_name: str = "gemini-1.5-flash", api_key: str | None = None):
        from google import genai
        self.model_name = model_name
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("API key is required. Set GOOGLE_API_KEY in .env file or pass api_key parameter.")
        self.client = genai.Client(api_key=api_key)

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        # Gemini는 system instruction과 user message를 분리
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"

        # 비동기 생성
        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.models.generate_content(
                model=self.model_name,
                contents=combined_prompt
            )
        )
        return response.text
