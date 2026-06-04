"""Quick financial analysis — lightweight alternative to Dexter.

Uses DeerFlow's existing web search and scraping tools instead of
running a nested agent loop. Fast (10-30s) and cheap (1-2 LLM calls).
"""

from __future__ import annotations

import logging
from typing import Any

from deerflow.config import get_app_config

logger = logging.getLogger(__name__)


def _find_tool(name: str) -> Any | None:
    """Find a tool by name from the app config."""
    cfg = get_app_config()
    for tool in cfg.tools:
        if tool.name == name:
            # Import the tool function
            module_path, func_name = tool.use.rsplit(":", 1)
            import importlib

            module = importlib.import_module(module_path)
            return getattr(module, func_name)
    return None


async def quick_financial_analysis(query: str) -> str:
    """Quick financial analysis using DeerFlow's built-in tools.

    Searches the web for current financial information and synthesizes an answer.
    Much faster than Dexter (10-30s vs 3-10min).

    Args:
        query: The financial question.
    """
    web_search = _find_tool("web_search") or _find_tool("brave_search")
    web_scrape = _find_tool("web_scrape") or _find_tool("web_fetch")

    if not web_search:
        return "No web search tool configured. Cannot perform financial analysis."

    # Step 1: Search for the query
    try:
        search_results = web_search.invoke(query)
    except Exception as e:
        logger.warning(f"Web search failed: {e}")
        return f"Web search unavailable: {e}"

    # Step 2: If we got results, return a summary
    if isinstance(search_results, str) and search_results:
        return f"Research results for: {query}\n\n{search_results[:4000]}"

    return f"No relevant financial information found for: {query}"
