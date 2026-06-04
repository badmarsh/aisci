"""PDF Reader Tool — extract text and tables from PDF files using PyMuPDF (fitz)."""

import json
import logging
import os

from langchain.tools import tool

logger = logging.getLogger(__name__)


@tool("read_pdf", parse_docstring=True)
def pdf_reader_tool(
    file_path: str,
    pages: list[int] | None = None,
    extract_tables: bool = False,
) -> str:
    """Extract text content from a PDF file. Use this to read research papers, reports, and documents.

    Args:
        file_path: Path to the PDF file (absolute or relative path).
        pages: Optional list of page numbers (0-indexed) to extract. If None, extracts all pages.
        extract_tables: If True, also attempt to extract tables from the PDF.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return json.dumps({"error": "PyMuPDF not installed. Run: pip install pymupdf", "file_path": file_path}, ensure_ascii=False)

    if not os.path.exists(file_path):
        return json.dumps({"error": f"File not found: {file_path}", "file_path": file_path}, ensure_ascii=False)

    try:
        doc = fitz.open(file_path)
        total_pages = len(doc)

        if pages is not None:
            page_range = [p for p in pages if 0 <= p < total_pages]
        else:
            page_range = list(range(total_pages))

        output = {
            "file_path": file_path,
            "total_pages": total_pages,
            "extracted_pages": len(page_range),
            "text": "",
        }

        text_parts = []
        tables = []
        for page_num in page_range:
            page = doc[page_num]
            text = page.get_text("text")
            text_parts.append(f"--- Page {page_num + 1} ---\n{text}")

            if extract_tables:
                try:
                    page_tables = page.find_tables()
                    for i, tab in enumerate(page_tables):
                        tables.append({
                            "page": page_num + 1,
                            "table_index": i,
                            "headers": tab.header.names if tab.header else [],
                            "rows": tab.extract(),
                        })
                except Exception:
                    pass

        output["text"] = "\n\n".join(text_parts)
        if tables:
            output["tables"] = tables

        doc.close()
        return json.dumps(output, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"PDF reading failed: {e}")
        return json.dumps({"error": str(e), "file_path": file_path}, ensure_ascii=False)
