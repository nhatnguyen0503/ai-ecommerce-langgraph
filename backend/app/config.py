from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent  # .../backend


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    # Environment
    app_env: Literal["dev", "test", "prod"] = "dev"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # LLM (Groq -- https://console.groq.com for keys + the current model catalog)
    groq_api_key: SecretStr = SecretStr("")
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

    # Auth (JWT)
    jwt_secret_key: SecretStr = SecretStr("")
    jwt_algorithm: Literal["HS256"] = "HS256"
    access_token_expire_minutes: int = 30
    # Dev-only demo accounts (skipped when empty or when APP_ENV=prod)
    seed_demo_password: SecretStr = SecretStr("")

    @model_validator(mode="after")
    def _require_key_in_prod(self):
        if self.app_env == "prod" and not self.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY is required when APP_ENV=prod. "
                "Set it as an environment variable or in backend/.env."
            )
        if self.app_env == "prod" and len(self.jwt_secret_key.get_secret_value()) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters when APP_ENV=prod.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
