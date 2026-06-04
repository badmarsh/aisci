"""Citation Manager Tool — track research sources and generate formatted citations."""

import hashlib
import json
import logging
import os
import re
from datetime import datetime

from langchain.tools import tool

logger = logging.getLogger(__name__)

# In-memory citation store (thread-local in production; file-backed for persistence)
_CITATION_STORE = {}


def _get_store_path(thread_id: str) -> str:
    """Get the file path for persistent citation storage."""
    base = os.environ.get("DEER_FLOW_HOME", "/tmp")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, f"citations_{thread_id}.json")


def _load_citations(thread_id: str) -> list[dict]:
    """Load citations from persistent storage."""
    global _CITATION_STORE
    path = _get_store_path(thread_id)
    if thread_id in _CITATION_STORE:
        return _CITATION_STORE[thread_id]
    if os.path.exists(path):
        with open(path) as f:
            _CITATION_STORE[thread_id] = json.load(f)
        return _CITATION_STORE[thread_id]
    return []


def _save_citations(thread_id: str, citations: list[dict]) -> None:
    """Save citations to persistent storage."""
    global _CITATION_STORE
    _CITATION_STORE[thread_id] = citations
    path = _get_store_path(thread_id)
    with open(path, "w") as f:
        json.dump(citations, f, indent=2)


def _make_citation_id(url: str) -> str:
    """Generate a unique citation ID from URL."""
    return hashlib.md5(url.encode()).hexdigest()[:8]


def _format_apa(source: dict) -> str:
    """Format a citation in APA style."""
    author = source.get("authors", "Unknown")
    year = source.get("year", "n.d.")
    title = source.get("title", "Untitled")
    source_name = source.get("source_name", source.get("publisher", ""))
    url = source.get("url", "")

    citation = f"{author}. ({year}). {title}."
    if source_name:
        citation += f" {source_name}."
    if url:
        citation += f" {url}"
    return citation


def _format_mla(source: dict) -> str:
    """Format a citation in MLA style."""
    author = source.get("authors", "Unknown")
    title = source.get("title", "Untitled")
    source_name = source.get("source_name", source.get("publisher", ""))
    year = source.get("year", "n.d.")
    url = source.get("url", "")

    citation = f"{author}. \"{title}.\""
    if source_name:
        citation += f" {source_name},"
    citation += f" {year}."
    if url:
        citation += f" {url}."
    return citation


@tool("add_citation", parse_docstring=True)
def citation_add_tool(
    thread_id: str,
    url: str,
    title: str,
    authors: str = "Unknown",
    year: str | None = None,
    source_name: str = "",
    note: str = "",
) -> str:
    """Add a research source to the citation manager. Call this each time you use a source during research.

    Args:
        thread_id: The thread/session ID for persistent storage.
        url: URL of the source.
        title: Title of the article, paper, or page.
        authors: Author name(s). Default is "Unknown".
        year: Publication year. Auto-detected from URL if not provided.
        source_name: Journal, website, or publisher name.
        note: Optional note about why this source was cited.
    """
    # Auto-extract year from URL if not provided
    if not year:
        match = re.search(r"/(\d{4})/", url)
        if match:
            year = match.group(1)
        else:
            year = str(datetime.now().year)

    citation_id = _make_citation_id(url)
    citation = {
        "id": citation_id,
        "url": url,
        "title": title,
        "authors": authors,
        "year": year,
        "source_name": source_name,
        "note": note,
        "added_at": datetime.now().isoformat(),
    }

    citations = _load_citations(thread_id)

    # Deduplicate by URL
    existing = next((c for c in citations if c["url"] == url), None)
    if existing:
        return json.dumps({"message": f"Citation already exists: [{citation_id}] {title}", "citation_id": citation_id, "duplicate": True}, indent=2, ensure_ascii=False)

    citations.append(citation)
    _save_citations(thread_id, citations)

    return json.dumps({"message": f"Citation added: [{citation_id}] {title}", "citation_id": citation_id, "total_citations": len(citations)}, indent=2, ensure_ascii=False)


@tool("generate_citations", parse_docstring=True)
def citation_generate_tool(
    thread_id: str,
    format: str = "apa",
    include_urls: bool = True,
) -> str:
    """Generate formatted citations for all sources tracked during research. Call this at the end of a report.

    Args:
        thread_id: The thread/session ID to load citations from.
        format: Citation format. Options: "apa", "mla", "markdown". Default is "apa".
        include_urls: Whether to include URLs in the output. Default is True.
    """
    citations = _load_citations(thread_id)
    if not citations:
        return json.dumps({"message": "No citations tracked for this thread.", "thread_id": thread_id}, indent=2, ensure_ascii=False)

    # Sort alphabetically by authors
    citations.sort(key=lambda c: c.get("authors", ""))

    if format == "apa":
        formatted = [_format_apa(c) for c in citations]
    elif format == "mla":
        formatted = [_format_mla(c) for c in citations]
    elif format == "markdown":
        formatted = []
        for i, c in enumerate(citations, 1):
            line = f"{i}. **{c['authors']}** ({c['year']}). *{c['title']}*."
            if c.get("source_name"):
                line += f" {c['source_name']}."
            if include_urls and c.get("url"):
                line += f" [{c['url']}]({c['url']})"
            formatted.append(line)
    else:
        return json.dumps({"error": f"Unknown format: {format}. Options: apa, mla, markdown"}, ensure_ascii=False)

    output = {
        "thread_id": thread_id,
        "format": format,
        "total_citations": len(citations),
        "citations": formatted,
    }
    return json.dumps(output, indent=2, ensure_ascii=False)


@tool("list_citations", parse_docstring=True)
def citation_list_tool(
    thread_id: str,
) -> str:
    """List all citations tracked for a research thread. Use this to check what sources have been cited so far.

    Args:
        thread_id: The thread/session ID to list citations for.
    """
    citations = _load_citations(thread_id)
    if not citations:
        return json.dumps({"message": "No citations tracked.", "thread_id": thread_id}, indent=2, ensure_ascii=False)

    output = [{"id": c["id"], "url": c["url"], "title": c["title"], "authors": c["authors"], "year": c["year"]} for c in citations]
    return json.dumps({"thread_id": thread_id, "total_citations": len(citations), "citations": output}, indent=2, ensure_ascii=False)
