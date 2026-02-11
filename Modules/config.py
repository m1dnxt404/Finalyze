"""
Provider configuration and shared constants.
"""

PROVIDERS = {
    "anthropic": {
        "name": "Anthropic (Claude)",
        "env_key": "ANTHROPIC_API_KEY",
        "default_model": "claude-sonnet-4-20250514",
    },
    "openai": {
        "name": "OpenAI (GPT)",
        "env_key": "OPENAI_API_KEY",
        "default_model": "gpt-4o",
    },
    "gemini": {
        "name": "Google Gemini",
        "env_key": "GEMINI_API_KEY",
        "default_model": "gemini-2.0-flash",
    },
    "deepseek": {
        "name": "DeepSeek",
        "env_key": "DEEPSEEK_API_KEY",
        "default_model": "deepseek-chat",
    },
}

DEFAULT_MAX_TOKENS = 4000
DEFAULT_TEMPERATURE = 0.3
