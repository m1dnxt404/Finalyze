"""
Enhanced Earnings Report Analyzer with Web Scraping and PDF Support.
Composes the core EarningsReportAnalyzer and adds URL fetching, SEC search,
PDF file reading, and an alert system.
"""

import re
from typing import Dict, List, Optional

from Modules import EarningsReportAnalyzer
from text_extractor import extract_from_pdf_bytes

try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


class EnhancedEarningsAnalyzer:
    """Analyzer with automatic report fetching, SEC search, and alerts."""

    def __init__(self, provider: str = "anthropic", api_key: Optional[str] = None):
        self.analyzer = EarningsReportAnalyzer(provider=provider, api_key=api_key)

    # ------------------------------------------------------------------
    # Source fetching
    # ------------------------------------------------------------------

    def fetch_from_url(self, url: str) -> str:
        """Fetch earnings report text from a URL (HTML or PDF)."""
        if not SCRAPING_AVAILABLE:
            raise ImportError("Install requests and beautifulsoup4 for web scraping")

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        content_type = response.headers.get("content-type", "").lower()
        if "pdf" in content_type:
            return extract_from_pdf_bytes(response.content)
        return self._extract_html_text(response.text)

    @staticmethod
    def _extract_html_text(html: str) -> str:
        """Extract clean text from HTML."""
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()
        lines = (line.strip() for line in soup.get_text().splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return "\n".join(chunk for chunk in chunks if chunk)

    def extract_from_pdf_file(self, pdf_path: str) -> str:
        """Read a local PDF file and return its text."""
        with open(pdf_path, "rb") as f:
            return extract_from_pdf_bytes(f.read())

    # ------------------------------------------------------------------
    # SEC EDGAR
    # ------------------------------------------------------------------

    def search_sec_filings(self, ticker: str, filing_type: str = "8-K") -> List[Dict]:
        """Search SEC EDGAR for recent filings of the given type."""
        if not SCRAPING_AVAILABLE:
            raise ImportError("Install requests and beautifulsoup4 for SEC searching")

        base_url = "https://www.sec.gov/cgi-bin/browse-edgar"
        params = {
            "action": "getcompany",
            "CIK": ticker,
            "type": filing_type,
            "dateb": "",
            "owner": "exclude",
            "count": "10",
            "search_text": "",
        }
        headers = {"User-Agent": "Mozilla/5.0 (compatible; EarningsAnalyzer/1.0)"}

        try:
            resp = requests.get(base_url, params=params, headers=headers)
            soup = BeautifulSoup(resp.text, "html.parser")
            table = soup.find("table", {"class": "tableFile2"})
            filings = []
            if table:
                for row in table.find_all("tr")[1:6]:
                    cols = row.find_all("td")
                    if len(cols) >= 4:
                        link = cols[1].find("a")
                        filings.append({
                            "type": cols[0].text.strip(),
                            "description": cols[2].text.strip(),
                            "filing_date": cols[3].text.strip(),
                            "documents_url": f"https://www.sec.gov{link['href']}" if link else None,
                        })
            return filings
        except Exception as e:
            print(f"SEC search error: {e}")
            return []

    # ------------------------------------------------------------------
    # Unified analysis entry-point
    # ------------------------------------------------------------------

    def analyze_with_source(self, source: str, source_type: str = "text",
                            company_name: str = None) -> Dict:
        """
        Analyze earnings from various sources.

        Args:
            source: Text content, file path, URL, or stock ticker.
            source_type: "text", "url", "pdf", or "ticker".
            company_name: Optional company name for context.
        """
        if source_type == "text":
            text = source
        elif source_type == "url":
            text = self.fetch_from_url(source)
        elif source_type == "pdf":
            text = self.extract_from_pdf_file(source)
        elif source_type == "ticker":
            filings = self.search_sec_filings(source, "8-K")
            if not filings:
                return {"error": f"No recent 8-K filings found for {source}"}
            text = self.fetch_from_url(filings[0]["documents_url"])
        else:
            return {"error": f"Unknown source_type: {source_type}"}

        # Truncate very long documents, keeping the most relevant sections
        max_chars = 100_000
        if len(text) > max_chars:
            text = self._extract_earnings_section(text) or text[:max_chars]

        return self.analyzer.analyze_earnings(text, company_name)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_earnings_section(text: str) -> Optional[str]:
        """Extract the most relevant earnings paragraphs from a long document."""
        keywords = [
            r"earnings?\s+release",
            r"financial\s+results?",
            r"q[1-4]\s+\d{4}\s+results?",
            r"quarterly\s+results?",
            r"revenue",
            r"net\s+income",
        ]
        paragraphs = text.split("\n\n")
        scored = []
        for i, para in enumerate(paragraphs):
            score = sum(1 for kw in keywords if re.search(kw, para, re.IGNORECASE))
            if score > 0:
                scored.append((score, i, para))
        if scored:
            scored.sort(reverse=True)
            return "\n\n".join(p[2] for p in scored[:20])
        return None

    def create_alert_system(self, analysis: Dict, thresholds: Dict) -> List[Dict]:
        """Generate alerts based on analysis results and custom thresholds."""
        alerts = []
        try:
            earnings = analysis.get("financial_metrics", {}).get("earnings", {})
            if earnings.get("beat_miss") == "beat":
                nums = re.findall(r"[\d.]+", str(earnings.get("eps_reported", "0")))
                exp_nums = re.findall(r"[\d.]+", str(earnings.get("eps_expected", "0")))
                if nums and exp_nums:
                    reported = float(nums[0])
                    expected = float(exp_nums[0])
                    if expected:
                        beat_pct = ((reported - expected) / expected) * 100
                        if beat_pct > thresholds.get("eps_beat_threshold", 5):
                            alerts.append({
                                "type": "STRONG_BEAT",
                                "severity": "high",
                                "message": f"EPS beat expectations by {beat_pct:.1f}%",
                                "value": beat_pct,
                            })

            sentiment_score = analysis.get("sentiment_analysis", {}).get("sentiment_score", 50)
            if sentiment_score < thresholds.get("sentiment_min", 40):
                alerts.append({
                    "type": "LOW_SENTIMENT",
                    "severity": "warning",
                    "message": f"Sentiment score below threshold: {sentiment_score}",
                    "value": sentiment_score,
                })

            red_flags = analysis.get("red_flags", [])
            if red_flags:
                alerts.append({
                    "type": "RED_FLAGS",
                    "severity": "critical",
                    "message": f"{len(red_flags)} red flag(s) identified",
                    "details": red_flags,
                })

            guidance = analysis.get("financial_metrics", {}).get("guidance", {})
            if not guidance.get("provided", False):
                alerts.append({
                    "type": "NO_GUIDANCE",
                    "severity": "info",
                    "message": "Company did not provide forward guidance",
                })
        except Exception as e:
            alerts.append({
                "type": "ERROR",
                "severity": "error",
                "message": f"Alert generation error: {e}",
            })
        return alerts


# Example usage
if __name__ == "__main__":
    ea = EnhancedEarningsAnalyzer()

    print("Enhanced Earnings Analyzer Demo\n" + "=" * 70)

    sample = """
    Apple Inc. Q1 2025 Results
    Revenue: $124.3B (up 6% YoY)
    EPS: $2.45 (beat est. $2.38)
    iPhone revenue: $72.1B
    Services: $24.5B (all-time high)
    Gross margin: 44.1%
    """

    print("\n1. Analyzing sample earnings text...")
    result = ea.analyze_with_source(sample, "text", "Apple Inc.")
    print(f"   Sentiment: {result.get('sentiment_analysis', {}).get('overall_tone', 'N/A')}")

    print("\n2. Generating alerts...")
    alerts = ea.create_alert_system(result, {"eps_beat_threshold": 3, "sentiment_min": 60})
    for alert in alerts:
        print(f"  [{alert['severity'].upper()}] {alert['message']}")

    print("\n" + "=" * 70 + "\nDemo complete!")
