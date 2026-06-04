from contextlib import asynccontextmanager, contextmanager
from types import SimpleNamespace
from unittest.mock import patch

import pytest


class TestAsyncStoreDatabaseFallback:
    @pytest.mark.anyio
    async def test_make_store_uses_database_sqlite_when_checkpointer_missing(self):
        from deerflow.runtime.store.async_provider import make_store

        mock_config = SimpleNamespace(
            checkpointer=None,
            database=SimpleNamespace(
                backend="sqlite",
                checkpointer_sqlite_path="/tmp/deerflow.db",
                postgres_url="",
            ),
        )

        @asynccontextmanager
        async def fake_async_store(config):
            assert config.type == "sqlite"
            assert config.connection_string == "/tmp/deerflow.db"
            yield "sqlite-store"

        with patch("deerflow.runtime.store.async_provider.get_app_config", return_value=mock_config):
            with patch("deerflow.runtime.store.async_provider._async_store", fake_async_store):
                async with make_store() as store:
                    assert store == "sqlite-store"


class TestSyncStoreDatabaseFallback:
    def test_get_store_uses_database_sqlite_when_checkpointer_missing(self):
        from deerflow.runtime.store import provider

        mock_config = SimpleNamespace(
            checkpointer=None,
            database=SimpleNamespace(
                backend="sqlite",
                checkpointer_sqlite_path="/tmp/deerflow.db",
                postgres_url="",
            ),
        )

        @contextmanager
        def fake_sync_store(config):
            assert config.type == "sqlite"
            assert config.connection_string.endswith("/deerflow.db")
            yield "sqlite-store"

        provider.reset_store()
        try:
            with patch("deerflow.runtime.store.provider.get_app_config", return_value=mock_config):
                with patch("deerflow.runtime.store.provider._sync_store_cm", fake_sync_store):
                    assert provider.get_store() == "sqlite-store"
        finally:
            provider.reset_store()

    def test_store_context_uses_database_sqlite_when_checkpointer_missing(self):
        from deerflow.runtime.store.provider import store_context

        mock_config = SimpleNamespace(
            checkpointer=None,
            database=SimpleNamespace(
                backend="sqlite",
                checkpointer_sqlite_path="/tmp/deerflow.db",
                postgres_url="",
            ),
        )

        @contextmanager
        def fake_sync_store(config):
            assert config.type == "sqlite"
            assert config.connection_string.endswith("/deerflow.db")
            yield "sqlite-store"

        with patch("deerflow.runtime.store.provider.get_app_config", return_value=mock_config):
            with patch("deerflow.runtime.store.provider._sync_store_cm", fake_sync_store):
                with store_context() as store:
                    assert store == "sqlite-store"
