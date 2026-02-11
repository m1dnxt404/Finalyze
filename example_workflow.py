"""
Complete Example Workflow - Earnings Report Analyzer
Demonstrates all major features with real-world usage patterns
"""

import json
import os
from datetime import datetime
from Modules import EarningsReportAnalyzer, generate_investor_brief

def main():
    print("="*80)
    print("AI-POWERED EARNINGS REPORT ANALYZER - COMPLETE WORKFLOW")
    print("="*80)
    
    # Create outputs directory next to this script
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    os.makedirs(output_dir, exist_ok=True)

    # Initialize analyzer
    analyzer = EarningsReportAnalyzer()
    
    # =============================================================================
    # EXAMPLE 1: Basic Single Report Analysis
    # =============================================================================
    print("\n📊 EXAMPLE 1: Analyzing Single Earnings Report")
    print("-"*80)
    
    nvidia_q4 = """
    NVIDIA Corporation Q4 FY2024 Financial Results
    
    SANTA CLARA, Calif., February 21, 2024 - NVIDIA today reported record revenue 
    for the fourth quarter ended January 28, 2024.
    
    Q4 Financial Summary:
    - Revenue: $22.1 billion, up 265% year-over-year, up 22% sequentially
    - GAAP earnings per diluted share: $4.93, up 765% year-over-year
    - Non-GAAP earnings per diluted share: $5.16, up 486% year-over-year, beat 
      analyst expectations of $4.64
    
    Data Center revenue reached $18.4 billion, up 409% from a year ago and up 27% 
    from the previous quarter. The growth was driven by accelerating demand for AI 
    infrastructure, with all major cloud service providers and enterprise customers 
    expanding their AI computing capabilities.
    
    Gaming revenue was $2.9 billion, up 56% from a year ago. Professional 
    Visualization revenue was $463 million, up 105% year-over-year.
    
    Gross margin was 76.0%, up from 56.1% a year ago, reflecting strong pricing 
    power and favorable product mix shift toward high-margin data center products.
    
    "The era of AI is in full steam," said Jensen Huang, founder and CEO of NVIDIA. 
    "Demand is surging worldwide across companies, industries, and nations. Our 
    data center platform is powered by increasingly diverse drivers — from 
    accelerated computing and generative AI to recommender systems, and advanced 
    large language models."
    
    For the first quarter of fiscal 2025, NVIDIA expects revenue of $24.0 billion, 
    plus or minus 2%. GAAP and non-GAAP gross margins are expected to be 76.3% and 
    76.5%, respectively.
    
    The company noted some supply chain constraints for the latest Hopper 
    architecture GPUs but expressed confidence in meeting strong demand through 
    the remainder of the fiscal year.
    """
    
    print("Analyzing NVIDIA Q4 FY2024...")
    nvidia_analysis = analyzer.analyze_earnings(nvidia_q4, "NVIDIA Corporation")
    
    # Print key metrics
    print("\n✓ Analysis Complete!")
    print(f"\nCompany: {nvidia_analysis.get('company_info', {}).get('name', 'N/A')}")
    print(f"Period: {nvidia_analysis.get('company_info', {}).get('reporting_period', 'N/A')}")
    
    sentiment = nvidia_analysis.get('sentiment_analysis', {})
    print(f"\nSentiment Score: {sentiment.get('sentiment_score', 0)}/100")
    print(f"Overall Tone: {sentiment.get('overall_tone', 'N/A')}")
    print(f"Management Confidence: {sentiment.get('management_confidence', 'N/A')}")
    
    # Save detailed analysis
    with open(os.path.join(output_dir, 'nvidia_analysis.json'), 'w') as f:
        json.dump(nvidia_analysis, f, indent=2)
    print("\n💾 Detailed analysis saved to: nvidia_analysis.json")
    
    # =============================================================================
    # EXAMPLE 2: Generate Investor Brief
    # =============================================================================
    print("\n\n📝 EXAMPLE 2: Generating Investor Brief")
    print("-"*80)
    
    brief = generate_investor_brief(nvidia_analysis)
    print(brief)
    
    with open(os.path.join(output_dir, 'nvidia_brief.txt'), 'w') as f:
        f.write(brief)
    print("💾 Brief saved to: nvidia_brief.txt")
    
    # =============================================================================
    # EXAMPLE 3: Comparing Two Reports
    # =============================================================================
    print("\n\n📈 EXAMPLE 3: Comparing Quarterly Reports")
    print("-"*80)
    
    nvidia_q3 = """
    NVIDIA Corporation Q3 FY2024 Financial Results
    
    Q3 Financial Summary:
    - Revenue: $18.1 billion, up 206% year-over-year
    - GAAP earnings per diluted share: $3.71
    - Non-GAAP earnings per diluted share: $4.02
    
    Data Center revenue was $14.5 billion, up 279% from a year ago.
    Gaming revenue was $2.9 billion, up 81% from a year ago.
    Gross margin was 75.0%.
    
    CEO Jensen Huang noted: "The age of AI is here, with strong demand for our 
    data center platforms."
    
    For Q4, the company guided revenue of $20.0 billion, plus or minus 2%.
    """
    
    print("Comparing Q4 vs Q3 performance...")
    comparison = analyzer.compare_earnings(nvidia_q4, nvidia_q3, "NVIDIA Corporation")
    
    print("\n✓ Comparison Complete!")
    print("\nTrend Analysis:")
    print(f"  Revenue: {comparison.get('trend_analysis', {}).get('revenue_trend', 'N/A')}")
    print(f"  Profitability: {comparison.get('trend_analysis', {}).get('profitability_trend', 'N/A')}")
    print(f"  Margins: {comparison.get('trend_analysis', {}).get('margin_trend', 'N/A')}")
    
    print("\nKey Changes:")
    for change in comparison.get('key_changes', [])[:3]:
        print(f"  • {change}")
    
    with open(os.path.join(output_dir, 'nvidia_comparison.json'), 'w') as f:
        json.dump(comparison, f, indent=2)
    print("\n💾 Comparison saved to: nvidia_comparison.json")
    
    # =============================================================================
    # EXAMPLE 4: Batch Analysis of Multiple Companies
    # =============================================================================
    print("\n\n📦 EXAMPLE 4: Batch Analysis - Portfolio Review")
    print("-"*80)
    
    portfolio = {
        'Tesla': """
        Tesla Q4 2024: Revenue $25.2B (up 8% YoY). EPS $0.68 (beat $0.64).
        Automotive revenue $19.8B. Energy storage $3.9B (up 54%). 
        Operating margin 8.2% (down from 8.8%). CEO optimistic on energy business.
        """,
        
        'Apple': """
        Apple Q1 2025: Revenue $124.3B (up 6% YoY). EPS $2.45 (beat $2.38).
        iPhone revenue $72.1B. Services $24.5B (all-time high). 
        Gross margin 44.1%. Strong performance in Services segment.
        """,
        
        'Microsoft': """
        Microsoft Q2 FY2025: Revenue $62.0B (up 16% YoY). EPS $2.93 (up 10%).
        Intelligent Cloud $25.5B (up 20%). Azure up 30%. 
        Operating margin 43.5%. CEO confident in AI-driven growth.
        """
    }
    
    print("Analyzing portfolio companies...\n")
    
    portfolio_results = {}
    for company, earnings_text in portfolio.items():
        print(f"  Analyzing {company}...", end=" ")
        result = analyzer.analyze_earnings(earnings_text, company)
        portfolio_results[company] = {
            'sentiment_score': result.get('sentiment_analysis', {}).get('sentiment_score', 0),
            'tone': result.get('sentiment_analysis', {}).get('overall_tone', 'N/A'),
            'eps_result': result.get('financial_metrics', {}).get('earnings', {}).get('beat_miss', 'N/A')
        }
        print("✓")
    
    print("\n" + "="*80)
    print("PORTFOLIO SUMMARY")
    print("="*80)
    print(f"{'Company':<15} {'Sentiment':<12} {'Tone':<12} {'EPS Result':<12}")
    print("-"*80)
    
    for company, data in portfolio_results.items():
        sentiment_emoji = "🟢" if data['sentiment_score'] > 70 else "🟡" if data['sentiment_score'] > 50 else "🔴"
        print(f"{company:<15} {sentiment_emoji} {data['sentiment_score']:>3}/100    {data['tone']:<12} {data['eps_result']:<12}")
    
    # Save portfolio summary
    with open(os.path.join(output_dir, 'portfolio_summary.json'), 'w') as f:
        json.dump(portfolio_results, f, indent=2)
    print("\n💾 Portfolio summary saved to: portfolio_summary.json")
    
    # =============================================================================
    # EXAMPLE 5: Alert Generation
    # =============================================================================
    print("\n\n🔔 EXAMPLE 5: Generating Investment Alerts")
    print("-"*80)
    
    # Define alert thresholds
    print("\nSetting alert thresholds:")
    print("  • EPS beat > 5%")
    print("  • Sentiment score < 60")
    print("  • Any red flags detected")
    
    alerts = []
    
    # Check NVIDIA results
    sentiment_score = nvidia_analysis.get('sentiment_analysis', {}).get('sentiment_score', 0)
    red_flags = nvidia_analysis.get('red_flags', [])
    
    if sentiment_score > 80:
        alerts.append({
            'company': 'NVIDIA',
            'type': 'HIGH_SENTIMENT',
            'message': f'Exceptionally positive sentiment: {sentiment_score}/100',
            'severity': 'info'
        })
    
    if red_flags:
        alerts.append({
            'company': 'NVIDIA',
            'type': 'RED_FLAGS',
            'message': f'{len(red_flags)} red flag(s) detected',
            'severity': 'warning',
            'details': red_flags
        })
    
    # Check EPS beat
    eps_info = nvidia_analysis.get('financial_metrics', {}).get('earnings', {})
    if eps_info.get('beat_miss') == 'beat':
        alerts.append({
            'company': 'NVIDIA',
            'type': 'STRONG_BEAT',
            'message': f"EPS beat expectations: {eps_info.get('eps_reported')} vs {eps_info.get('eps_expected')}",
            'severity': 'high'
        })
    
    print("\n🔔 Active Alerts:")
    for alert in alerts:
        emoji = "⚠️" if alert['severity'] == 'warning' else "🔥" if alert['severity'] == 'high' else "ℹ️"
        print(f"{emoji}  [{alert['company']}] {alert['message']}")
    
    # =============================================================================
    # EXAMPLE 6: Exporting for Further Analysis
    # =============================================================================
    print("\n\n💾 EXAMPLE 6: Exporting Data for Spreadsheet Analysis")
    print("-"*80)
    
    # Create CSV-friendly export
    csv_data = []
    for company, data in portfolio_results.items():
        csv_data.append({
            'Company': company,
            'Date': datetime.now().strftime('%Y-%m-%d'),
            'Sentiment_Score': data['sentiment_score'],
            'Tone': data['tone'],
            'EPS_Result': data['eps_result']
        })
    
    # Save as JSON (can be imported to Excel/Google Sheets)
    with open(os.path.join(output_dir, 'portfolio_export.json'), 'w') as f:
        json.dump(csv_data, f, indent=2)
    
    print("✓ Data exported to: portfolio_export.json")
    print("  (Can be imported to Excel/Google Sheets)")
    
    # =============================================================================
    # Summary
    # =============================================================================
    print("\n\n" + "="*80)
    print("WORKFLOW COMPLETE - FILES CREATED")
    print("="*80)
    print("""
    ✅ nvidia_analysis.json       - Detailed NVIDIA analysis
    ✅ nvidia_brief.txt           - Investor brief for NVIDIA
    ✅ nvidia_comparison.json     - Q4 vs Q3 comparison
    ✅ portfolio_summary.json     - Multi-company summary
    ✅ portfolio_export.json      - CSV-ready export data
    
    📚 Next Steps:
    1. Review the detailed analysis files
    2. Set up automated analysis for your watchlist
    3. Create custom alert thresholds
    4. Build visualizations with the exported data
    5. Integrate with your investment workflow
    """)
    
    print("\n" + "="*80)
    print("💡 TIP: Run 'python web_dashboard.py' for a browser-based interface!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
