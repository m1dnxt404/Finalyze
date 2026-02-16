# Finalyze - AI-Powered Earnings Report Analyzer

A Python tool that uses AI to analyze company earnings reports, extract key financial metrics, assess sentiment, and generate actionable investor insights. Built on LangChain for unified multi-provider support and Pydantic for type-safe structured output. Ships with a FastAPI web dashboard, ChromaDB-powered RAG, and persistent storage.

## Features

- **Multi-Provider AI Support**: Anthropic Claude, OpenAI GPT, Google Gemini, DeepSeek, and Ollama (local) — unified via LangChain
- **Structured Output**: Pydantic schemas for type-safe, validated analysis results
- **Web Dashboard**: FastAPI-powered browser UI with real-time analysis
- **Multiple Input Methods**: Paste text, upload files (PDF, DOCX, TXT), or import from Google Docs
- **Financial Extraction**: Revenue, EPS, margins, guidance, and segment breakdowns
- **Sentiment Analysis**: Overall tone, management confidence, forward outlook (scored 0-100)
- **Risk Assessment**: Red flags, concerns, and risk identification
- **Report Comparison**: Compare current vs previous quarters to spot trends
- **Investor Briefs**: Generate concise summaries for quick decision-making
- **RAG-Powered Query**: Ask natural-language questions across all stored reports
- **Context-Aware Analysis**: Auto-retrieves past reports for the same company to identify trends
- **Persistent Storage**: ChromaDB vector store — analysis history survives server restarts
- **Enhanced Analyzer**: Fetch reports from URLs, search SEC EDGAR filings by ticker
- **Alert System**: Custom threshold-based alerts for EPS beats, sentiment, red flags

## Project Structure

```text
Finalyze/
├── Modules/                  # Core package
│   ├── __init__.py           # Re-exports public API
│   ├── config.py             # Provider config & constants
│   ├── providers.py          # LangChain ChatModel factory (unified .invoke())
│   ├── prompts.py            # LangChain ChatPromptTemplate definitions
│   ├── schemas.py            # Pydantic models for structured output
│   ├── analyzer.py           # EarningsReportAnalyzer (LangChain chains)
│   ├── formatter.py          # Investor brief formatting
│   └── store.py              # ChromaDB vector store for persistent storage & retrieval
├── text_extractor.py         # LangChain document loaders (PDF, DOCX, TXT, Google Docs)
├── enhanced_analyzer.py      # URL fetching, SEC search, alerts
├── web_dashboard.py          # FastAPI web dashboard
├── example_workflow.py       # End-to-end demo script
├── requirements.txt
├── data/chromadb/            # Persistent vector database (auto-created)
└── templates/
    ├── dashboard.html
    ├── css/styles.css
    └── js/app.js
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys

Set at least one provider's API key as an environment variable:

**Linux/Mac:**

```bash
export ANTHROPIC_API_KEY='your-key-here'
# Optional additional providers:
export OPENAI_API_KEY='your-key-here'
export GEMINI_API_KEY='your-key-here'
export DEEPSEEK_API_KEY='your-key-here'
```

**Windows (PowerShell):**

```powershell
$env:ANTHROPIC_API_KEY='your-key-here'
```

**Windows (Command Prompt):**

```cmd
set ANTHROPIC_API_KEY=your-key-here
```

Or create a `.env` file in the project root:

```ini
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
```

## Usage

### Web Dashboard (Recommended)

```bash
python web_dashboard.py
```

Open <http://localhost:5000> in your browser. The dashboard supports:

- Pasting earnings text directly
- Uploading PDF, DOCX, or TXT files
- Importing from a public Google Docs URL
- Choosing your AI provider
- Viewing analysis history and exporting results

API docs are available at <http://localhost:5000/docs>.

### Python API - Basic Analysis

```python
from Modules import EarningsReportAnalyzer, generate_investor_brief

# Initialize with your preferred provider (default: anthropic)
analyzer = EarningsReportAnalyzer(provider="anthropic")

# Analyze an earnings report
analysis = analyzer.analyze_earnings(earnings_text, company_name="Apple Inc.")

# Generate a human-readable brief
print(generate_investor_brief(analysis))
```

### Switching Providers

```python
# Use OpenAI GPT
analyzer = EarningsReportAnalyzer(provider="openai")

# Use Google Gemini
analyzer = EarningsReportAnalyzer(provider="gemini")

# Use DeepSeek
analyzer = EarningsReportAnalyzer(provider="deepseek")

# Use Ollama (local, requires Ollama running at localhost:11434)
analyzer = EarningsReportAnalyzer(provider="ollama")
```

### Context-Aware Analysis

When you analyze a company that already has stored reports, Finalyze automatically retrieves past analyses and feeds them as context. The LLM will reference trends from prior quarters:

```python
# First analysis — no historical context
result1 = analyzer.analyze_earnings(q3_text, "NVIDIA")

# Second analysis — automatically uses Q3 as context
result2 = analyzer.analyze_earnings(q4_text, "NVIDIA")
# result2 will include cross-quarter trend references like
# "Revenue grew 12%, accelerating from 8% in the prior quarter"
```

### Query Stored Reports

Ask natural-language questions across all previously analyzed reports:

```python
from Modules import query_reports

