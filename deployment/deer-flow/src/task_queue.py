"""
Quick-Win #5 - ARQ Async Task Queue
=====================================
Background Redis workers for long research runs.
Users can close the browser without losing progress.

Usage:
    # Enqueue from API handler:
    from src.task_queue import enqueue_research
    job_id = await enqueue_research(run_id="abc", query="...", config={})

    # Check status:
    from src.task_queue import get_job_status
    status = await get_job_status(job_id)

Start worker:
    python -m src.task_queue worker
"""
from __future__ import annotations

import os
import sys
from typing import Any

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
ARQ_MAX_JOBS = int(os.getenv("ARQ_MAX_JOBS", "10"))
ARQ_JOB_TIMEOUT = int(os.getenv("ARQ_JOB_TIMEOUT", "3600"))
TASK_QUEUE_ENABLED = os.getenv("TASK_QUEUE_ENABLED", "false").lower() == "true"


async def run_research_task(
    ctx: dict,
    run_id: str,
    query: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    """
    Background task: execute a full DeerFlow research run.
    HTTP request returns immediately with a job_id; work continues here.
    """
    import logging
    logger = logging.getLogger("arq.research")
    logger.info("[arq] Starting run %s: %s", run_id, query[:80])
    try:
        from deerflow.graph import run_agent_graph  # type: ignore
        result = await run_agent_graph(run_id=run_id, query=query, config=config)
        logger.info("[arq] Completed run %s", run_id)
        return {"run_id": run_id, "status": "completed", "result": result}
    except Exception as exc:
        logger.exception("[arq] Run %s failed: %s", run_id, exc)
        return {"run_id": run_id, "status": "failed", "error": str(exc)}


class WorkerSettings:
    functions = [run_research_task]
    # BUGFIX: ARQ expects `redis_settings`, not `redis_settings_from_dsn`.
    # The previous attribute name was ignored, so the worker connected to the
    # default localhost:6379 regardless of REDIS_URL, and workers configured
    # for hosted Redis silently failed to start.
    try:
        import arq as _arq  # type: ignore
        redis_settings = _arq.connections.RedisSettings.from_dsn(REDIS_URL)
    except Exception:  # arq not installed at import time
        redis_settings = None
    max_jobs = ARQ_MAX_JOBS
    job_timeout = ARQ_JOB_TIMEOUT
    keep_result = 86400  # 24 h
    retry_jobs = True
    max_tries = 3


async def enqueue_research(
    run_id: str,
    query: str,
    config: dict[str, Any] | None = None,
) -> str | None:
    """Enqueue a research job. Returns job_id, or None if queue disabled."""
    if not TASK_QUEUE_ENABLED:
        return None
    import logging
    logger = logging.getLogger(__name__)
    try:
        import arq  # type: ignore
        redis = await arq.create_pool(
            arq.connections.RedisSettings.from_dsn(REDIS_URL)
        )
        try:
            job = await redis.enqueue_job(
                "run_research_task",
                run_id=run_id,
                query=query,
                config=config or {},
            )
        finally:
            await redis.close()
        return job.job_id if job else None
    except Exception as exc:
        # BUGFIX: previously returned None on any failure, indistinguishable
        # from `TASK_QUEUE_ENABLED=false`. Log it so ops can see queue outages.
        logger.exception("enqueue_research failed for run_id=%s: %s", run_id, exc)
        raise


async def get_job_status(job_id: str) -> dict[str, Any]:
    """Return status/result for a previously enqueued job."""
    if not TASK_QUEUE_ENABLED:
        return {"status": "disabled"}
    try:
        import arq  # type: ignore
        redis = await arq.create_pool(
            arq.connections.RedisSettings.from_dsn(REDIS_URL)
        )
        job = arq.jobs.Job(job_id, redis)
        info = await job.info()
        await redis.close()
        if info is None:
            return {"status": "not_found"}
        return {
            "job_id": job_id,
            "status": info.status.value if info.status else "unknown",
            "result": info.result,
            "enqueue_time": str(info.enqueue_time),
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "worker":
    import arq  # type: ignore
    arq.run_worker(WorkerSettings)
