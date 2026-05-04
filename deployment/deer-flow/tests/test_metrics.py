"""
Unit tests for Prometheus metrics stubs.
Ensures no-op stubs don't raise when PROMETHEUS_ENABLED is false.
"""

import os

import pytest


class TestMetricsNoOp:
    """All operations should be silent no-ops when Prometheus is disabled."""

    def setup_method(self):
        os.environ.pop("PROMETHEUS_ENABLED", None)

    def test_counter_inc_does_not_raise(self):
        from deployment.deer_flow.metrics import RESEARCH_REQUESTS_TOTAL

        RESEARCH_REQUESTS_TOTAL.labels(status="started").inc()

    def test_gauge_set_does_not_raise(self):
        from deployment.deer_flow.metrics import ACTIVE_RESEARCH_TASKS

        ACTIVE_RESEARCH_TASKS.set(5)

    def test_histogram_observe_does_not_raise(self):
        from deployment.deer_flow.metrics import RESEARCH_DURATION_SECONDS

        RESEARCH_DURATION_SECONDS.observe(42.0)

    def test_track_research_task_context_manager(self):
        from deployment.deer_flow.metrics import track_research_task

        with track_research_task():
            pass  # should not raise

    def test_track_research_task_records_failure(self):
        from deployment.deer_flow.metrics import track_research_task

        with pytest.raises(ValueError):
            with track_research_task():
                raise ValueError("intentional")
