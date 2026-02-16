"""
Text extraction module using LangChain document loaders.
Supports PDF, DOCX, TXT files and Google Docs URLs.
"""

import os
import re
import tempfile

try:
    from langchain_community.document_loaders import PyPDFLoader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from langchain_community.document_loaders import Docx2txtLoader
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}


def _bytes_to_tempfile(data: bytes, suffix: str) -> str:
    """Write bytes to a temporary file and return the path. Caller must delete."""
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    tmp.write(data)
    tmp.close()
    return tmp.name


def extract_from_pdf_bytes(data: bytes) -> str:
    """Extract text from PDF file bytes using LangChain PyPDFLoader."""
    if not PDF_AVAILABLE:
        raise ImportError("langchain-community and pypdf are required for PDF support. "
                          "Install with: pip install langchain-community pypdf")
    path = _bytes_to_tempfile(data, ".pdf")
    try:
        loader = PyPDFLoader(path)
        docs = loader.load()
        return "\n".join(doc.page_content for doc in docs).strip()
    finally:
        os.unlink(path)


def extract_from_docx_bytes(data: bytes) -> str:
    """Extract text from DOCX file bytes using LangChain Docx2txtLoader."""
    if not DOCX_AVAILABLE:
        raise ImportError("langchain-community and docx2txt are required for DOCX support. "
                          "Install with: pip install langchain-community docx2txt")
    path = _bytes_to_tempfile(data, ".docx")
    try:
        loader = Docx2txtLoader(path)
        docs = loader.load()
        return "\n".join(doc.page_content for doc in docs).strip()
    finally:
        os.unlink(path)


def extract_from_txt_bytes(data: bytes) -> str:
    """Extract text from TXT file bytes, trying multiple encodings."""
    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            return data.decode(encoding).strip()
        except (UnicodeDecodeError, ValueError):
            continue
    return data.decode("utf-8", errors="replace").strip()


def extract_from_uploaded_file(data: bytes, filename: str) -> str:
    """
    Extract text from uploaded file bytes.
    Validates extension and size, then dispatches to the correct loader.

    Args:
        data: Raw file bytes
        filename: Original filename (used to determine type)

    Returns:
        Extracted text string

    Raises:
        ValueError: if file type is unsupported or file is too large
        ImportError: if required library is missing
    """
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type '{ext}'. Allowed: PDF, DOCX, TXT")

    if len(data) > MAX_FILE_SIZE:
        raise ValueError(f"File too large ({len(data) / 1024 / 1024:.1f} MB). Maximum is 10 MB.")

    if ext == ".pdf":
        return extract_from_pdf_bytes(data)
    elif ext == ".docx":
        return extract_from_docx_bytes(data)
    else:
        return extract_from_txt_bytes(data)


def extract_from_google_docs_url(url: str) -> str:
    """
    Fetch plain text from a public Google Docs URL.

    Args:
        url: A Google Docs sharing URL

    Returns:
        Document text

    Raises:
        ValueError: if URL format is invalid
        ImportError: if requests is not installed
        Exception: if the fetch fails
    """
    if not REQUESTS_AVAILABLE:
        raise ImportError("requests is required for Google Docs support. Install with: pip install requests")

    match = re.search(r"/document/d/([a-zA-Z0-9_-]+)", url)
    if not match:
        raise ValueError("Invalid Google Docs URL. Expected a URL like https://docs.google.com/document/d/...")

    doc_id = match.group(1)
    export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"

    response = requests.get(export_url, timeout=30)

    if response.status_code == 404:
        raise ValueError("Document not found. Make sure the Google Doc exists and sharing is set to 'Anyone with the link'.")
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch document (HTTP {response.status_code}). Ensure the document is publicly shared.")

    text = response.text.strip()
    if not text:
        raise ValueError("The Google Doc appears to be empty.")

    return text
