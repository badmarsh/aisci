"""
Quick-Win #4 - Deep Think / Extended Reasoning
===============================================
Inserts a chain-of-thought reasoning block before the planning phase.
Enabled globally via DEEP_THINK_ENABLED=true or per-request via API payload.

Usage:
    from src.deep_think import maybe_deep_think
    thinking = await maybe_deep_think(query=user_query, llm=llm)
    # Returns structured reasoning string, or empty string if disabled.
"""
from __future__ import annotations

import os
from typing import Any

DEEP_THINK_ENABLED = os.getenv("DEEP_THINK_ENABLED", "false").lower() == "true"

DEEP_THINK_SYSTEM = (
    "You are an expert research strategist. "
    "Before any search or planning begins, reason carefully through the query.\n\n"
    "Output structure:\n"
    "1. What is truly being asked (decompose ambiguous phrasing)\n"
    "2. Key sub-questions that must be answered\n"
    "3. Potential dead-end research paths to avoid\n"
    "4. Optimal research sequence (which subtopic first, why)\n"
    "5. Domain-specific knowledge that should inform the plan\n\n"
    "Be concise but thorough."
)


async def maybe_deep_think(
    query: str,
    llm: Any,
    force: bool = False,
    extra_context: str = "",
) -> str:
    """
    Run a deep-think reasoning pass if enabled.

    Returns a <deep_think>...</deep_think> block to prepend
    to the planner context, or empty string if disabled.
    """
    if not (DEEP_THINK_ENABLED or force):
        return ""

    from langchain_core.messages import HumanMessage, SystemMessage  # type: ignore

    messages = [
        SystemMessage(content=DEEP_THINK_SYSTEM),
        HumanMessage(content=f"Query: {query}\n\n{extra_context}".strip()),
    ]
    try:
        response = await llm.ainvoke(messages)
        thinking = response.content if hasattr(response, "content") else str(response)
        return f"<deep_think>\n{thinking}\n</deep_think>"
    except Exception as exc:
        # BUGFIX: was silently swallowing every LLM failure with no signal;
        # planner ran without deep-think and nobody knew why. Log and degrade.
        import logging
        logging.getLogger(__name__).warning(
            "deep_think failed (%s: %s); continuing without it",
            type(exc).__name__, exc,
        )
        return ""


def deep_think_sync(query: str, llm: Any, force: bool = False) -> str:
    """Synchronous variant for non-async call sites."""
    import asyncio
    # BUGFIX: the previous implementation created a NEW event loop and called
    # run_until_complete on it. When invoked from inside an already-running
    # loop (very common in FastAPI/LangGraph code) that raises
    # "RuntimeError: This event loop is already running" and blows up the
    # request. Detect a running loop and offload to a worker thread instead.
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(maybe_deep_think(query, llm, force=force))
    # Already inside an event loop — cannot nest run_until_complete.
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(
            lambda: asyncio.run(maybe_deep_think(query, llm, force=force))
        ).result()
