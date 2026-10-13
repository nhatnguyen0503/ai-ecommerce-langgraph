"""Single place that constructs the Groq-hosted chat model used across nodes."""
from langchain_groq import ChatGroq

from app_reference.config import get_settings

_settings = get_settings()

_model: ChatGroq | None = None


def get_llm() -> ChatGroq:
    global _model
    if _model is None:
        _model = ChatGroq(
            model=_settings.groq_model,
            api_key=_settings.groq_api_key or None,
            temperature=0,
            max_tokens=1024,
        )
    return _model
