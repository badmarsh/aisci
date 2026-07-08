"""
Quick-Win #1 - Parallel Multi-Engine Search
============================================
Fans out a query to Tavily, Brave, DuckDuckGo, Exa, and Serper simultaneously
using asyncio.gather, then merges and deduplicates results by URL.

Usage:
    from src.parallel_search import parallel_web_search
    results = await parallel_web_search("my query", max_results=8)

Each result dict:
    {"title": str, "url": str, "content": str, "source": str}
"""
from __future__ import annotations

import asyncio
import os
from typing import Any


async def _search_tavily(query: str, max_results: int) -> list[dict]:
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key:
        return []
    try:
        from tavily import AsyncTavilyClient  # type: ignore
        client = AsyncTavilyClient(api_key=api_key)
        resp = await client.search(query, max_results=max_results)
        return [
            {"title": r.get("title", ""), "url": r.get("url", ""),
             "content": r.get("content", ""), "source": "tavily"}
            for r in resp.get("results", [])
        ]
    except Exception:
        return []


async def _search_brave(query: str, max_results: int) -> list[dict]:
    api_key = os.getenv("BRAVE_API_KEY", "")
    if not api_key:
        return []
    try:
        import httpx
        headers = {"Accept": "application/json", "X-Subscription-Token": api_key}
        params = {"q": query, "count": max_results}
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers, params=params
            )
            resp.raise_for_status()
            data = resp.json()
        return [
            {"title": r.get("title", ""), "url": r.get("url", ""),
             "content": r.get("description", ""), "source": "brave"}
            for r in data.get("web", {}).get("results", [])
        ]
    except Exception:
        return []


async def _search_ddg(query: str, max_results: int) -> list[dict]:
    try:
        from duckduckgo_search import AsyncDDGS  # type: ignore
        async with AsyncDDGS() as ddgs:
            results = await ddgs.atext(query, max_results=max_results)
        return [
            {"title": r.get("title", ""), "url": r.get("href", ""),
             "content": r.get("body", ""), "source": "duckduckgo"}
            for r in (results or [])
        ]
    except Exception:
        return []


async def _search_exa(query: str, max_results: int) -> list[dict]:
    api_key = os.getenv("EXA_API_KEY", "")
    if not api_key:
        return []
    try:
        import httpx
        payload = {"query": query, "numResults": max_results, "contents": {"text": True}}
        headers = {"x-api-key": api_key, "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=12) as client:
            resp = await client.post(
                "https://api.exa.ai/search", json=payload, headers=headers
            )
            resp.raise_for_status()
            data = resp.json()
        return [
            {"title": r.get("title", ""), "url": r.get("url", ""),
             "content": (r.get("text") or r.get("snippet", ""))[:800],
             "source": "exa"}
            for r in data.get("results", [])
        ]
    except Exception:
        return []


async def _search_serper(query: str, max_results: int) -> list[dict]:
    api_key = os.getenv("SERPER_API_KEY", "")
    if not api_key:
        return []
    try:
        import httpx
        payload = {"q": query, "num": max_results}
        headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                "https://google.serper.dev/search", json=payload, headers=headers
            )
            resp.raise_for_status()
            data = resp.json()
        return [
            {"title": r.get("title", ""), "url": r.get("link", ""),
             "content": r.get("snippet", ""), "source": "serper"}
            for r in data.get("organic", [])
        ]
    except Exception:
        return []


async def parallel_web_search(
    query: str,
    max_results: int = 8,
    engines: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Fan-out query to all configured engines in parallel.
    Returns deduplicated results (earliest engine wins on URL collision).

    Args:
        query:       Search query string.
        max_results: Maximum results per engine before dedup.
        engines:     Whitelist of engine names; None = all available.
    """
    all_engines = {
        "tavily":     _search_tavily,
        "brave":      _search_brave,
        "duckduckgo": _search_ddg,
        "exa":        _search_exa,
        "serper":     _search_serper,
    }
    selected = {k: v for k, v in all_engines.items()
                if engines is None or k in engines}

    tasks = [fn(query, max_results) for fn in selected.values()]
    batches: list[list[dict]] = await asyncio.gather(*tasks, return_exceptions=False)

    seen_urls: set[str] = set()
    merged: list[dict] = []
    for batch in batches:
        for item in batch:
            url = item.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                merged.append(item)

    return merged
