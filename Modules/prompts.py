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


def build_context_aware_prompt(earnings_text: str, company_name: str = None,
                               past_context: list = None) -> str:
    """Build an analysis prompt enriched with historical context from past reports."""
    if not past_context:
        return build_analysis_prompt(earnings_text, company_name)

    company_context = f" for {company_name}" if company_name else ""

    context_section = "HISTORICAL CONTEXT FROM PREVIOUS REPORTS:\n"
    for i, ctx in enumerate(past_context, 1):
        quarter = ctx.get("quarter", "Unknown period")
        summary = ctx.get("summary", "")
        context_section += f"\n--- Report {i} ({quarter}) ---\n{summary}\n"

    return f"""Analyze this earnings report{company_context} and extract the following information in a structured JSON format.

You have access to previous reports for this company below. Use them to identify trends, compare performance across quarters, and note any acceleration or deceleration in key metrics. Reference specific changes from prior periods where relevant (e.g., "Revenue grew 12%, accelerating from 8% in the prior quarter").

{context_section}

CURRENT EARNINGS REPORT:
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
  "historical_comparison": {{
    "trends": "Key trends observed across available quarters",
    "improving_areas": ["Metrics or areas showing improvement"],
    "declining_areas": ["Metrics or areas showing decline"]
  }},
  "red_flags": [
    "Any concerning patterns or statements"
  ],
  "analyst_summary": "2-3 paragraph executive summary that references trends from prior quarters where applicable"
}}

Be thorough but concise. If information is not available in the report, use null or "Not disclosed". Focus on actionable insights and cross-quarter trends."""


def build_query_prompt(query: str, relevant_reports: list) -> str:
    """Build a prompt for answering questions across stored reports."""
    context = ""
    for i, report in enumerate(relevant_reports, 1):
        company = report.get("company", "Unknown")
        quarter = report.get("quarter", "")
        summary = report.get("summary", "")
        context += f"\n--- Report {i}: {company} ({quarter}) ---\n{summary}\n"

    return f"""You are a financial analyst assistant. Answer the following question using ONLY the earnings report data provided below. If the data doesn't contain enough information to answer fully, say so.

AVAILABLE EARNINGS REPORT DATA:
{context}

QUESTION: {query}

Provide your answer in the following JSON format:
{{
  "answer": "Your detailed answer to the question",
  "confidence": "high/medium/low based on how well the data supports the answer",
  "sources": [
    {{
      "company": "Company name",
      "quarter": "Reporting period",
      "relevant_detail": "The specific data point used"
    }}
  ],
  "limitations": "Any caveats or missing data that could affect the answer"
}}"""


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
