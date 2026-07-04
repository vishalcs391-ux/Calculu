"""
Local Ollama provider — default for MVP so there's zero API cost while building.
Requires `ollama serve` running locally with a model pulled, e.g.:
    ollama pull llama3.1
"""
import requests

from app.services.ai.base import AIProvider
from app.core.config import settings


class OllamaProvider(AIProvider):
    def generate(self, prompt: str, system: str = "", max_tokens: int = 1024) -> str:
        resp = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "system": system,
                "stream": False,
                "options": {"num_predict": max_tokens},
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
