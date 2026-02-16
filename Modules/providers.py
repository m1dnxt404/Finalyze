"""
LangChain ChatModel factory.
Creates a unified chat model interface for all supported providers.
"""

import os
from typing import Optional

from langchain_core.language_models.chat_models import BaseChatModel

from .config import PROVIDERS, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS


def create_model(provider: str, api_key: Optional[str] = None) -> BaseChatModel:
    """
    Create a LangChain ChatModel for the given provider.

    Args:
        provider: One of "anthropic", "openai", "gemini", "deepseek", "ollama"
        api_key: API key (defaults to provider-specific env variable)

    Returns:
        A LangChain BaseChatModel instance with unified .invoke() interface
    """
    if provider not in PROVIDERS:
        raise ValueError(
            f"Unknown provider '{provider}'. Choose from: {list(PROVIDERS.keys())}"
        )

    config = PROVIDERS[provider]
    model = config["default_model"]
    key = api_key or os.environ.get(config.get("env_key", ""))

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model,
            api_key=key,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS,
        )

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model,
            api_key=key,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS,
        )

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=key,
            temperature=DEFAULT_TEMPERATURE,
            max_output_tokens=DEFAULT_MAX_TOKENS,
        )

    if provider == "deepseek":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model,
            api_key=key,
            base_url="https://api.deepseek.com",
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS,
        )

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=model,
            temperature=DEFAULT_TEMPERATURE,
            num_predict=DEFAULT_MAX_TOKENS,
        )

    raise ValueError(f"Unknown provider: {provider}")
