"""
ARQ Async Task Queue Worker for DeerFlow
=========================================
Runs long research tasks in the background so users can close the browser
without losing progress. Results are stored in Redis and can be polled
via the DeerFlow API.

Usage:
    # Start the worker (inside Docker or locally with Redis running):
    python -m deployment.deer_flow.tasks.arq_worker

    # Enqueue a research task from the DeerFlow backend:
    from deployment.deer_flow.tasks.arq_worker import enqueue_research
    job = await enqueue_research(redis, query="What is the Higgs mass?", run_id="abc123")

Environment:
    REDIS_URL   Redis connection URL (default: redis://localhost:6379/0)
"""

from __future__ import annotations

import logging
import os
from datetime import timedelta
from typing import Any

try:
    import arq
    from arq import create_pool
    from arq.connections import RedisSettings
except ImportError as e:
    raise ImportError(
        "arq is required for the async task queue. "
        "Install it with: pip install arq"
    ) from e

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Redis settings
# ---------------------------------------------------------------------------
_redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")


def _parse_redis_settings(url: str) -> RedisSettings:
    """Parse a redis:// URL into arq RedisSettings."""
    from urllib.parse import urlparse

    parsed = urlparse(url)
    return RedisSettings(
        host=parsed.hostname or "localhost",
        port=parsed.port or 6379,
        database=int(parsed.path.lstrip("/") or 0),
        password=parsed.password,
    )


REDIS_SETTINGS = _parse_redis_settings(_redis_url)


# ---------------------------------------------------------------------------
# Task definitions
# ---------------------------------------------------------------------------

async def run_research_task(ctx: dict[str, Any], *, run_id: str, query: str, config: dict | None = None) -> dict:
    """
    Background task: run a full DeerFlow research pipeline.

    Args:
        ctx:     ARQ worker context (contains redis connection, etc.)
        run_id:  Unique run identifier (matches DeerFlow run_id)
        query:   The research query string
        config:  Optional dict of DeerFlow config overrides

    Returns:
        dict with keys: run_id, status, report (str)
    """
    logger.info("[arq] Starting research task run_id=%s query=%r", run_id, query[:80])

    try:
        # Import here to avoid circular imports at module load time.
        # Replace this stub with the actual DeerFlow pipeline call.
        # Example:
        #   from deerflow.graph import run_research_graph
        #   result = await run_research_graph(query=query, config=config or {})

        # --- STUB: replace with real pipeline invocation ---
        result = {
            "run_id": run_id,
            "status": "completed",
            "report": f"[stub] Research complete for: {query}",
        }
        # ---------------------------------------------------

        logger.info("[arq] Completed research task run_id=%s", run_id)
        return result

    except Exception as exc:
        logger.exception("[arq] Research task failed run_id=%s: %s", run_id, exc)
        return {"run_id": run_id, "status": "failed", "error": str(exc)}


async def run_report_export(ctx: dict[str, Any], *, run_id: str, format: str = "pdf") -> dict:
    """
    Background task: export a completed report to PDF, DOCX, or Notion.

    Args:
        ctx:    ARQ worker context
        run_id: Existing run to export
        format: One of 'pdf', 'docx', 'notion'

    Returns:
        dict with keys: run_id, format, output_path or notion_url
    """
    logger.info("[arq] Starting report export run_id=%s format=%s", run_id, format)
    # TODO: implement PDF (Playwright headless), DOCX (python-docx), Notion (notion-client)
    return {"run_id": run_id, "format": format, "status": "not_implemented"}


async def run_vector_index(ctx: dict[str, Any], *, run_id: str, report_text: str) -> dict:
    """
    Background task: embed and index a completed research report into Chroma/Qdrant.

    Args:
        ctx:         ARQ worker context
        run_id:      Run whose report should be indexed
        report_text: Markdown text of the report

    Returns:
        dict with keys: run_id, indexed_chunks (int)
    """
    logger.info("[arq] Indexing report run_id=%s (%d chars)", run_id, len(report_text))
    # TODO: chunk report_text → embed with sentence-transformers → upsert to Chroma/Qdrant
    return {"run_id": run_id, "indexed_chunks": 0, "status": "not_implemented"}


# ---------------------------------------------------------------------------
# Startup / shutdown hooks
# ---------------------------------------------------------------------------

async def startup(ctx: dict[str, Any]) -> None:
    logger.info("[arq] Worker starting up")


async def shutdown(ctx: dict[str, Any]) -> None:
    logger.info("[arq] Worker shutting down")


# ---------------------------------------------------------------------------
# Worker settings
# ---------------------------------------------------------------------------

class WorkerSettings:
    """ARQ worker configuration."""

    functions = [
        run_research_task,
        run_report_export,
        run_vector_index,
    ]

    redis_settings = REDIS_SETTINGS
    on_startup = startup
    on_shutdown = shutdown

    # Retry failed tasks up to 3 times with exponential backoff
    max_tries = 3
    retry_delay = timedelta(seconds=5)

    # Keep job results in Redis for 24 h so the API can poll them
    keep_result = timedelta(hours=24)

    # Timeout per task (30 min to accommodate long research runs)
    job_timeout = timedelta(minutes=30)

    # Health check interval
    health_check_interval = timedelta(seconds=30)


# ---------------------------------------------------------------------------
# Convenience helper: enqueue from the DeerFlow API process
# ---------------------------------------------------------------------------

async def enqueue_research(
    redis_pool,
    *,
    run_id: str,
    query: str,
    config: dict | None = None,
) -> Any:
    """
    Enqueue a research task from the DeerFlow API.

    Example usage in a FastAPI endpoint::

        from arq import create_pool
        pool = await create_pool(REDIS_SETTINGS)
        job = await enqueue_research(pool, run_id=run_id, query=query)
        return {"job_id": job.job_id}
    """
    return await redis_pool.enqueue_job(
        "run_research_task",
        run_id=run_id,
        query=query,
        config=config,
        _job_id=run_id,  # use run_id as job ID for easy polling
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    arq.run_worker(WorkerSettings)  # type: ignore[attr-defined]
