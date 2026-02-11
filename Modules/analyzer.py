"""
Core EarningsReportAnalyzer class.
Orchestrates prompt building, provider calls, and JSON parsing.
"""

import json
from typing import Dict, Optional
from datetime import datetime

from .config import PROVIDERS
from .providers import create_client, call_provider
from .prompts import build_analysis_prompt, build_comparison_prompt


class EarningsReportAnalyzer:
    def __init__(self, provider: str = "anthropic", api_key: Optional[str] = None):
        """
        Args:
            provider: AI provider to use ("anthropic", "openai", "gemini", "deepseek")
            api_key: API key (defaults to provider-specific env variable)
        """
        if provider not in PROVIDERS:
            raise ValueError(
                f"Unknown provider '{provider}'. Choose from: {list(PROVIDERS.keys())}"
            )
        self.provider = provider
        self.model = PROVIDERS[provider]["default_model"]
        self.client = create_client(provider, api_key)

    def analyze_earnings(self, earnings_text: str, company_name: str = None) -> Dict:
        """Analyze an earnings report and return structured results."""
        prompt = build_analysis_prompt(earnings_text, company_name)

        try:
            raw, usage = call_provider(
                self.client, self.provider, self.model, prompt
            )
            data = json.loads(_extract_json(raw))
            data["metadata"] = {
                "analyzed_at": datetime.now().isoformat(),
                "provider": self.provider,
                "model_used": self.model,
                "token_usage": usage,
            }
            return data

        except json.JSONDecodeError as e:
            return {
                "error": "Failed to parse JSON response",
                "raw_analysis": raw,
                "exception": str(e),
            }
        except Exception as e:
            return {"error": "Analysis failed", "exception": str(e)}

    def compare_earnings(self, current_report: str, previous_report: str,
                         company_name: str = None) -> Dict:
        """Compare two earnings reports to identify trends."""
        prompt = build_comparison_prompt(current_report, previous_report, company_name)

        try:
            raw, _ = call_provider(
                self.client, self.provider, self.model, prompt, max_tokens=3000
            )
            return json.loads(_extract_json(raw))
        except Exception as e:
            return {"error": str(e)}


def _extract_json(text: str) -> str:
    """Strip markdown code fences from an AI JSON response."""
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        return text[start:end].strip()
    if "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        return text[start:end].strip()
    return text.strip()
