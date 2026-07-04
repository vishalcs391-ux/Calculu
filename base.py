"""
Abstract AI provider interface.

Every provider (Ollama, HuggingFace, OpenAI, Anthropic...) implements this
same contract. The rest of the app NEVER talks to a provider directly —
it only talks to AIService (ai_service.py), which picks the provider
based on settings.AI_PROVIDER. This is what makes providers swappable
without touching routers/services.
"""
from abc import ABC, abstractmethod


class AIProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system: str = "", max_tokens: int = 1024) -> str:
        """Return a plain-text completion for the given prompt."""
        raise NotImplementedError
