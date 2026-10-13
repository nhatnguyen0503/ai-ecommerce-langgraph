"""Application configuration, loaded from environment variables / .env file."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM (Groq -- https://console.groq.com for keys + the current model catalog)
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # Business rules
    return_window_days: int = 14
    auto_approve_refund_ceiling_eur: float = 100.0

    # Storage
    database_url: str = "sqlite:///./ecommerce.db"
    checkpoint_db_path: str = "./checkpoints.sqlite"

    # CORS
    frontend_origin: str = "http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()
