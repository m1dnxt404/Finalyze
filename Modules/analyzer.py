"""
Core EarningsReportAnalyzer class.
Uses LangChain chains with structured output for type-safe parsing.
"""

from typing import Dict, Optional
from datetime import datetime

from .config import PROVIDERS
from .providers import create_model
from .prompts import (
    analysis_prompt, context_aware_prompt, comparison_prompt, query_prompt,
    format_context_section, format_query_context,
)
from .schemas import EarningsAnalysis, EarningsComparison, QueryResponse


def _invoke_structured(model, schema, messages):
    """
    Invoke a model with structured output, returning (parsed_dict, usage_dict).
    Uses include_raw=True to get both the parsed Pydantic object and token usage.
    """
    structured = model.with_structured_output(schema, include_raw=True)
    result = structured.invoke(messages)

    parsed = result["parsed"]
    data = parsed.model_dump() if parsed else {}

    raw_msg = result["raw"]
    usage = {}
    if hasattr(raw_msg, "usage_metadata") and raw_msg.usage_metadata:
        usage = {
            "input": raw_msg.usage_metadata.get("input_tokens", 0),
            "output": raw_msg.usage_metadata.get("output_tokens", 0),
        }

    return data, usage


class EarningsReportAnalyzer:
    def __init__(self, provider: str = "anthropic", api_key: Optional[str] = None):
        """
        Args:
            provider: AI provider to use ("anthropic", "openai", "gemini", "deepseek", "ollama")
            api_key: API key (defaults to provider-specific env variable)
        """
        if provider not in PROVIDERS:
            raise ValueError(
                f"Unknown provider '{provider}'. Choose from: {list(PROVIDERS.keys())}"
            )
        self.provider = provider
        self.model_name = PROVIDERS[provider]["default_model"]
        self.model = create_model(provider, api_key)

    def analyze_earnings(self, earnings_text: str, company_name: str = None) -> Dict:
        """Analyze an earnings report and return structured results."""
        try:
            messages = analysis_prompt.format_messages(
                earnings_text=earnings_text,
                company_context=f" for {company_name}" if company_name else "",
            )
            data, usage = _invoke_structured(self.model, EarningsAnalysis, messages)
            data["metadata"] = {
                "analyzed_at": datetime.now().isoformat(),
                "provider": self.provider,
                "model_used": self.model_name,
                "token_usage": usage,
            }
            return data

        except Exception as e:
            return {"error": "Analysis failed", "exception": str(e)}

    def analyze_with_context(self, earnings_text: str, company_name: str = None,
                             past_context: list = None) -> Dict:
        """Analyze with historical context from past reports."""
        try:
            context_section = format_context_section(past_context or [])
            messages = context_aware_prompt.format_messages(
                earnings_text=earnings_text,
                company_context=f" for {company_name}" if company_name else "",
                context_section=context_section,
            )
            data, usage = _invoke_structured(self.model, EarningsAnalysis, messages)
            data["metadata"] = {
                "analyzed_at": datetime.now().isoformat(),
                "provider": self.provider,
                "model_used": self.model_name,
                "token_usage": usage,
                "context_reports_used": len(past_context or []),
            }
            return data

        except Exception as e:
            return {"error": "Analysis failed", "exception": str(e)}

    def compare_earnings(self, current_report: str, previous_report: str,
                         company_name: str = None) -> Dict:
        """Compare two earnings reports to identify trends."""
        try:
            messages = comparison_prompt.format_messages(
                current_report=current_report,
                previous_report=previous_report,
                company_context=f" for {company_name}" if company_name else "",
            )
            data, _ = _invoke_structured(self.model, EarningsComparison, messages)
            return data

        except Exception as e:
            return {"error": str(e)}

    def query(self, user_query: str, relevant_reports: list) -> Dict:
        """Answer a natural-language question across stored reports."""
        try:
            context = format_query_context(relevant_reports)
            messages = query_prompt.format_messages(
                query=user_query,
                context=context,
            )
            data, _ = _invoke_structured(self.model, QueryResponse, messages)
            return data

        except Exception as e:
            return {"error": str(e)}
