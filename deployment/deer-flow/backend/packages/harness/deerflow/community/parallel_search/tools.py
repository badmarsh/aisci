"""Multi-Engine Parallel Search Tool — queries Tavily, Brave Search, and DuckDuckGo
simultaneously, then merges and deduplicates results before returning."""

import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from langchain.tools import tool

logger = logging.getLogger(__name__)


def _search_tavily(query: str, max_results: int = 5) -> list[dict]:
    """Search using Tavily."""
    import os

    api_key = os.environ.get("TAVILY_API_KEY", "")
    if not api_key:
        return []

    import httpx

    url = "https://api.tavily.com/search"
    body = {
        "api_key": api_key,
        "query": query,
        "max_results": max_results,
        "search_depth": "basic",
        "include_answer": False,
    }
    try:
        resp = httpx.post(url, json=body, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", r.get("snippet", "")),
                "source": "tavily",
            }
            for r in data.get("results", [])
        ]
    except Exception as e:
        logger.error(f"Tavily search failed: {e}")
        return []


def _search_brave(query: str, max_results: int = 5) -> list[dict]:
    """Search using Brave Search API."""
    import os

    api_key = os.environ.get("BRAVE_SEARCH_API_KEY") or os.environ.get("BRAVE_API_KEY", "")
    if not api_key:
        return []

    import httpx

    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {"Accept": "application/json", "Accept-Encoding": "gzip", "X-Subscription-Token": api_key}
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
                "content": r.get("description", ""),
                "source": "brave",
            }
            for r in results
        ]
    except Exception as e:
        logger.error(f"Brave search failed: {e}")
        return []


def _search_ddg(query: str, max_results: int = 5) -> list[dict]:
    """Search using DuckDuckGo."""
    try:
        from ddgs import DDGS
    except ImportError:
        return []

    ddgs = DDGS(timeout=15)
    try:
        results = ddgs.text(query, region="wt-wt", safesearch="moderate", max_results=max_results)
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("href", r.get("link", "")),
                "content": r.get("body", ""),
                "source": "duckduckgo",
            }
            for r in results
        ]
    except Exception as e:
        logger.error(f"DDG search failed: {e}")
        return []


@tool("parallel_search", parse_docstring=True)
def parallel_search_tool(
    query: str,
    max_results: int = 5,
) -> str:
    """Search the web using multiple engines simultaneously (Tavily + Brave + DuckDuckGo).
    Results are merged and deduplicated for maximum coverage.

    Args:
        query: Search query string.
        max_results: Maximum results per engine. Default is 5.
    """
    all_results = []
    seen_urls = set()
    engines_used = []

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(_search_tavily, query, max_results): "tavily",
            executor.submit(_search_brave, query, max_results): "brave",
            executor.submit(_search_ddg, query, max_results): "duckduckgo",
        }
        for future in as_completed(futures):
            engine = futures[future]
            try:
                results = future.result()
                if results:
                    engines_used.append(engine)
                for r in results:
                    url = r["url"]
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_results.append(r)
            except Exception as e:
                logger.warning(f"Search engine {engine} failed: {e}")

    if not all_results:
        return json.dumps({"error": "No results from any search engine", "query": query}, ensure_ascii=False)

    return json.dumps({
        "query": query,
        "total_results": len(all_results),
        "engines_used": engines_used,
        "results": all_results,
    }, indent=2, ensure_ascii=False)