# Find reports matching a question
results = query_reports("Which companies had strong revenue growth?", n=5)

# Filter by company
results = query_reports("What was the gross margin trend?", company="NVIDIA")
```

Via the API:

```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Which companies mentioned AI as a growth driver?", "provider": "anthropic"}'
```

### Compare Reports

```python
comparison = analyzer.compare_earnings(
    current_report=q4_text,
    previous_report=q3_text,
    company_name="NVIDIA"
)

print(comparison['trend_analysis'])
print(comparison['key_changes'])
```

### Enhanced Analyzer - URLs, PDFs, SEC Filings

```python
from enhanced_analyzer import EnhancedEarningsAnalyzer

ea = EnhancedEarningsAnalyzer(provider="anthropic")

# From a PDF file
result = ea.analyze_with_source("path/to/earnings.pdf", source_type="pdf", company_name="Apple")

# From a URL
result = ea.analyze_with_source("https://example.com/earnings.html", source_type="url")

# Search SEC EDGAR by ticker
result = ea.analyze_with_source("AAPL", source_type="ticker")

# Alert system
alerts = ea.create_alert_system(result, {
    "eps_beat_threshold": 5,
    "sentiment_min": 60,
})
```

### Run the Demo Workflow

```bash
python example_workflow.py
```

This runs a complete demo covering single-report analysis, investor briefs, quarterly comparisons, batch portfolio analysis, and alert generation. Results are saved to the `outputs/` directory.

## Output Structure

```json
{
  "company_info": {
    "name": "Tesla, Inc.",
    "ticker": "TSLA",
    "reporting_period": "Q4 2024",
    "report_date": "2025-01-15"
  },
  "financial_metrics": {
    "revenue": { "current": "$25.2B", "yoy_growth": "8%" },
    "earnings": { "eps_reported": "$0.68", "beat_miss": "beat" },
    "margins": { "gross_margin": "18.2%", "operating_margin": "8.2%" },
    "guidance": { "provided": true, "full_year": "Low double digit growth" }
  },
  "sentiment_analysis": {
    "overall_tone": "bullish",
    "management_confidence": "high",
    "sentiment_score": 75
  },
  "key_highlights": ["..."],
  "concerns_risks": ["..."],
  "red_flags": ["..."],
  "market_implications": { "likely_market_reaction": "..." },
  "metadata": {
    "provider": "anthropic",
    "model_used": "claude-sonnet-4-20250514",
    "token_usage": { "input": 2100, "output": 1500 }
  }
}
```

## REST API Endpoints

| Method | Endpoint           | Description                                              |
| ------ | ------------------ | -------------------------------------------------------- |
| GET    | `/`                | Web dashboard                                            |
| GET    | `/api/providers`   | List available AI providers                              |
| POST   | `/api/analyze`     | Analyze a report (text, file upload, or Google Docs)     |
| POST   | `/api/compare`     | Compare two earnings reports                             |
| POST   | `/api/query`       | Ask natural-language questions across all stored reports |
| GET    | `/api/history`     | Get analysis history (persistent via ChromaDB)           |
| GET    | `/api/export/{id}` | Export a specific analysis as JSON                       |

## Cost Estimation

Typical usage per earnings report:

| Provider         | Input Tokens | Output Tokens | Approx. Cost         |
| ---------------- | ------------ | ------------- | -------------------- |
| Anthropic Claude | 1,500-3,000  | 1,000-2,000   | $0.01-0.03           |
| OpenAI GPT-4o    | 1,500-3,000  | 1,000-2,000   | $0.01-0.04           |
| Google Gemini    | 1,500-3,000  | 1,000-2,000   | Free tier / low cost |
| DeepSeek         | 1,500-3,000  | 1,000-2,000   | < $0.01              |
| Ollama (local)   | N/A          | N/A           | Free                 |

## Troubleshooting

### API key not found

- Ensure the correct environment variable is set for your chosen provider
- Check your `.env` file if using one

### Structured output errors

- LangChain uses tool calling for structured output — ensure your provider/model supports it
- Ollama models need function-calling support (e.g., llama3.1, mistral)
- Very long reports (>100k characters) are automatically truncated to relevant sections

### Web dashboard won't start

- Make sure FastAPI and Uvicorn are installed: `pip install fastapi uvicorn`
- Check if port 5000 is already in use
- API docs at `/docs` can help debug endpoint issues

### PDF parsing not working

- Install pypdf: `pip install pypdf`
- Image-based PDFs won't extract text — use OCR tools first

## Best Practices

1. **Validate numbers**: Always cross-check extracted metrics with the source document
2. **Use for analysis, not advice**: This is an analysis tool, not financial advice
3. **Combine with judgment**: AI should augment, not replace, analyst expertise
4. **Review red flags**: Always check the `red_flags` and `concerns_risks` sections
5. **Compare quarters**: Trend analysis across periods reveals more than single-report analysis

## License

MIT License - feel free to modify and use for your projects.

## Disclaimer

This tool is for informational purposes only. It does not constitute financial advice. Always conduct your own research and consult with qualified financial advisors before making investment decisions.
