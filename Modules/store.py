"""
ChromaDB vector store for persistent report storage and semantic retrieval.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

import chromadb


_client = None


def get_client() -> chromadb.ClientAPI:
    """Return a singleton PersistentClient."""
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path="./data/chromadb")
    return _client


def _get_collection():
    """Return the reports collection."""
    return get_client().get_or_create_collection("reports")


def _build_document(analysis: Dict) -> str:
    """Build the text that gets embedded — analyst summary + key highlights."""
    parts = []

    company = analysis.get("company_info", {})
    if company.get("name"):
        parts.append(f"Company: {company['name']}")
    if company.get("reporting_period"):
        parts.append(f"Period: {company['reporting_period']}")

    summary = analysis.get("analyst_summary", "")
    if summary:
        parts.append(summary)

    highlights = analysis.get("key_highlights", [])
    if highlights:
        parts.append("Key highlights: " + "; ".join(highlights))

    concerns = analysis.get("concerns_risks", [])
    if concerns:
        parts.append("Concerns: " + "; ".join(concerns))

    return "\n".join(parts)


def save_report(analysis: Dict, company_name: str = "") -> str:
    """Store a report analysis in ChromaDB. Returns the report ID."""
    collection = _get_collection()

    company_info = analysis.get("company_info", {})
    ticker = company_info.get("ticker", "UNKNOWN")
    quarter = company_info.get("reporting_period", "")
    timestamp = datetime.now().isoformat()
    report_id = f"{ticker}-{quarter}-{timestamp}".replace(" ", "_")

    resolved_name = company_name or company_info.get("name", "Unknown")
    sentiment = analysis.get("sentiment_analysis", {}).get("sentiment_score", 0)

    document = _build_document(analysis)

    # ChromaDB metadata values must be str, int, float, or bool.
    metadata = {
        "company": resolved_name,
        "ticker": ticker,
        "quarter": quarter,
        "timestamp": timestamp,
        "sentiment_score": int(sentiment) if sentiment else 0,
        "analysis_json": json.dumps(analysis),
    }

    collection.add(
        documents=[document],
        metadatas=[metadata],
        ids=[report_id],
    )
    return report_id


def get_history() -> List[Dict]:
    """Return all stored reports, most recent first."""
    collection = _get_collection()
    results = collection.get(include=["metadatas"])

    history = []
    for id_, meta in zip(results["ids"], results["metadatas"]):
        history.append({
            "id": id_,
            "timestamp": meta.get("timestamp", ""),
            "company": meta.get("company", "Unknown"),
            "ticker": meta.get("ticker", ""),
            "quarter": meta.get("quarter", ""),
            "sentiment_score": meta.get("sentiment_score", 0),
        })

    history.sort(key=lambda x: x["timestamp"], reverse=True)
    return history


def get_report(report_id: str) -> Optional[Dict]:
    """Fetch a single report by ID, including the full analysis."""
    collection = _get_collection()
    results = collection.get(ids=[report_id], include=["metadatas"])

    if not results["ids"]:
        return None

    meta = results["metadatas"][0]
    return {
        "id": report_id,
        "timestamp": meta.get("timestamp", ""),
        "company": meta.get("company", "Unknown"),
        "sentiment_score": meta.get("sentiment_score", 0),
        "analysis": json.loads(meta.get("analysis_json", "{}")),
    }


def query_reports(query: str, n: int = 5, company: str = None) -> List[Dict]:
    """Semantic search across all stored reports."""
    collection = _get_collection()

    if collection.count() == 0:
        return []

    kwargs = {
        "query_texts": [query],
        "n_results": min(n, collection.count()),
        "include": ["documents", "metadatas", "distances"],
    }
    if company:
        kwargs["where"] = {"company": company}

    results = collection.query(**kwargs)

    reports = []
    for id_, doc, meta, dist in zip(
        results["ids"][0],
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        reports.append({
            "id": id_,
            "company": meta.get("company", "Unknown"),
            "quarter": meta.get("quarter", ""),
            "timestamp": meta.get("timestamp", ""),
            "sentiment_score": meta.get("sentiment_score", 0),
            "relevance": round(1 - dist, 4),
            "summary": doc,
            "analysis": json.loads(meta.get("analysis_json", "{}")),
        })
    return reports


def get_company_context(company: str, n: int = 3) -> List[Dict]:
    """Retrieve past reports for a specific company (most recent first)."""
    collection = _get_collection()

    if collection.count() == 0:
        return []

    results = collection.get(
        where={"company": company},
        include=["documents", "metadatas"],
    )

    if not results["ids"]:
        return []

    reports = []
    for id_, doc, meta in zip(
        results["ids"], results["documents"], results["metadatas"]
    ):
        reports.append({
            "id": id_,
            "quarter": meta.get("quarter", ""),
            "timestamp": meta.get("timestamp", ""),
            "summary": doc,
        })

    reports.sort(key=lambda x: x["timestamp"], reverse=True)
    return reports[:n]
