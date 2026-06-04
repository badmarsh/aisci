"""SearXNG Search Tool — self-hosted meta-search engine (no API key required)."""

import json
import logging
import os

from langchain.tools import tool

logger = logging.getLogger(__name__)

# Default SearXNG instance URL — can be overridden via env var
_SEARXNG_URL = os.environ.get("SEARXNG_URL", "http://localhost:8080")


def _searxng_search(query: str, max_results: int = 5) -> list[dict]:
    """Execute search using a self-hosted SearXNG instance."""
    import httpx

    url = f"{_SEARXNG_URL}/search"
    params = {
        "q": query,
        "format": "json",
        "categories": "general",
        "language": "en",
        "pageno": 1,
    }

    try:
        resp = httpx.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])[:max_results]
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", r.get("snippet", "")),
            }
            for r in results
        ]
    except Exception as e:
        logger.error(f"SearXNG search failed: {e}")
        return []


@tool("searxng_search", parse_docstring=True)
def searxng_search_tool(
    query: str,
    max_results: int = 5,
) -> str:
    """Search the web using a self-hosted SearXNG instance. Free, private, no API key needed.

    Args:
        query: Search query string.
        max_results: Maximum number of results to return. Default is 5.
    """
    results = _searxng_search(query, max_results)
    if not results:
        return json.dumps({"error": "No results from SearXNG", "query": query}, ensure_ascii=False)
    return json.dumps({"query": query, "total_results": len(results), "results": results}, indent=2, ensure_ascii=False)
