"""
Centralized configuration. All values come from environment variables
so the same code runs locally, on Render/Railway, and in CI.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "AI Super Study Platform"
    ENV: str = "development"  # development | staging | production
    API_V1_PREFIX: str = "/api/v1"
    FRONTEND_ORIGIN: str = "http://localhost:5500"

    # --- Database ---
    DATABASE_URL: str = "postgresql+psycopg://study_user:study_pass@localhost:5432/study_platform"

    # --- Firebase Auth ---
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_SERVICE_ACCOUNT_JSON: str = ""  # path to service account json, or inline JSON

    # --- AI Provider selection ---
    # ollama (local, default/free) | huggingface | openai | anthropic
    AI_PROVIDER: str = "ollama"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"
    HUGGINGFACE_API_KEY: str = ""
    HUGGINGFACE_MODEL: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"

    # --- File storage ---
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_MB: int = 25

    # --- YouTube ---
    YOUTUBE_API_KEY: str = ""  # optional, only needed for metadata lookups

    # --- Billing (Stripe placeholders) ---
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_PREMIUM_MONTHLY: str = ""
    STRIPE_PRICE_STUDENT_YEARLY: str = ""

    # --- Free plan limits (usage caps) ---
    FREE_PLAN_MAX_SOURCES_PER_MONTH: int = 5
    FREE_PLAN_MAX_QUIZZES_PER_MONTH: int = 10
    FREE_PLAN_MAX_TUTOR_MESSAGES_PER_DAY: int = 20

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
