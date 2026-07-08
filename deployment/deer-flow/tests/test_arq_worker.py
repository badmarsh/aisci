"""
Unit tests for the ARQ async task worker.
"""

import pytest


class TestWorkerSettings:
    def test_worker_has_expected_functions(self):
        from deployment.deer_flow.tasks.arq_worker import WorkerSettings

        fn_names = {f.__name__ for f in WorkerSettings.functions}
        assert "run_research_task" in fn_names
        assert "run_report_export" in fn_names
        assert "run_vector_index" in fn_names

    def test_redis_settings_default_host(self):
        from deployment.deer_flow.tasks.arq_worker import REDIS_SETTINGS

        assert REDIS_SETTINGS.host in ("localhost", "redis")
        assert REDIS_SETTINGS.port == 6379


class TestRunResearchTaskStub:
    @pytest.mark.asyncio
    async def test_stub_returns_completed_status(self):
        from deployment.deer_flow.tasks.arq_worker import run_research_task

        result = await run_research_task(
            ctx={},
            run_id="test-001",
            query="What is the speed of light?",
        )
        assert result["run_id"] == "test-001"
        assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_stub_returns_run_id_on_failure(self):
        from deployment.deer_flow.tasks.arq_worker import run_research_task

        # Simulate a future failure (the stub always succeeds, so we just
        # check the contract of the return dict for the error path)
        result = await run_research_task(
            ctx={},
            run_id="test-fail",
            query="What is the Higgs boson mass?",
        )
        assert "run_id" in result
        assert "status" in result
