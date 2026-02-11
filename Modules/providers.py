"""
AI provider client factory and unified API call interface.
Supports Anthropic, OpenAI, Gemini, and DeepSeek.
"""

import os
from typing import Optional
from .config import PROVIDERS, DEFAULT_TEMPERATURE


def create_client(provider: str, api_key: Optional[str] = None):
    """Create an API client for the given provider using lazy imports."""
    config = PROVIDERS[provider]
    key = api_key or os.environ.get(config["env_key"])

    if provider == "anthropic":
        from anthropic import Anthropic
        return Anthropic(api_key=key)

    if provider == "openai":
        from openai import OpenAI
        return OpenAI(api_key=key)

    if provider == "gemini":
        from google import genai
        return genai.Client(api_key=key)

    if provider == "deepseek":
        from openai import OpenAI
        return OpenAI(api_key=key, base_url="https://api.deepseek.com")

    raise ValueError(f"Unknown provider: {provider}")


def call_provider(client, provider: str, model: str, prompt: str,
                  max_tokens: int = 4000) -> tuple[str, dict]:
    """
    Send a prompt to the configured provider and return (response_text, usage).

    Each provider SDK has a different call shape — this function abstracts that.
    """
    if provider == "anthropic":
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=DEFAULT_TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text, {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens,
        }

    if provider in ("openai", "deepseek"):
        response = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=DEFAULT_TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content, {
            "input": response.usage.prompt_tokens,
            "output": response.usage.completion_tokens,
        }

    if provider == "gemini":
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "temperature": DEFAULT_TEMPERATURE,
                "max_output_tokens": max_tokens,
            },
        )
        return response.text, {
            "input": response.usage_metadata.prompt_token_count,
            "output": response.usage_metadata.candidates_token_count,
        }

    raise ValueError(f"Unknown provider: {provider}")
