"""
Pydantic schemas for structured LLM output.
Used with LangChain's .with_structured_output() for type-safe parsing.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# ── Analysis schemas ─────────────────────────────────────────────

class CompanyInfo(BaseModel):
    name: Optional[str] = Field(None, description="Company name")
    ticker: Optional[str] = Field(None, description="Stock ticker symbol")
    reporting_period: Optional[str] = Field(None, description="Quarter/Year, e.g. Q4 2024")
    report_date: Optional[str] = Field(None, description="Date of report")


class Revenue(BaseModel):
    current: Optional[str] = Field(None, description="Revenue for this period")
    previous: Optional[str] = Field(None, description="Revenue for comparison period")
    yoy_growth: Optional[str] = Field(None, description="Year-over-year growth percentage")
    currency: Optional[str] = Field(None, description="Currency, e.g. USD, EUR")


class Earnings(BaseModel):
    eps_reported: Optional[str] = Field(None, description="Reported EPS")
    eps_expected: Optional[str] = Field(None, description="Expected/Consensus EPS")
    beat_miss: Optional[str] = Field(None, description="beat, miss, or inline")
    net_income: Optional[str] = Field(None, description="Net income value")


class Margins(BaseModel):
    gross_margin: Optional[str] = Field(None, description="Gross margin percentage")
    operating_margin: Optional[str] = Field(None, description="Operating margin percentage")
    net_margin: Optional[str] = Field(None, description="Net margin percentage")


class Guidance(BaseModel):
    provided: Optional[bool] = Field(None, description="Whether guidance was provided")
    next_quarter_revenue: Optional[str] = Field(None, description="Next quarter revenue guidance")
    next_quarter_eps: Optional[str] = Field(None, description="Next quarter EPS guidance")
    full_year: Optional[str] = Field(None, description="Full year guidance")


class FinancialMetrics(BaseModel):
    revenue: Optional[Revenue] = None
    earnings: Optional[Earnings] = None
    margins: Optional[Margins] = None
    guidance: Optional[Guidance] = None


class SentimentAnalysis(BaseModel):
    overall_tone: Optional[str] = Field(None, description="bullish, neutral, or bearish")
    management_confidence: Optional[str] = Field(None, description="high, medium, or low")
    forward_outlook: Optional[str] = Field(None, description="optimistic, cautious, or pessimistic")
    sentiment_score: Optional[int] = Field(None, description="0-100 where 100 is most positive")


class BusinessSegment(BaseModel):
    name: Optional[str] = Field(None, description="Segment name")
    performance: Optional[str] = Field(None, description="Description of performance")
    revenue_contribution: Optional[str] = Field(None, description="Percentage or amount")


class NotableQuote(BaseModel):
    quote: Optional[str] = Field(None, description="Important statement from management")
    speaker: Optional[str] = Field(None, description="CEO, CFO, etc.")
    context: Optional[str] = Field(None, description="What this relates to")


class MarketImplications(BaseModel):
    likely_market_reaction: Optional[str] = Field(None, description="Expected stock movement reasoning")
    key_takeaways: Optional[List[str]] = Field(None, description="Summary points for investors")
    comparison_to_peers: Optional[str] = Field(None, description="How this compares to industry")


class HistoricalComparison(BaseModel):
    trends: Optional[str] = Field(None, description="Key trends observed across available quarters")
    improving_areas: Optional[List[str]] = Field(None, description="Metrics or areas showing improvement")
    declining_areas: Optional[List[str]] = Field(None, description="Metrics or areas showing decline")


class EarningsAnalysis(BaseModel):
    """Complete structured earnings report analysis."""
    company_info: Optional[CompanyInfo] = None
    financial_metrics: Optional[FinancialMetrics] = None
    key_highlights: Optional[List[str]] = Field(None, description="Most important positive developments")
    concerns_risks: Optional[List[str]] = Field(None, description="Challenges and risk factors")
    sentiment_analysis: Optional[SentimentAnalysis] = None
    business_segments: Optional[List[BusinessSegment]] = None
    notable_quotes: Optional[List[NotableQuote]] = None
    market_implications: Optional[MarketImplications] = None
    historical_comparison: Optional[HistoricalComparison] = None
    red_flags: Optional[List[str]] = Field(None, description="Concerning patterns or statements")
    analyst_summary: Optional[str] = Field(None, description="2-3 paragraph executive summary")


# ── Comparison schemas ───────────────────────────────────────────

class TrendAnalysis(BaseModel):
    revenue_trend: Optional[str] = Field(None, description="improving, declining, or stable")
    profitability_trend: Optional[str] = Field(None, description="improving, declining, or stable")
    margin_trend: Optional[str] = Field(None, description="expanding, contracting, or stable")


class Momentum(BaseModel):
    accelerating: Optional[List[str]] = Field(None, description="Areas showing acceleration")
    decelerating: Optional[List[str]] = Field(None, description="Areas showing deceleration")


class EarningsComparison(BaseModel):
    """Structured comparison of two earnings reports."""
    trend_analysis: Optional[TrendAnalysis] = None
    key_changes: Optional[List[str]] = Field(None, description="Significant changes between periods")
    momentum: Optional[Momentum] = None
    management_tone_shift: Optional[str] = Field(None, description="More optimistic, pessimistic, or consistent")
    strategic_shifts: Optional[List[str]] = Field(None, description="Changes in strategy or focus")
    comparative_summary: Optional[str] = Field(None, description="2 paragraph comparison summary")


# ── Query schemas ────────────────────────────────────────────────

class QuerySource(BaseModel):
    company: Optional[str] = Field(None, description="Company name")
    quarter: Optional[str] = Field(None, description="Reporting period")
    relevant_detail: Optional[str] = Field(None, description="The specific data point used")


class QueryResponse(BaseModel):
    """Structured response to a cross-report query."""
    answer: Optional[str] = Field(None, description="Detailed answer to the question")
    confidence: Optional[str] = Field(None, description="high, medium, or low")
    sources: Optional[List[QuerySource]] = None
    limitations: Optional[str] = Field(None, description="Caveats or missing data")
