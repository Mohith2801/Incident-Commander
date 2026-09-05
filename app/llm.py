from __future__ import annotations

from functools import lru_cache
from typing import Any

from langchain_groq import ChatGroq

from app.config import settings


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    """
    Create and cache the configured Groq LLM.
    """

    provider = settings.llm_provider.lower().strip()

    if provider != "groq":
        raise ValueError(
            f"Unsupported LLM provider: {settings.llm_provider}"
        )

    if not settings.groq_api_key:
        raise ValueError(
            "GROQ_API_KEY is not configured. "
            "Add it to the .env file."
        )

    return ChatGroq(
        model=settings.llm_model,
        groq_api_key=settings.groq_api_key,
        temperature=0,
        max_retries=0,
        timeout=60,
    )


class LazyLLM:
    """
    Lazy wrapper around get_llm().
    """

    def __getattr__(
        self,
        name: str,
    ) -> Any:
        return getattr(
            get_llm(),
            name,
        )

    def __call__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return get_llm()(
            *args,
            **kwargs,
        )


llm = LazyLLM()