"""
Hugging Face Inference API provider — fallback when Ollama isn't available
(e.g. deployed backend with no local GPU).
"""
import requests

from app.services.ai.base import AIProvider
from app.core.config import settings


class HuggingFaceProvider(AIProvider):
    def generate(self, prompt: str, system: str = "", max_tokens: int = 1024) -> str:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        resp = requests.post(
            f"https://api-inference.huggingface.co/models/{settings.HUGGINGFACE_MODEL}",
            headers={"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"},
            json={"inputs": full_prompt, "parameters": {"max_new_tokens": max_tokens}},
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and data and "generated_text" in data[0]:
            return data[0]["generated_text"].strip()
        return str(data)
