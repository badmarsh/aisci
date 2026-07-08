"""
Quick-Win #1 - Parallel Multi-Engine Search  (hardened)
=======================================================
Fans out a query to Tavily, Brave, DuckDuckGo, Exa, and Serper simultaneously
using asyncio.gather, then merges and deduplicates results by URL.

Hardening vs. original:
- Input validation (`query`, `max_results`, `engines`) at the boundary.
- Per-engine timeout via `asyncio.wait_for` so one hung provider can't stall
  the whole fan-out.
- Bare `except Exception: return []` replaced with typed catches that log a
  concise reason and record it in the returned `engine_errors` map.
- `parallel_web_search` now returns a structured envelope
  `{"results": [...], "engine_errors": {engine: reason}}` so callers can
  distinguish "no results" from "all providers failed".
- Legacy callers that expect a bare list can use `parallel_web_search_list`.
"""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)

PER_ENGINE_TIMEOUT_S = 12.0
MAX_QUERY_CHARS = 2000
MAX_RESULTS_HARD_CAP = 50


class SearchInputError(ValueError):
    """Raised when the caller passes bad arguments to parallel_web_search."""


# --------------------------------------------------------------------------- #
# Engine adapters                                                             #
# --------------------------------------------------------------------------- #

async def _search_tavily(query: str, max_results: int) -> list[dict]:
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key:
        return []
    from tavily import AsyncTavilyClient  # type: ignore
    client = AsyncTavilyClient(api_key=api_key)
    resp = await client.search(query, max_results=max_results)
    return [
        {"title": r.get("title", ""), "url": r.get("url", ""),
         "content": r.get("content", ""), "source": "tavily"}
        for r in resp.get("results", [])
    ]


async def _search_brave(query: str, max_results: int) -> list[dict]:
    api_key = os.getenv("BRAVE_API_KEY", "")
    if not api_key:
        return []
    import httpx
    headers = {"Accept": "application/json", "X-Subscription-Token": api_key}
    params = {"q": query, "count": max_results}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers=headers, params=params,
        )
        resp.raise_for_status()
        data = resp.json()
    return [
        {"title": r.get("title", ""), "url": r.get("url", ""),
         "content": r.get("description", ""), "source": "brave"}
        for r in data.get("web", {}).get("results", [])
    ]


async def _search_ddg(query: str, max_results: int) -> list[dict]:
    from duckduckgo_search import AsyncDDGS  # type: ignore
    async with AsyncDDGS() as ddgs:
        results = await ddgs.atext(query, max_results=max_results)
    return [
        {"title": r.get("title", ""), "url": r.get("href", ""),
         "content": r.get("body", ""), "source": "duckduckgo"}
        for r in (results or [])
    ]


async def _search_exa(query: str, max_results: int) -> list[dict]:
    api_key = os.getenv("EXA_API_KEY", "")
    if not api_key:
        return []
    import httpx
    payload = {"query": query, "numResults": max_results, "contents": {"text": True}}
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=12) as client:
        resp = await client.post(
            "https://api.exa.ai/search", json=payload, headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()
    return [
        {"title": r.get("title", ""), "url": r.get("url", ""),
         "content": (r.get("text") or r.get("snippet", ""))[:800],
         "source": "exa"}
        for r in data.get("results", [])
    ]


async def _search_serper(query: str, max_results: int) -> list[dict]:
    api_key = os.getenv("SERPER_API_KEY", "")
    if not api_key:
        return []
    import httpx
    payload = {"q": query, "num": max_results}
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            "https://google.serper.dev/search", json=payload, headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()
    return [
        {"title": r.get("title", ""), "url": r.get("link", ""),
         "content": r.get("snippet", ""), "source": "serper"}
        for r in data.get("organic", [])
    ]


# --------------------------------------------------------------------------- #
# Orchestration                                                               #
# --------------------------------------------------------------------------- #

EngineFn = Callable[[str, int], Awaitable[list[dict]]]

ALL_ENGINES: dict[str, EngineFn] = {
    "tavily":     _search_tavily,
    "brave":      _search_brave,
    "duckduckgo": _search_ddg,
    "exa":        _search_exa,
    "serper":     _search_serper,
}


def _validate(query: str, max_results: int, engines: list[str] | None) -> None:
    if not isinstance(query, str) or not query.strip():
        raise SearchInputError("query must be a non-empty string")
    if len(query) > MAX_QUERY_CHARS:
        raise SearchInputError(
            f"query is too long ({len(query)} > {MAX_QUERY_CHARS})"
        )
    if not isinstance(max_results, int) or max_results < 1:
        raise SearchInputError("max_results must be a positive integer")
    if max_results > MAX_RESULTS_HARD_CAP:
        raise SearchInputError(
            f"max_results must be <= {MAX_RESULTS_HARD_CAP}"
        )
    if engines is not None:
        unknown = [e for e in engines if e not in ALL_ENGINES]
        if unknown:
            raise SearchInputError(
                f"unknown engines: {unknown}; allowed: {sorted(ALL_ENGINES)}"
            )


async def _run_one(name: str, fn: EngineFn, query: str, max_results: int
                   ) -> tuple[str, list[dict], str | None]:
    try:
        result = await asyncio.wait_for(
            fn(query, max_results), timeout=PER_ENGINE_TIMEOUT_S
        )
        return name, result, None
    except asyncio.TimeoutError:
        logger.warning("search engine %s timed out after %.1fs", name, PER_ENGINE_TIMEOUT_S)
        return name, [], "timeout"
    except ImportError as exc:
        logger.info("search engine %s unavailable: %s", name, exc)
        return name, [], "not_installed"
    except Exception as exc:  # noqa: BLE001 - engine-boundary catch-all
        logger.warning("search engine %s failed: %s: %s",
                       name, type(exc).__name__, exc)
        return name, [], f"{type(exc).__name__}: {exc}"[:200]


async def parallel_web_search(
    query: str,
    max_results: int = 8,
    engines: list[str] | None = None,
) -> dict[str, Any]:
    """Fan-out search. Returns `{"results": [...], "engine_errors": {...}}`."""
    _validate(query, max_results, engines)

    selected = {k: v for k, v in ALL_ENGINES.items()
                if engines is None or k in engines}

    tasks = [_run_one(name, fn, query, max_results) for name, fn in selected.items()]
    triples = await asyncio.gather(*tasks)

    seen: set[str] = set()
    merged: list[dict] = []
    errors: dict[str, str] = {}
    for name, batch, err in triples:
        if err is not None:
            errors[name] = err
            continue
        for item in batch:
            url = item.get("url", "")
            if url and url not in seen:
                seen.add(url)
                merged.append(item)

    if not merged and errors and len(errors) == len(selected):
        logger.error("parallel_web_search: all %d engines failed: %s",
                     len(selected), errors)

    return {"results": merged, "engine_errors": errors}


async def parallel_web_search_list(
    query: str,
    max_results: int = 8,
    engines: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Backwards-compatible variant that returns a bare list of results."""
    envelope = await parallel_web_search(query, max_results, engines)
    return envelope["results"]
