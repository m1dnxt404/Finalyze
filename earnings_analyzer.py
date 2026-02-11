"""
AI-Powered Earnings Report Analyzer
Analyzes company earnings reports to extract key metrics, sentiment, and insights
"""

import os
import json
from anthropic import Anthropic
from typing import Dict, List, Optional
from datetime import datetime

class EarningsReportAnalyzer:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the earnings report analyzer
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env variable)
        """
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"
        
    def create_analysis_prompt(self, earnings_text: str, company_name: str = None) -> str:
        """
        Create a structured prompt for earnings analysis
        
        Args:
            earnings_text: The earnings report text
            company_name: Optional company name for context
        """
        company_context = f" for {company_name}" if company_name else ""
        
        prompt = f"""Analyze this earnings report{company_context} and extract the following information in a structured JSON format:

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

        return prompt
    
    def analyze_earnings(self, earnings_text: str, company_name: str = None) -> Dict:
        """
        Analyze an earnings report and return structured results
        
        Args:
            earnings_text: The earnings report text to analyze
            company_name: Optional company name
            
        Returns:
            Dictionary containing structured analysis
        """
        prompt = self.create_analysis_prompt(earnings_text, company_name)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.3,  # Lower temperature for more consistent extraction
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract the text response
            analysis_text = response.content[0].text
            
            # Try to parse JSON from the response
            # Claude might wrap it in markdown code blocks
            if "```json" in analysis_text:
                json_start = analysis_text.find("```json") + 7
                json_end = analysis_text.find("```", json_start)
                analysis_text = analysis_text[json_start:json_end].strip()
            elif "```" in analysis_text:
                json_start = analysis_text.find("```") + 3
                json_end = analysis_text.find("```", json_start)
                analysis_text = analysis_text[json_start:json_end].strip()
            
            analysis_data = json.loads(analysis_text)
            
            # Add metadata
            analysis_data["metadata"] = {
                "analyzed_at": datetime.now().isoformat(),
                "model_used": self.model,
                "token_usage": {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens
                }
            }
            
            return analysis_data
            
        except json.JSONDecodeError as e:
            # If JSON parsing fails, return raw analysis
            return {
                "error": "Failed to parse JSON response",
                "raw_analysis": analysis_text,
                "exception": str(e)
            }
        except Exception as e:
            return {
                "error": "Analysis failed",
                "exception": str(e)
            }
    
    def compare_earnings(self, current_report: str, previous_report: str, 
                        company_name: str = None) -> Dict:
        """
        Compare two earnings reports to identify trends
        
        Args:
            current_report: Most recent earnings report
            previous_report: Previous period earnings report
            company_name: Optional company name
            
        Returns:
            Dictionary containing comparison analysis
        """
        prompt = f"""Compare these two earnings reports{' for ' + company_name if company_name else ''} and identify:

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

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            analysis_text = response.content[0].text
            
            # Clean JSON formatting
            if "```json" in analysis_text:
                json_start = analysis_text.find("```json") + 7
                json_end = analysis_text.find("```", json_start)
                analysis_text = analysis_text[json_start:json_end].strip()
            
            return json.loads(analysis_text)
            
        except Exception as e:
            return {"error": str(e)}
    
    def generate_investor_brief(self, analysis: Dict) -> str:
        """
        Generate a concise investor brief from analysis results
        
        Args:
            analysis: Analysis dictionary from analyze_earnings()
            
        Returns:
            Formatted investor brief as string
        """
        if "error" in analysis:
            return f"Error generating brief: {analysis['error']}"
        
        brief = f"""
{'='*70}
INVESTOR BRIEF - {analysis.get('company_info', {}).get('name', 'N/A')}
{'='*70}

Period: {analysis.get('company_info', {}).get('reporting_period', 'N/A')}
Date: {analysis.get('company_info', {}).get('report_date', 'N/A')}

PERFORMANCE SNAPSHOT
{'-'*70}
Revenue: {analysis.get('financial_metrics', {}).get('revenue', {}).get('current', 'N/A')}
YoY Growth: {analysis.get('financial_metrics', {}).get('revenue', {}).get('yoy_growth', 'N/A')}
EPS: {analysis.get('financial_metrics', {}).get('earnings', {}).get('eps_reported', 'N/A')} 
     ({analysis.get('financial_metrics', {}).get('earnings', {}).get('beat_miss', 'N/A')} expectations)

SENTIMENT
{'-'*70}
Overall: {analysis.get('sentiment_analysis', {}).get('overall_tone', 'N/A')} 
         (Score: {analysis.get('sentiment_analysis', {}).get('sentiment_score', 'N/A')}/100)
Outlook: {analysis.get('sentiment_analysis', {}).get('forward_outlook', 'N/A')}

KEY HIGHLIGHTS
{'-'*70}
"""
        for i, highlight in enumerate(analysis.get('key_highlights', [])[:5], 1):
            brief += f"{i}. {highlight}\n"
        
        brief += f"\nCONCERNS & RISKS\n{'-'*70}\n"
        for i, concern in enumerate(analysis.get('concerns_risks', [])[:5], 1):
            brief += f"{i}. {concern}\n"
        
        if analysis.get('red_flags'):
            brief += f"\n⚠️  RED FLAGS\n{'-'*70}\n"
            for flag in analysis['red_flags']:
                brief += f"• {flag}\n"
        
        brief += f"\n{'='*70}\n"
        
        return brief


def main():
    """
    Example usage of the EarningsReportAnalyzer
    """
    # Sample earnings report excerpt (you would use real data)
    sample_report = """
    Tesla, Inc. Q4 2024 Earnings Report
    
    Tesla today announced financial results for the fourth quarter ended December 31, 2024.
    
    Revenue for the quarter was $25.2 billion, up 8% year-over-year from $23.4 billion in Q4 2023.
    Net income was $2.1 billion, resulting in earnings per share of $0.68, beating analyst expectations 
    of $0.64 per share.
    
    Automotive revenue was $19.8 billion, with 484,000 vehicles delivered in the quarter. Energy 
    generation and storage revenue reached $3.9 billion, up 54% year-over-year, driven by strong 
    demand for Powerwall and Megapack products.
    
    Operating margin was 8.2%, down from 8.8% in the previous quarter due to pricing pressures 
    and increased competition in the EV market.
    
    CEO Elon Musk stated: "We're seeing incredible momentum in energy storage, which is becoming 
    a major profit driver for the company. While automotive margins face near-term pressure, we're 
    confident in our roadmap with the upcoming launch of our next-generation vehicle platform."
    
    For Q1 2025, Tesla expects vehicle deliveries to be in line with Q4 2024 levels, with full-year 
    2025 growth expected to be in the low double digits percentage-wise.
    
    The company highlighted challenges including supply chain constraints and increased competition,
    but expressed confidence in long-term growth driven by energy storage and autonomous driving 
    technology development.
    """
    
    # Initialize analyzer
    analyzer = EarningsReportAnalyzer()
    
    print("Analyzing earnings report...\n")
    
    # Analyze the report
    analysis = analyzer.analyze_earnings(sample_report, "Tesla, Inc.")
    
    # Save detailed analysis to JSON
    with open('/home/claude/earnings_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)
    print("✓ Detailed analysis saved to earnings_analysis.json\n")
    
    # Generate and print investor brief
    brief = analyzer.generate_investor_brief(analysis)
    print(brief)
    
    # Save brief to text file
    with open('/home/claude/investor_brief.txt', 'w') as f:
        f.write(brief)
    print("✓ Investor brief saved to investor_brief.txt")


if __name__ == "__main__":
    main()
