"""
Finalyze core modules — config, providers, prompts, analyzer, formatter.
"""

from .config import PROVIDERS, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE
from .providers import create_client, call_provider
from .prompts import build_analysis_prompt, build_comparison_prompt
from .analyzer import EarningsReportAnalyzer
from .formatter import generate_investor_brief
from .store import save_report, get_history, get_report, query_reports, get_company_context
