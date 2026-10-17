import pytest
from pydantic import ValidationError

from app.config import Settings


def test_default_to_dev_without_env_file(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    settings = Settings(_env_file=None)
    assert settings.app_env == "dev"


def test_prod_without_api_key_fails(monkeypatch):
    monkeypatch.setenv("APP_ENV", "prod")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(ValidationError, match="GROQ_API_KEY"):
        Settings(_env_file=None)


def test_prod_with_api_key_ok(monkeypatch):
    monkeypatch.setenv("APP_ENV", "prod")
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test")
    settings = Settings(_env_file=None)
    assert settings.app_env == "prod"


def test_invalid_app_env_rejected(monkeypatch):
    monkeypatch.setenv("APP_ENV", "invalid")
    with pytest.raises(ValidationError, match="app_env"):
        Settings(_env_file=None)


def test_refund_ceiling_read_from_env(monkeypatch):
    monkeypatch.setenv("AUTO_APPROVE_REFUND_CEILING_EUR", "250.0")
    settings = Settings(_env_file=None)
    assert settings.auto_approve_refund_ceiling_eur == 250.0


def test_api_key_hidden_in_repr(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test")
    settings = Settings(_env_file=None)
    repr_str = repr(settings)
    assert "gsk_test" not in repr_str
    assert "groq_api_key" in repr_str
