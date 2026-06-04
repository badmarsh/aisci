"""Brave Search Tool — web search via Brave Search API (requires API key)."""

import json
import logging
import os

from langchain.tools import tool

logger = logging.getLogger(__name__)


def _brave_search(query: str, max_results: int = 5) -> list[dict]:
    """Execute search using Brave Search API."""
    api_key = os.environ.get("BRAVE_SEARCH_API_KEY") or os.environ.get("BRAVE_API_KEY", "")
    if not api_key:
        logger.warning("BRAVE_SEARCH_API_KEY not set — Brave search unavailable")
        return []

    import httpx

    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key,
    }
    params = {"q": query, "count": max_results, "search_lang": "en"}

    try:
        resp = httpx.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("web", {}).get("results", [])
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("description", r.get("snippet", "")),
            }
            for r in results
        ]
    except Exception as e:
        logger.error(f"Brave search failed: {e}")
        return []


@tool("brave_search", parse_docstring=True)
def brave_search_tool(
    query: str,
    max_results: int = 5,
) -> str:
    """Search the web using Brave Search API. Returns high-quality web results with snippets.

    Args:
        query: Search query string.
        max_results: Maximum number of results to return. Default is 5.
    """
    results = _brave_search(query, max_results)
    if not results:
        return json.dumps({"error": "No results from Brave Search", "query": query}, ensure_ascii=False)
    return json.dumps({"query": query, "total_results": len(results), "results": results}, indent=2, ensure_ascii=False)
