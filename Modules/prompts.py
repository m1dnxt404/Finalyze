"""
LangChain prompt templates for earnings report analysis.
Since structured output is handled by Pydantic schemas via .with_structured_output(),
prompts focus on WHAT to analyze rather than HOW to format the output.
"""

from langchain_core.prompts import ChatPromptTemplate


analysis_prompt = ChatPromptTemplate.from_messages([
    ("human", """Analyze this earnings report{company_context} thoroughly and extract all key financial data.

EARNINGS REPORT:
{earnings_text}

Provide a comprehensive analysis covering:
- Company identification (name, ticker, reporting period, date)
- Financial metrics: revenue (current, previous, YoY growth, currency), earnings (EPS reported vs expected, beat/miss, net income), margins (gross, operating, net), and guidance (if provided)
- Key highlights and positive developments
- Concerns, risks, and headwinds
- Categorized risks — classify each identified risk into one of these categories:
  * Regulatory (government policy, legal, compliance, SEC)
  * Market (demand shifts, pricing pressure, currency exposure)
  * Competition (market share loss, new entrants, disruption)
  * Operational (supply chain, execution, workforce, technology)
  * Macro (recession, inflation, interest rates, geopolitical)
- Sentiment analysis: overall tone (bullish/neutral/bearish), management confidence (high/medium/low), forward outlook (optimistic/cautious/pessimistic), and a sentiment score from 0-100
- Business segment breakdown with performance and revenue contribution
- Notable management quotes with speaker and context
- Market implications: likely reaction, key takeaways, peer comparison
- Red flags or concerning patterns
- A 2-3 paragraph analyst summary

For each metric category (revenue, earnings, margins, sentiment), also provide a confidence score from 0-100 indicating how confident you are in the extracted data:
- 90-100: Data is explicitly and clearly stated in the report
- 70-89: Data is present but requires minor interpretation or calculation
- 40-69: Data is partially available, inferred, or ambiguous
- 0-39: Data is largely estimated or not directly supported by the report text

If information is not available in the report, use null. Focus on actionable insights.""")
])


context_aware_prompt = ChatPromptTemplate.from_messages([
    ("human", """Analyze this earnings report{company_context} thoroughly. You have access to previous reports for this company — use them to identify trends, compare performance across quarters, and note acceleration or deceleration in key metrics. Reference specific changes from prior periods where relevant (e.g., "Revenue grew 12%, accelerating from 8% in the prior quarter").

{context_section}

CURRENT EARNINGS REPORT:
{earnings_text}

Provide a comprehensive analysis covering:
- Company identification (name, ticker, reporting period, date)
- Financial metrics: revenue, earnings, margins, and guidance
- Key highlights and concerns/risks
- Categorized risks — classify each risk into: Regulatory, Market, Competition, Operational, or Macro
- Sentiment analysis with a score from 0-100
- Business segments, notable quotes, market implications
- Historical comparison: trends across quarters, improving areas, declining areas
- Red flags
- A 2-3 paragraph analyst summary that references trends from prior quarters

For each metric category (revenue, earnings, margins, sentiment), also provide a confidence score from 0-100 indicating how confident you are in the extracted data:
- 90-100: Data is explicitly and clearly stated in the report
- 70-89: Data is present but requires minor interpretation or calculation
- 40-69: Data is partially available, inferred, or ambiguous
- 0-39: Data is largely estimated or not directly supported by the report text

If information is not available, use null. Focus on actionable insights and cross-quarter trends.""")
])


comparison_prompt = ChatPromptTemplate.from_messages([
    ("human", """Compare these two earnings reports{company_context} and identify trends, changes, and shifts.

CURRENT REPORT:
{current_report}

PREVIOUS REPORT:
{previous_report}

Analyze: revenue/profitability/margin trends (improving/declining/stable), key changes between periods, momentum (accelerating vs decelerating areas), management tone shift, strategic shifts, and provide a 2-paragraph comparative summary.""")
])


query_prompt = ChatPromptTemplate.from_messages([
    ("human", """You are a financial analyst assistant. Answer the following question using ONLY the earnings report data provided below. If the data doesn't contain enough information to answer fully, say so.

AVAILABLE EARNINGS REPORT DATA:
{context}

QUESTION: {query}

Provide a detailed answer, indicate your confidence level (high/medium/low), cite specific sources (company, quarter, relevant detail), and note any limitations.""")
])


def format_context_section(past_context: list) -> str:
    """Format historical context reports into a prompt section."""
    if not past_context:
        return ""
    section = "HISTORICAL CONTEXT FROM PREVIOUS REPORTS:\n"
    for i, ctx in enumerate(past_context, 1):
        quarter = ctx.get("quarter", "Unknown period")
        summary = ctx.get("summary", "")
        section += f"\n--- Report {i} ({quarter}) ---\n{summary}\n"
    return section


def format_query_context(relevant_reports: list) -> str:
    """Format retrieved reports into a prompt section for queries."""
    context = ""
    for i, report in enumerate(relevant_reports, 1):
        company = report.get("company", "Unknown")
        quarter = report.get("quarter", "")
        summary = report.get("summary", "")
        context += f"\n--- Report {i}: {company} ({quarter}) ---\n{summary}\n"
    return context
