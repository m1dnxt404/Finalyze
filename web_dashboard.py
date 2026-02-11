"""
Web Dashboard for Earnings Report Analyzer (FastAPI)
Run with: python web_dashboard.py
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import tempfile
import os
from datetime import datetime
from Modules import EarningsReportAnalyzer, PROVIDERS
from text_extractor import extract_from_uploaded_file, extract_from_google_docs_url

app = FastAPI(title="Finalyze")

# Serve static CSS and JS from templates/ subfolders
app.mount("/css", StaticFiles(directory="templates/css"), name="css")
app.mount("/js", StaticFiles(directory="templates/js"), name="js")

templates = Jinja2Templates(directory="templates")

# Store analysis history in memory (in production, use a database)
analysis_history = []


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse(request=request, name="dashboard.html")


@app.get("/api/providers")
async def get_providers():
    """Return available AI providers"""
    return {key: val["name"] for key, val in PROVIDERS.items()}


@app.post("/api/analyze")
async def analyze(request: Request):
    """API endpoint for analyzing earnings reports.

    Accepts three input modes:
    - multipart/form-data with a 'file' field (PDF, DOCX, TXT upload)
    - JSON with 'google_docs_url' (fetches text from a public Google Doc)
    - JSON with 'earnings_text' (direct text paste, existing flow)
    """
    try:
        content_type = request.headers.get("content-type", "")

        # --- Determine input mode and extract text ---
        if "multipart/form-data" in content_type:
            # File upload
            form = await request.form()
            uploaded = form.get("file")
            if not uploaded or not uploaded.filename:
                return JSONResponse({"error": "No file provided"}, status_code=400)
            company_name = form.get("company_name", "")
            provider = form.get("provider", "anthropic")
            try:
                data = await uploaded.read()
                earnings_text = extract_from_uploaded_file(data, uploaded.filename)
            except (ValueError, ImportError) as e:
                return JSONResponse({"error": str(e)}, status_code=400)
        else:
            body = await request.json()
            company_name = body.get("company_name", "")
            provider = body.get("provider", "anthropic")
            google_docs_url = body.get("google_docs_url", "")

            if google_docs_url:
                try:
                    earnings_text = extract_from_google_docs_url(google_docs_url)
                except (ValueError, ImportError) as e:
                    return JSONResponse({"error": str(e)}, status_code=400)
            else:
                earnings_text = body.get("earnings_text", "")

        if not earnings_text or not earnings_text.strip():
            return JSONResponse({"error": "No earnings text provided"}, status_code=400)

        # --- Perform analysis with selected provider ---
        analyzer = EarningsReportAnalyzer(provider=provider)
        result = analyzer.analyze_earnings(earnings_text, company_name)

        # Add to history
        history_entry = {
            "id": len(analysis_history),
            "timestamp": datetime.now().isoformat(),
            "company": company_name or result.get("company_info", {}).get("name", "Unknown"),
            "sentiment_score": result.get("sentiment_analysis", {}).get("sentiment_score", 0),
            "analysis": result,
        }
        analysis_history.append(history_entry)

        return result

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/history")
async def get_history():
    """Get analysis history"""
    return analysis_history


@app.get("/api/export/{analysis_id}")
async def export_analysis(analysis_id: int):
    """Export specific analysis as JSON"""
    if analysis_id >= len(analysis_history):
        return JSONResponse({"error": "Analysis not found"}, status_code=404)

    analysis = analysis_history[analysis_id]

    # Create temporary file
    filename = f"analysis_{analysis_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(tempfile.gettempdir(), filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2)

    return FileResponse(filepath, filename=filename, media_type="application/json")


@app.post("/api/compare")
async def compare_reports(request: Request):
    """Compare two earnings reports"""
    try:
        body = await request.json()
        current_text = body.get("current_report", "")
        previous_text = body.get("previous_report", "")
        company_name = body.get("company_name", "")
        provider = body.get("provider", "anthropic")

        if not current_text or not previous_text:
            return JSONResponse({"error": "Both reports required"}, status_code=400)

        analyzer = EarningsReportAnalyzer(provider=provider)
        comparison = analyzer.compare_earnings(current_text, previous_text, company_name)
        return comparison

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 70)
    print("Starting Earnings Report Analyzer Web Dashboard")
    print("=" * 70)
    print("\nAccess the dashboard at: http://localhost:5000")
    print("API docs available at:   http://localhost:5000/docs")
    print("\nSet API keys for your providers as environment variables:")
    print("   ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY, DEEPSEEK_API_KEY")
    print("\nPress CTRL+C to stop the server\n")

    uvicorn.run("web_dashboard:app", host="127.0.0.1", port=5000, reload=True)
