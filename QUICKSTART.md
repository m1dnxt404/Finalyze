# 🚀 Quick Start Guide - Earnings Report Analyzer

## What You've Got

A complete AI-powered earnings report analysis system with:

- ✅ Core analyzer with sentiment analysis
- ✅ Enhanced version with PDF parsing and web scraping
- ✅ Web dashboard with beautiful UI
- ✅ Alert system for key metrics
- ✅ Comparison tools for trend analysis
- ✅ Persistent storage via ChromaDB (survives restarts)
- ✅ Context-aware analysis using past reports
- ✅ RAG-powered cross-report querying

## Setup (5 minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Your API Key

Get your Anthropic API key from: **<https://console.anthropic.com/>**

**Option A - Environment Variable:**

```bash
export ANTHROPIC_API_KEY='sk-ant-...'
```

**Option B - .env File:**

Create a file named `.env`:

```text
ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Launch the Web Dashboard

```bash
python web_dashboard.py
```

Open **<http://localhost:5000>** in your browser. Analyze a report — it will be automatically saved to ChromaDB and available across restarts.

## Usage Options

### Option 1: Command Line (Simplest)

**Analyze a single report:**

```python
from Modules import EarningsReportAnalyzer, generate_investor_brief

analyzer = EarningsReportAnalyzer()

# Your earnings text
earnings_text = """
[Paste earnings report here]
"""

# Analyze
result = analyzer.analyze_earnings(earnings_text, "Company Name")

# Print brief
print(generate_investor_brief(result))
```

Save this as `my_analysis.py` and run: `python my_analysis.py`

### Option 2: Web Dashboard (Most User-Friendly)

```bash
python web_dashboard.py
```

Then open your browser to: **<http://localhost:5000>**

You'll get a beautiful interface where you can:

- Paste earnings text
- Get instant analysis
- View persistent history (survives restarts)
- See visual metrics
- Query across all stored reports

### Option 3: Enhanced Analyzer (Most Powerful)

For PDF files, URLs, or SEC filings:

```python
from enhanced_analyzer import EnhancedEarningsAnalyzer

analyzer = EnhancedEarningsAnalyzer()

# From PDF file
result = analyzer.analyze_with_source(
    "path/to/earnings.pdf", 
    source_type="pdf",
    company_name="Apple"
)

# From URL
result = analyzer.analyze_with_source(
    "https://example.com/earnings-release.html",
    source_type="url"
)

# Directly from SEC by ticker
result = analyzer.analyze_with_source(
    "AAPL",
    source_type="ticker"
)
```

## Real-World Example

Let's analyze Microsoft's latest earnings:

```python
from Modules import EarningsReportAnalyzer, generate_investor_brief
import json

analyzer = EarningsReportAnalyzer()

# Paste actual earnings text here
msft_earnings = """
Microsoft Cloud revenue up 22%
Revenue: $62.0 billion, up 16% YoY
Operating income: $27.0 billion, up 14%
Diluted EPS: $2.93, up 10%

Intelligent Cloud revenue: $25.5 billion, up 20%
Azure and other cloud services revenue up 30%
...
"""

# Analyze
analysis = analyzer.analyze_earnings(msft_earnings, "Microsoft")

# Save detailed results
with open('msft_q4_analysis.json', 'w') as f:
    json.dump(analysis, f, indent=2)

# Print investor brief
print(generate_investor_brief(analysis))

# Check sentiment
sentiment = analysis['sentiment_analysis']['sentiment_score']
if sentiment > 75:
    print("🟢 Strong positive sentiment")
elif sentiment > 50:
    print("🟡 Moderate positive sentiment")
else:
    print("🔴 Negative sentiment")
```

## Common Use Cases

### 1. Quick Daily Check

Monitor your portfolio companies:

```python
companies = {
    'AAPL': 'path/to/apple_earnings.txt',
    'MSFT': 'path/to/msft_earnings.txt',
    'GOOGL': 'path/to/google_earnings.txt'
}

for ticker, filepath in companies.items():
    with open(filepath, 'r') as f:
        text = f.read()
    
    result = analyzer.analyze_earnings(text, ticker)
    sentiment = result['sentiment_analysis']['sentiment_score']
    
    print(f"{ticker}: {sentiment}/100 - {result['financial_metrics']['earnings']['beat_miss']}")
```

### 2. Automated Alerts

Get notified of important changes:

```python
from enhanced_analyzer import EnhancedEarningsAnalyzer

