"""
Output formatting for earnings analysis results.
"""

from typing import Dict


def generate_investor_brief(analysis: Dict) -> str:
    """Format an analysis dict into a human-readable investor brief."""
    if "error" in analysis:
        return f"Error generating brief: {analysis['error']}"

    company = analysis.get("company_info", {})
    metrics = analysis.get("financial_metrics", {})
    sentiment = analysis.get("sentiment_analysis", {})

    brief = f"""
{'='*70}
INVESTOR BRIEF - {company.get('name', 'N/A')}
{'='*70}

Period: {company.get('reporting_period', 'N/A')}
Date: {company.get('report_date', 'N/A')}

PERFORMANCE SNAPSHOT
{'-'*70}
Revenue: {metrics.get('revenue', {}).get('current', 'N/A')}
YoY Growth: {metrics.get('revenue', {}).get('yoy_growth', 'N/A')}
EPS: {metrics.get('earnings', {}).get('eps_reported', 'N/A')} \
({metrics.get('earnings', {}).get('beat_miss', 'N/A')} expectations)

SENTIMENT
{'-'*70}
Overall: {sentiment.get('overall_tone', 'N/A')} \
(Score: {sentiment.get('sentiment_score', 'N/A')}/100)
Outlook: {sentiment.get('forward_outlook', 'N/A')}

KEY HIGHLIGHTS
{'-'*70}
"""
    for i, highlight in enumerate(analysis.get("key_highlights", [])[:5], 1):
        brief += f"{i}. {highlight}\n"

    brief += f"\nCONCERNS & RISKS\n{'-'*70}\n"
    for i, concern in enumerate(analysis.get("concerns_risks", [])[:5], 1):
        brief += f"{i}. {concern}\n"

    red_flags = analysis.get("red_flags")
    if red_flags:
        brief += f"\nRED FLAGS\n{'-'*70}\n"
        for flag in red_flags:
            brief += f"  {flag}\n"

    brief += f"\n{'='*70}\n"
    return brief
