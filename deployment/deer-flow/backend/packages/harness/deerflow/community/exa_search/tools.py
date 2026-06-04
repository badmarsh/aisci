"""Exa AI Neural Search Tool — neural search for high-quality results on niche/technical topics."""

import json
import logging
import os

from langchain.tools import tool

logger = logging.getLogger(__name__)


def _exa_search(query: str, max_results: int = 5) -> list[dict]:
    """Execute search using Exa AI neural search API."""
    api_key = os.environ.get("EXA_API_KEY", "")
    if not api_key:
        logger.warning("EXA_API_KEY not set — Exa search unavailable")
        return []

    import httpx

    url = "https://api.exa.ai/search"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }
    body = {
        "query": query,
        "numResults": max_results,
        "useAutoprompt": True,
        "text": True,
    }

    try:
        resp = httpx.post(url, headers=headers, json=body, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("text", ""),
            }
            for r in results
        ]
    except Exception as e:
        logger.error(f"Exa search failed: {e}")
        return []


@tool("exa_search", parse_docstring=True)
def exa_search_tool(
    query: str,
    max_results: int = 5,
) -> str:
    """Search using Exa AI neural search. Best for niche, technical, or hard-to-find topics.

    Args:
        query: Search query string.
        max_results: Maximum number of results to return. Default is 5.
    """
    results = _exa_search(query, max_results)
    if not results:
        return json.dumps({"error": "No results from Exa", "query": query}, ensure_ascii=False)
    return json.dumps({"query": query, "total_results": len(results), "results": results}, indent=2, ensure_ascii=False)
