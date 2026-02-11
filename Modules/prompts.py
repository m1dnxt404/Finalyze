"""
Prompt templates for earnings report analysis.
"""


def build_analysis_prompt(earnings_text: str, company_name: str = None) -> str:
    """Build the structured JSON-extraction prompt for a single earnings report."""
    company_context = f" for {company_name}" if company_name else ""

    return f"""Analyze this earnings report{company_context} and extract the following information in a structured JSON format:

EARNINGS REPORT:
{earnings_text}

Please provide a comprehensive analysis in the following JSON structure:

{{
  "company_info": {{
    "name": "Company name",
    "ticker": "Stock ticker symbol",
    "reporting_period": "Quarter/Year (e.g., Q4 2024)",
    "report_date": "Date of report"
  }},
  "financial_metrics": {{
    "revenue": {{
      "current": "Revenue for this period",
      "previous": "Revenue for comparison period",
      "yoy_growth": "Year-over-year growth percentage",
      "currency": "USD, EUR, etc."
    }},
    "earnings": {{
      "eps_reported": "Reported EPS",
      "eps_expected": "Expected/Consensus EPS",
      "beat_miss": "beat/miss/inline",
      "net_income": "Net income value"
    }},
    "margins": {{
      "gross_margin": "Gross margin percentage",
      "operating_margin": "Operating margin percentage",
      "net_margin": "Net margin percentage"
    }},
    "guidance": {{
      "provided": true/false,
      "next_quarter_revenue": "Guidance if provided",
      "next_quarter_eps": "EPS guidance if provided",
      "full_year": "Full year guidance if provided"
    }}
  }},
  "key_highlights": [
    "Most important positive developments",
    "Major achievements or milestones",
    "Strategic initiatives mentioned"
  ],
  "concerns_risks": [
    "Challenges mentioned",
    "Risk factors highlighted",
    "Headwinds or obstacles"
  ],
  "sentiment_analysis": {{
    "overall_tone": "bullish/neutral/bearish",
    "management_confidence": "high/medium/low",
    "forward_outlook": "optimistic/cautious/pessimistic",
    "sentiment_score": "0-100 where 100 is most positive"
  }},
  "business_segments": [
    {{
      "name": "Segment name",
      "performance": "Description of performance",
      "revenue_contribution": "Percentage or amount"
    }}
  ],
  "notable_quotes": [
    {{
      "quote": "Important statement from management",
      "speaker": "CEO/CFO/etc.",
      "context": "What this relates to"
    }}
  ],
  "market_implications": {{
    "likely_market_reaction": "Expected stock movement reasoning",
    "key_takeaways": ["Summary points for investors"],
    "comparison_to_peers": "How this compares to industry"
  }},
  "red_flags": [
    "Any concerning patterns or statements"
  ],
  "analyst_summary": "2-3 paragraph executive summary of the earnings report"
}}

Be thorough but concise. If information is not available in the report, use null or "Not disclosed". Focus on actionable insights."""


def build_comparison_prompt(current_report: str, previous_report: str,
                            company_name: str = None) -> str:
    """Build the prompt for comparing two earnings reports."""
    company_context = f" for {company_name}" if company_name else ""

    return f"""Compare these two earnings reports{company_context} and identify:

CURRENT REPORT:
{current_report}

PREVIOUS REPORT:
{previous_report}

Provide analysis in JSON format:
{{
  "trend_analysis": {{
    "revenue_trend": "improving/declining/stable",
    "profitability_trend": "improving/declining/stable",
    "margin_trend": "expanding/contracting/stable"
  }},
  "key_changes": [
    "Significant changes between periods"
  ],
  "momentum": {{
    "accelerating": ["Areas showing acceleration"],
    "decelerating": ["Areas showing deceleration"]
  }},
  "management_tone_shift": "More optimistic/pessimistic/consistent",
  "strategic_shifts": ["Any changes in strategy or focus"],
  "comparative_summary": "2 paragraph comparison summary"
}}"""
