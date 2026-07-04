"""
Cloud fallback provider using OpenAI-compatible chat completions.
Also works with any OpenAI-compatible endpoint (Groq, Together, etc.)
by overriding the base URL if you extend this class later.
"""
from openai import OpenAI

from app.services.ai.base import AIProvider
from app.core.config import settings


class OpenAIProvider(AIProvider):
    def __init__(self):
        self._client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate(self, prompt: str, system: str = "", max_tokens: int = 1024) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        resp = self._client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content.strip()
