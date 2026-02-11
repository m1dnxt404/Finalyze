"""
Enhanced Earnings Report Analyzer with Web Scraping and PDF Support
Automatically fetches and analyzes earnings reports from SEC filings
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from anthropic import Anthropic

try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False
    print("Warning: requests and beautifulsoup4 not installed. Web scraping disabled.")

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: PyPDF2 not installed. PDF parsing disabled.")


class EnhancedEarningsAnalyzer:
    """
    Enhanced analyzer with automatic report fetching capabilities
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"
        
    def fetch_from_url(self, url: str) -> str:
        """
        Fetch earnings report content from a URL
        
        Args:
            url: URL to the earnings report (HTML or PDF)
            
        Returns:
            Extracted text content
        """
        if not SCRAPING_AVAILABLE:
            raise ImportError("Install requests and beautifulsoup4 for web scraping")
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            
            if 'pdf' in content_type:
                return self._extract_pdf_from_response(response.content)
            else:
                return self._extract_html_text(response.text)
                
        except Exception as e:
            raise Exception(f"Failed to fetch URL: {str(e)}")
    
    def _extract_html_text(self, html: str) -> str:
        """Extract clean text from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_pdf_from_response(self, pdf_content: bytes) -> str:
        """Extract text from PDF bytes"""
        if not PDF_AVAILABLE:
            raise ImportError("Install PyPDF2 for PDF parsing")
        
        import io
        pdf_file = io.BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text
    
    def extract_from_pdf_file(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        if not PDF_AVAILABLE:
            raise ImportError("Install PyPDF2 for PDF parsing")
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        return text
    
    def search_sec_filings(self, ticker: str, filing_type: str = "8-K") -> List[Dict]:
        """
        Search SEC EDGAR for recent filings
        
        Args:
            ticker: Stock ticker symbol
            filing_type: Type of filing (8-K for earnings, 10-Q, 10-K, etc.)
            
        Returns:
            List of filing information dictionaries
        """
        if not SCRAPING_AVAILABLE:
            raise ImportError("Install requests and beautifulsoup4 for SEC searching")
        
        # SEC EDGAR search URL
        base_url = "https://www.sec.gov/cgi-bin/browse-edgar"
        params = {
            "action": "getcompany",
            "CIK": ticker,
            "type": filing_type,
            "dateb": "",
            "owner": "exclude",
            "count": "10",
            "search_text": ""
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; EarningsAnalyzer/1.0)"
        }
        
        try:
            response = requests.get(base_url, params=params, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            filings = []
            table = soup.find('table', {'class': 'tableFile2'})
            
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                for row in rows[:5]:  # Get latest 5
                    cols = row.find_all('td')
                    if len(cols) >= 4:
                        filing_info = {
                            'type': cols[0].text.strip(),
                            'description': cols[2].text.strip(),
                            'filing_date': cols[3].text.strip(),
                            'documents_url': None
                        }
                        
                        # Get documents link
                        link = cols[1].find('a')
                        if link:
                            filing_info['documents_url'] = f"https://www.sec.gov{link['href']}"
                        
                        filings.append(filing_info)
            
            return filings
            
        except Exception as e:
            print(f"SEC search error: {str(e)}")
            return []
    
    def analyze_with_source(self, source: str, source_type: str = "text", 
                           company_name: str = None) -> Dict:
        """
        Analyze earnings from various sources
        
        Args:
            source: Text content, file path, or URL
            source_type: "text", "url", "pdf", or "ticker"
            company_name: Optional company name
            
        Returns:
            Analysis dictionary
        """
        # Get the text content based on source type
        if source_type == "text":
            text = source
        elif source_type == "url":
            text = self.fetch_from_url(source)
        elif source_type == "pdf":
            text = self.extract_from_pdf_file(source)
        elif source_type == "ticker":
            # Search SEC and get latest 8-K
            filings = self.search_sec_filings(source, "8-K")
            if not filings:
                return {"error": f"No recent 8-K filings found for {source}"}
            
            # Try to fetch the first filing
            text = self.fetch_from_url(filings[0]['documents_url'])
        else:
            return {"error": f"Unknown source_type: {source_type}"}
        
        # Analyze the text
        return self._analyze_text(text, company_name)
    
    def _analyze_text(self, text: str, company_name: str = None) -> Dict:
        """Core analysis function"""
        # Truncate if too long (Claude has context limits)
        max_chars = 100000  # ~25k tokens
        if len(text) > max_chars:
            # Try to find the earnings section
            text = self._extract_earnings_section(text) or text[:max_chars]
        
        company_context = f" for {company_name}" if company_name else ""
        
        prompt = f"""Analyze this earnings report{company_context} and provide structured analysis.

EARNINGS REPORT:
{text}

Provide comprehensive analysis in JSON format with these sections:
- company_info (name, ticker, period, date)
- financial_metrics (revenue, earnings, margins, guidance)
- key_highlights (positive developments)
- concerns_risks (challenges and risks)
- sentiment_analysis (tone, confidence, outlook, score 0-100)
- business_segments (segment performance)
- notable_quotes (management statements)
- market_implications (likely reaction, takeaways)
- red_flags (concerning patterns)
- analyst_summary (executive summary)

