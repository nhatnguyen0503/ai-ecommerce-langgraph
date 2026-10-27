from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, model_validator
from pathlib import Path
from typing import Literal

BACKEND_DIR = Path(__file__).resolve().parent.parent  # .../backend


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    # Environment
    app_env: Literal["dev", "test", "prod"] = "dev"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # LLM (Groq -- https://console.groq.com for keys + the current model catalog)
    groq_api_key: SecretStr = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # Business rules
    return_window_days: int = 14
    auto_approve_refund_ceiling_eur: float = 100.0

    # Storage
    # NOTE: relative paths, resolved from CWD; replaced by Postgres URL in item #5
    database_url: str = "sqlite:///./ecommerce.db"
    checkpoint_db_path: str = "./checkpoints.sqlite"

    # CORS
    frontend_origin: str = "http://localhost:5173"

    @model_validator(mode="after")
    def _require_key_in_prod(self):
        if self.app_env == "prod" and not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is required when APP_ENV=prod. Set it as an environment variable or in backend/.env.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
