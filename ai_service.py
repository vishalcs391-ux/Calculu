"""
AIService — the single entry point the rest of the app uses for AI calls.
Routers/services never import a provider directly; they import AIService.

This keeps AI "behind a service layer" per the architecture requirement:
swap providers via AI_PROVIDER env var, no other code changes.
"""
import json
import re

from app.core.config import settings
from app.services.ai.ollama_provider import OllamaProvider
from app.services.ai.huggingface_provider import HuggingFaceProvider
from app.services.ai.openai_provider import OpenAIProvider


class AIService:
    def __init__(self):
        self._provider = self._select_provider()

    def _select_provider(self):
        if settings.AI_PROVIDER == "ollama":
            return OllamaProvider()
        if settings.AI_PROVIDER == "huggingface":
            return HuggingFaceProvider()
        if settings.AI_PROVIDER == "openai":
            return OpenAIProvider()
        raise ValueError(f"Unknown AI_PROVIDER: {settings.AI_PROVIDER}")

    def _generate_json(self, prompt: str, system: str, max_tokens: int = 2048) -> dict | list:
        """Ask the model for JSON and parse it defensively (models sometimes
        wrap JSON in prose or markdown fences)."""
        raw = self._provider.generate(prompt, system=system, max_tokens=max_tokens)
        match = re.search(r"\[.*\]|\{.*\}", raw, re.DOTALL)
        json_str = match.group(0) if match else raw
        return json.loads(json_str)

    # ---- Step 1: summarize uploaded content into structured notes ----
    def summarize(self, raw_text: str) -> dict:
        system = (
            "You are a study assistant. Turn source material into clear, "
            "well-structured markdown notes for a student. Be concise and accurate."
        )
        prompt = (
            f"Summarize the following content into markdown notes with headings "
            f"and bullet points, then list 5-10 key points as a JSON array.\n\n"
            f"Return ONLY valid JSON: {{\"content_md\": string, \"key_points\": string[]}}\n\n"
            f"CONTENT:\n{raw_text[:12000]}"
        )
        return self._generate_json(prompt, system)

    # ---- Step 2: convert notes into flashcards ----
    def generate_flashcards(self, notes_md: str, count: int = 12) -> list[dict]:
        system = "You create effective active-recall flashcards from study notes."
        prompt = (
            f"Create {count} flashcards from these notes. "
            f"Return ONLY a JSON array: [{{\"question\": string, \"answer\": string, "
            f"\"difficulty\": \"easy\"|\"medium\"|\"hard\"}}]\n\nNOTES:\n{notes_md[:8000]}"
        )
        return self._generate_json(prompt, system)

    # ---- Step 3: generate a quiz from notes ----
    def generate_quiz(self, notes_md: str, num_questions: int = 10, difficulty: str = "medium") -> list[dict]:
        system = "You create fair, exam-style multiple-choice quizzes."
        prompt = (
            f"Create {num_questions} multiple-choice questions at {difficulty} difficulty "
            f"from these notes. Each question has exactly 4 options.\n"
            f"Return ONLY a JSON array: [{{\"question\": string, \"options\": string[4], "
            f"\"correct_index\": int, \"explanation\": string}}]\n\nNOTES:\n{notes_md[:8000]}"
        )
        return self._generate_json(prompt, system)

    # ---- Step 4: explain answers / general tutoring in chat ----
    def tutor_reply(self, message: str, context_md: str = "") -> str:
        system = (
            "You are a patient, encouraging AI study tutor. Explain concepts "
            "clearly with simple examples. Keep answers focused and student-friendly."
        )
        prompt = f"Study context:\n{context_md[:4000]}\n\nStudent question:\n{message}" if context_md else message
        return self._provider.generate(prompt, system=system, max_tokens=800)

    # ---- Step 5: produce a practice test at appropriate difficulty ----
    def generate_practice_test(self, combined_notes_md: str, num_questions: int, difficulty: str) -> list[dict]:
        system = "You design exam-style practice tests that mirror real test conditions."
        prompt = (
            f"Create a {num_questions}-question practice test at {difficulty} difficulty, "
            f"covering the material below broadly (not just the start).\n"
            f"Return ONLY a JSON array: [{{\"question\": string, \"options\": string[4], "
            f"\"correct_index\": int, \"explanation\": string}}]\n\nMATERIAL:\n{combined_notes_md[:10000]}"
        )
        return self._generate_json(prompt, system)


ai_service = AIService()
