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

# BUGFIX: cap remote PDF downloads so a hostile or misconfigured URL cannot
# stream unbounded bytes into memory / disk.
MAX_PDF_BYTES = int(os.getenv("PDF_MAX_BYTES", str(50 * 1024 * 1024)))  # 50 MiB


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
        # BUGFIX: stream + size check instead of buffering the whole body.
        async with client.stream("GET", url) as resp:
            resp.raise_for_status()
            content = bytearray()
            async for chunk in resp.aiter_bytes():
                content.extend(chunk)
                if len(content) > MAX_PDF_BYTES:
                    raise ValueError(
                        f"PDF exceeds MAX_PDF_BYTES={MAX_PDF_BYTES} at {url}"
                    )
            content = bytes(content)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        f.write(content)
        tmp_path = f.name

    try:
        # BUGFIX: asyncio.get_event_loop() is deprecated in 3.10+ and raises
        # DeprecationWarning / RuntimeError under 3.12+. Use asyncio.to_thread.
        result = await asyncio.to_thread(extract_pdf, tmp_path, max_pages)
        result["source_url"] = url
        return result
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
