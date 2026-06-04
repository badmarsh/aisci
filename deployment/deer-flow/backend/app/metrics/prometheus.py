"""
DeerFlow Prometheus Metrics
============================
Instruments key operational metrics so Prometheus can scrape and Grafana
can visualise research pipeline health.

Usage
-----
1. Install prometheus-client::

       pip install prometheus-client

2. Mount the metrics endpoint in your FastAPI app::

       from deployment.deer_flow.metrics.prometheus import init_metrics, metrics_app
       app.mount("/metrics", metrics_app)

3. Or expose a separate port (see WorkerSettings below)::

       from deployment.deer_flow.metrics.prometheus import start_http_server
       start_http_server(port=9091)  # call once at startup

4. Point prometheus.yml scrape_configs at the /metrics endpoint.
"""

from __future__ import annotations

import logging
import os
import time
from contextlib import contextmanager
from functools import wraps
from typing import Callable

logger = logging.getLogger(__name__)

try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        Counter,
        Gauge,
        Histogram,
        Summary,
        generate_latest,
        make_asgi_app,
        start_http_server as _start_http_server,
    )
    _PROMETHEUS_AVAILABLE = True
except ImportError:
    _PROMETHEUS_AVAILABLE = False
    logger.warning(
        "prometheus_client not installed — metrics are no-ops. "
        "Install with: pip install prometheus-client"
    )

_ENABLED = os.getenv("PROMETHEUS_ENABLED", "false").lower() == "true"


# ---------------------------------------------------------------------------
# Metric definitions
# ---------------------------------------------------------------------------

if _PROMETHEUS_AVAILABLE and _ENABLED:
    # Research pipeline
    RESEARCH_REQUESTS_TOTAL = Counter(
        "deerflow_research_requests_total",
        "Total number of research requests initiated",
        ["status"],  # labels: started, completed, failed
    )
    RESEARCH_DURATION_SECONDS = Histogram(
        "deerflow_research_duration_seconds",
        "End-to-end research task duration in seconds",
        buckets=[10, 30, 60, 120, 300, 600, 900, 1800],
    )
    ACTIVE_RESEARCH_TASKS = Gauge(
        "deerflow_active_research_tasks",
        "Number of research tasks currently running",
    )

    # LLM usage
    LLM_TOKENS_TOTAL = Counter(
        "deerflow_llm_tokens_total",
        "Total LLM tokens consumed",
        ["model", "direction"],  # direction: input, output
    )
    LLM_REQUESTS_TOTAL = Counter(
        "deerflow_llm_requests_total",
        "Total LLM API calls made",
        ["model", "status"],  # status: success, error, rate_limited
    )
    LLM_LATENCY_SECONDS = Histogram(
        "deerflow_llm_latency_seconds",
        "LLM API call latency",
        ["model"],
        buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60],
    )

    # Tool calls
    TOOL_CALLS_TOTAL = Counter(
        "deerflow_tool_calls_total",
        "Total tool invocations",
        ["tool_name", "status"],
    )

    # Search
    SEARCH_REQUESTS_TOTAL = Counter(
        "deerflow_search_requests_total",
        "Total search API calls",
        ["engine", "status"],  # engine: tavily, brave, ddg, exa
    )

    # MCP
    MCP_CALLS_TOTAL = Counter(
        "deerflow_mcp_calls_total",
        "Total MCP server invocations",
        ["server", "status"],
    )

    # Guardrails
    GUARDRAIL_VERDICTS_TOTAL = Counter(
        "deerflow_guardrail_verdicts_total",
        "Guardrail check outcomes",
        ["verdict"],  # allow, block, warn
    )

    # ARQ queue
    ARQ_QUEUE_DEPTH = Gauge(
        "deerflow_arq_queue_depth",
        "Number of pending ARQ tasks",
    )

else:
    # Provide no-op stubs so the rest of the codebase can import without guards
    class _Noop:
        def labels(self, **_):    return self
        def inc(self, *_, **__):  return None
        def dec(self, *_, **__):  return None
        def observe(self, *_):    return None
        def set(self, *_):        return None
        def time(self):           return _NoopCtx()

    class _NoopCtx:
        def __enter__(self): return self
        def __exit__(self, *_): pass

    _noop = _Noop()
    RESEARCH_REQUESTS_TOTAL = _noop
    RESEARCH_DURATION_SECONDS = _noop
    ACTIVE_RESEARCH_TASKS = _noop
    LLM_TOKENS_TOTAL = _noop
    LLM_REQUESTS_TOTAL = _noop
    LLM_LATENCY_SECONDS = _noop
    TOOL_CALLS_TOTAL = _noop
    SEARCH_REQUESTS_TOTAL = _noop
    MCP_CALLS_TOTAL = _noop
    GUARDRAIL_VERDICTS_TOTAL = _noop
    ARQ_QUEUE_DEPTH = _noop


# ---------------------------------------------------------------------------
# ASGI app for mounting on FastAPI
# ---------------------------------------------------------------------------

def metrics_app():
    """Return a Prometheus ASGI app to mount at /metrics."""
    if _PROMETHEUS_AVAILABLE and _ENABLED:
        return make_asgi_app()
    async def _disabled_app(scope, receive, send):
        await send({"type": "http.response.start", "status": 503, "headers": []})
        await send({"type": "http.response.body", "body": b"Prometheus not enabled"})
    return _disabled_app


def start_http_server(port: int | None = None) -> None:
    """Start a standalone Prometheus HTTP server on the given port."""
    if not _PROMETHEUS_AVAILABLE or not _ENABLED:
        return
    port = port or int(os.getenv("PROMETHEUS_PORT", "9091"))
    _start_http_server(port)
    logger.info("[metrics] Prometheus metrics server started on port %d", port)


# ---------------------------------------------------------------------------
# Convenience decorators / context managers
# ---------------------------------------------------------------------------

@contextmanager
def track_research_task():
    """Context manager that tracks active research tasks and duration."""
    RESEARCH_REQUESTS_TOTAL.labels(status="started").inc()
    ACTIVE_RESEARCH_TASKS.inc()
    start = time.perf_counter()
    try:
        yield
        RESEARCH_REQUESTS_TOTAL.labels(status="completed").inc()
    except Exception:
        RESEARCH_REQUESTS_TOTAL.labels(status="failed").inc()
        raise
    finally:
        ACTIVE_RESEARCH_TASKS.dec()
        RESEARCH_DURATION_SECONDS.observe(time.perf_counter() - start)


def track_llm_call(model: str):
    """Decorator that tracks LLM call latency and status."""
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = await fn(*args, **kwargs)
                LLM_REQUESTS_TOTAL.labels(model=model, status="success").inc()
                return result
            except Exception as exc:
                status = "rate_limited" if "rate" in str(exc).lower() else "error"
                LLM_REQUESTS_TOTAL.labels(model=model, status=status).inc()
                raise
            finally:
                LLM_LATENCY_SECONDS.labels(model=model).observe(time.perf_counter() - start)
        return wrapper
    return decorator