Be thorough and data-driven. Extract all numerical values with proper context."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            analysis_text = response.content[0].text
            
            # Parse JSON
            if "```json" in analysis_text:
                json_start = analysis_text.find("```json") + 7
                json_end = analysis_text.find("```", json_start)
                analysis_text = analysis_text[json_start:json_end].strip()
            
            analysis_data = json.loads(analysis_text)
            analysis_data["metadata"] = {
                "analyzed_at": datetime.now().isoformat(),
                "model": self.model,
                "tokens": {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens
                }
            }
            
            return analysis_data
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _extract_earnings_section(self, text: str) -> Optional[str]:
        """Try to extract just the earnings-related section from long documents"""
        # Look for common earnings keywords
        earnings_keywords = [
            r"earnings?\s+release",
            r"financial\s+results?",
            r"q[1-4]\s+\d{4}\s+results?",
            r"quarterly\s+results?",
            r"revenue",
            r"net\s+income"
        ]
        
        # Find sections with high keyword density
        paragraphs = text.split('\n\n')
        scored_paragraphs = []
        
        for i, para in enumerate(paragraphs):
            score = sum(1 for keyword in earnings_keywords 
                       if re.search(keyword, para, re.IGNORECASE))
            if score > 0:
                scored_paragraphs.append((score, i, para))
        
        if scored_paragraphs:
            # Sort by score and take top paragraphs
            scored_paragraphs.sort(reverse=True)
            relevant_text = '\n\n'.join([p[2] for p in scored_paragraphs[:20]])
            return relevant_text
        
        return None
    
    def create_alert_system(self, analysis: Dict, thresholds: Dict) -> List[Dict]:
        """
        Generate alerts based on analysis and custom thresholds
        
        Args:
            analysis: Analysis results
            thresholds: Dictionary of threshold values
                       e.g., {"eps_beat_threshold": 0.05, "sentiment_min": 60}
        
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        try:
            # Check EPS beat/miss
            earnings = analysis.get('financial_metrics', {}).get('earnings', {})
            if earnings.get('beat_miss') == 'beat':
                eps_reported = float(re.findall(r'[\d.]+', str(earnings.get('eps_reported', '0')))[0])
                eps_expected = float(re.findall(r'[\d.]+', str(earnings.get('eps_expected', '0')))[0])
                beat_percentage = ((eps_reported - eps_expected) / eps_expected) * 100
                
                if beat_percentage > thresholds.get('eps_beat_threshold', 5):
                    alerts.append({
                        'type': 'STRONG_BEAT',
                        'severity': 'high',
                        'message': f"EPS beat expectations by {beat_percentage:.1f}%",
                        'value': beat_percentage
                    })
            
            # Check sentiment
            sentiment_score = analysis.get('sentiment_analysis', {}).get('sentiment_score', 50)
            if sentiment_score < thresholds.get('sentiment_min', 40):
                alerts.append({
                    'type': 'LOW_SENTIMENT',
                    'severity': 'warning',
                    'message': f"Sentiment score below threshold: {sentiment_score}",
                    'value': sentiment_score
                })
            
            # Check for red flags
            red_flags = analysis.get('red_flags', [])
            if red_flags:
                alerts.append({
                    'type': 'RED_FLAGS',
                    'severity': 'critical',
                    'message': f"{len(red_flags)} red flag(s) identified",
                    'details': red_flags
                })
            
            # Check guidance
            guidance = analysis.get('financial_metrics', {}).get('guidance', {})
            if not guidance.get('provided', False):
                alerts.append({
                    'type': 'NO_GUIDANCE',
                    'severity': 'info',
                    'message': "Company did not provide forward guidance"
                })
            
        except Exception as e:
            alerts.append({
                'type': 'ERROR',
                'severity': 'error',
                'message': f"Alert generation error: {str(e)}"
            })
        
        return alerts


# Example usage
if __name__ == "__main__":
    analyzer = EnhancedEarningsAnalyzer()
    
    print("Enhanced Earnings Analyzer Demo\n")
    print("=" * 70)
    
    # Example 1: Analyze from text
    print("\n1. Analyzing sample earnings text...")
    sample = """
    Apple Inc. Q1 2025 Results
    Revenue: $124.3B (up 6% YoY)
    EPS: $2.45 (beat est. $2.38)
    iPhone revenue: $72.1B
    Services: $24.5B (all-time high)
    Gross margin: 44.1%
    """
    
    result = analyzer.analyze_with_source(sample, "text", "Apple Inc.")
    print(f"✓ Analysis complete - Sentiment: {result.get('sentiment_analysis', {}).get('overall_tone', 'N/A')}")
    
    # Example 2: Alert system
    print("\n2. Generating alerts...")
    thresholds = {
        'eps_beat_threshold': 3,
        'sentiment_min': 60
    }
    alerts = analyzer.create_alert_system(result, thresholds)
    for alert in alerts:
        print(f"  [{alert['severity'].upper()}] {alert['message']}")
    
    print("\n" + "=" * 70)
    print("Demo complete!")
