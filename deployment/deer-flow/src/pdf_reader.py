"""
PDF Reader Tool
===============
Extracts text and metadata from research PDFs found via crawl or upload.
Falls back gracefully when neither pymupdf nor pdfplumber is installed.

Usage:
    from src.pdf_reader import extract_pdf, extract_pdf_from_url
    doc = extract_pdf("/path/to/paper.pdf")
    print(doc["text"])
    print(doc["metadata"])
    doc = await extract_pdf_from_url("https://arxiv.org/pdf/2301.00001")
"""
from __future__ import annotations

import asyncio
import os
import tempfile
from typing import Any


def extract_pdf(path: str, max_pages: int = 50) -> dict[str, Any]:
    """Extract text from a local PDF file."""
    try:
        import fitz  # type: ignore  # pip install pymupdf
        doc = fitz.open(path)
        pages = min(len(doc), max_pages)
        text_parts = [doc[i].get_text() for i in range(pages)]
        return {
            "text": "\n".join(text_parts),
            "metadata": doc.metadata or {},
            "pages": len(doc),
            "backend": "pymupdf",
        }
    except ImportError:
        pass

    try:
        import pdfplumber  # type: ignore  # pip install pdfplumber
        with pdfplumber.open(path) as pdf:
            n = len(pdf.pages)
            text_parts = [
                (pdf.pages[i].extract_text() or "")
                for i in range(min(n, max_pages))
            ]
        return {"text": "\n".join(text_parts), "metadata": {}, "pages": n, "backend": "pdfplumber"}
    except ImportError:
        pass

    raise RuntimeError(
        "No PDF library available.\n"
        "Install: pip install pymupdf  (preferred)\n"
        "     or: pip install pdfplumber"
    )


async def extract_pdf_from_url(
    url: str,
    timeout: int = 30,
    max_pages: int = 50,
) -> dict[str, Any]:
    """Download a PDF from url and extract its text asynchronously."""
    import httpx
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        content = resp.content

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        f.write(content)
        tmp_path = f.name

    try:
        result = await asyncio.get_event_loop().run_in_executor(
            None, extract_pdf, tmp_path, max_pages
        )
        result["source_url"] = url
        return result
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