analyzer = EnhancedEarningsAnalyzer()
analysis = analyzer.analyze_with_source(earnings_text, "text", "Tesla")

# Set your thresholds
thresholds = {
    'eps_beat_threshold': 5,  # Alert if beats by >5%
    'sentiment_min': 60        # Alert if sentiment <60
}

alerts = analyzer.create_alert_system(analysis, thresholds)

for alert in alerts:
    if alert['severity'] in ['critical', 'high']:
        print(f"⚠️  {alert['message']}")
        # Send email, Slack notification, etc.
```

### 3. Trend Analysis

Compare quarters:

```python
# Load Q3 and Q4 reports
with open('q3_2024.txt') as f:
    q3 = f.read()
with open('q4_2024.txt') as f:
    q4 = f.read()

# Compare
comparison = analyzer.compare_earnings(q4, q3, "Apple")

print("Revenue trend:", comparison['trend_analysis']['revenue_trend'])
print("Key changes:", comparison['key_changes'])
```

### 4. Query Across Reports (RAG)

Once you've analyzed several reports, ask questions across all of them:

```python
from Modules import query_reports

# Semantic search across all stored reports
results = query_reports("Which companies had the strongest EPS beats?", n=5)

for r in results:
    print(f"{r['company']} ({r['quarter']}): relevance {r['relevance']}")
```

Via the REST API:

```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What were the key risks mentioned across all reports?", "provider": "anthropic"}'
```

The query endpoint retrieves relevant stored reports from ChromaDB and sends them as context to the LLM, which synthesizes an answer with source references.

## Tips for Best Results

1. **Clean Your Input**: Remove headers, footers, page numbers from PDFs
2. **Include Context**: Company name helps the AI understand industry-specific terms
3. **Check Red Flags**: Always review the `red_flags` section carefully
4. **Validate Numbers**: Cross-check extracted metrics with the original
5. **Use Comparisons**: Quarterly comparisons reveal important trends

## Troubleshooting

### "API key not found"

- Make sure ANTHROPIC_API_KEY is set in your environment
- Check `.env` file if using one

### "Analysis failed" or JSON parsing errors

- The earnings text might be too long (>100k characters)
- Try using just the financial highlights section
- Check if special characters are causing issues

### Web dashboard won't start

- Make sure FastAPI is installed: `pip install fastapi uvicorn`
- Check if port 5000 is already in use

### PDF parsing not working

- Install pypdf: `pip install pypdf`
- Some PDFs are image-based and won't extract text
- Consider using OCR tools first

## Cost Estimation

Approximate cost per single earnings report analysis (~2,000 input + ~1,500 output tokens):

| Provider                  | Model             | Per Report | 10 Reports/Day for a Month |
| ------------------------- | ----------------- | ---------- | -------------------------- |
| Anthropic Claude Sonnet 4 | claude-sonnet-4   | ~$0.02     | ~$6-10                     |
| OpenAI GPT-4o             | gpt-4o            | ~$0.02     | ~$6-10                     |
| Google Gemini 2.0 Flash   | gemini-2.0-flash  | Free tier  | Free-$2                    |
| DeepSeek                  | deepseek-chat     | < $0.01    | ~$1-3                      |
| Ollama (local)            | llama3.1          | Free       | Free                       |

Larger reports (full 10-Ks) and RAG queries with historical context will use more tokens and cost proportionally more. Context-aware analysis roughly doubles input tokens since past reports are included in the prompt.

## Next Steps

1. **Integrate with your workflow**: Add to your morning routine
2. **Set up automations**: Schedule analyses with cron jobs
3. **Query your history**: Use `/api/query` to ask questions across all stored reports
4. **Create custom alerts**: Email or Slack notifications
5. **Add visualizations**: Charts for sentiment trends over time

## Need Help?

- Check README.md for detailed documentation
- Review example code in earnings_analyzer.py
- Test with the sample data first
- Start simple, then add complexity

## File Overview

- `Modules/` - Core package (LangChain-based analyzer, providers, prompts, schemas, store)
- `Modules/schemas.py` - Pydantic models for structured LLM output
- `Modules/store.py` - ChromaDB vector store for persistent storage & RAG
- `enhanced_analyzer.py` - PDF, URL, SEC support
- `web_dashboard.py` - Browser-based UI with RAG query endpoint
- `requirements.txt` - All dependencies
- `README.md` - Full documentation
- `data/chromadb/` - Persistent vector database (auto-created on first analysis)

Happy analyzing! 📊
