from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    groq_api_key: str =""
    groq_model: str ="llama-3.3-70b-versatile"

    return_window_days: int = 14
    auto_approve_refund_ceiling_eur: float = 100.0

    database_url: str = "sqlite:///./ecommerce.db"


@lru_cache
def get_settings()->Settings:
    return Settings()