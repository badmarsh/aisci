"""Persistent MCP session pool for stateful tool calls.

When MCP tools are loaded via langchain-mcp-adapters with session=None, each
tool call creates a new MCP session. Stateful stdio servers such as Playwright
then lose browser/page state between consecutive calls in the same thread.

This module keeps sessions scoped by (server_name, scope_key), where scope_key
is normally the LangGraph thread_id. Sessions are evicted in LRU order.
"""

from __future__ import annotations

import asyncio
import logging
import threading
from collections import OrderedDict
from typing import Any

from mcp import ClientSession

logger = logging.getLogger(__name__)


class PersistentSession:
    """A wrapper for a persistent MCP session managed via a background task
    to prevent anyio cancel scope issues when exiting the session from a different task.
    """

    def __init__(self, connection: dict[str, Any]) -> None:
        self.connection = connection
        self.session: ClientSession | None = None
        self.task: asyncio.Task | None = None
        self.session_ready = asyncio.Event()
        self.close_event = asyncio.Event()
        self.closed_event = asyncio.Event()
        self.exception: Exception | None = None

    def start(self) -> None:
        self.task = asyncio.create_task(self._run())

    async def _run(self) -> None:
        from langchain_mcp_adapters.sessions import create_session
        try:
            # We must enter create_session inside this background task
            async with create_session(self.connection) as session:
                self.session = session
                await session.initialize()
                self.session_ready.set()
                # Keep it open until close_event is set
                await self.close_event.wait()
        except Exception as e:
            self.exception = e
            logger.warning("Exception in persistent MCP session background task", exc_info=True)
        finally:
            self.session_ready.set()
            self.closed_event.set()

    async def get_session(self) -> ClientSession:
        await self.session_ready.wait()
        if self.exception is not None:
            raise self.exception
        if self.session is None:
            raise RuntimeError("MCP session failed to initialize without a recorded exception")
        return self.session

    async def close(self) -> None:
        self.close_event.set()
        if self.task:
            try:
                # Give it a short timeout to exit cleanly
                await asyncio.wait_for(self.closed_event.wait(), timeout=3.0)
            except asyncio.TimeoutError:
                logger.warning("Timeout waiting for persistent MCP session to close cleanly, cancelling task")
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass

    def close_sync(self, loop: asyncio.AbstractEventLoop) -> None:
        if loop.is_closed():
            return
        if loop.is_running():
            loop.call_soon_threadsafe(self.close_event.set)
        else:
            # Loop is not running, we can run until complete or let it be
            try:
                loop.run_until_complete(self.close())
            except Exception:
                pass


class MCPSessionPool:
    """Manage persistent MCP sessions scoped by server and thread."""

    MAX_SESSIONS = 256
    SESSION_CLOSE_TIMEOUT = 5.0

    def __init__(self) -> None:
        self._entries: OrderedDict[
            tuple[str, str],
            tuple[ClientSession, asyncio.AbstractEventLoop],
        ] = OrderedDict()
        self._persistent_sessions: dict[tuple[str, str], PersistentSession] = {}
        self._lock = threading.Lock()

    async def get_session(
        self,
        server_name: str,
        scope_key: str,
        connection: dict[str, Any],
    ) -> ClientSession:
        key = (server_name, scope_key)
        current_loop = asyncio.get_running_loop()
        sessions_to_close: list[PersistentSession] = []

        with self._lock:
            if key in self._entries:
                session, loop = self._entries[key]
                if loop is current_loop:
                    self._entries.move_to_end(key)
                    return session

                p_sess = self._persistent_sessions.pop(key, None)
                self._entries.pop(key)
                if p_sess is not None:
                    sessions_to_close.append(p_sess)

            while len(self._entries) >= self.MAX_SESSIONS:
                oldest_key = next(iter(self._entries))
                p_sess = self._persistent_sessions.pop(oldest_key, None)
                self._entries.pop(oldest_key)
                if p_sess is not None:
                    sessions_to_close.append(p_sess)

        for p_sess in sessions_to_close:
            try:
                await p_sess.close()
            except Exception:
                logger.warning("Error closing MCP session %s", key, exc_info=True)

        p_sess = PersistentSession(connection)
        p_sess.start()
        try:
            session = await p_sess.get_session()
        except Exception:
            await p_sess.close()
            raise

        with self._lock:
            self._entries[key] = (session, current_loop)
            self._persistent_sessions[key] = p_sess

        logger.info("Created persistent MCP session for %s/%s", server_name, scope_key)
        return session

    async def _close_session(self, p_sess: PersistentSession) -> None:
        try:
            await p_sess.close()
        except Exception:
            logger.warning("Error closing MCP session", exc_info=True)

    async def close_scope(self, scope_key: str) -> None:
        with self._lock:
            keys = [key for key in self._entries if key[1] == scope_key]
            p_sesses = [self._persistent_sessions.pop(key, None) for key in keys]
            for key in keys:
                self._entries.pop(key, None)

        for p_sess in p_sesses:
            if p_sess is not None:
                await self._close_session(p_sess)

    async def close_server(self, server_name: str) -> None:
        with self._lock:
            keys = [key for key in self._entries if key[0] == server_name]
            p_sesses = [self._persistent_sessions.pop(key, None) for key in keys]
            for key in keys:
                self._entries.pop(key, None)

        for p_sess in p_sesses:
            if p_sess is not None:
                await self._close_session(p_sess)

    async def close_all(self) -> None:
        with self._lock:
            p_sesses = list(self._persistent_sessions.values())
            self._persistent_sessions.clear()
            self._entries.clear()

        for p_sess in p_sesses:
            await self._close_session(p_sess)

    def close_all_sync(self) -> None:
        with self._lock:
            entries = list(self._entries.items())
            p_sesses = dict(self._persistent_sessions)
            self._persistent_sessions.clear()
            self._entries.clear()

        for key, (_, loop) in entries:
            p_sess = p_sesses.get(key)
            if p_sess is None:
                continue
            try:
                p_sess.close_sync(loop)
            except Exception:
                logger.debug("Error closing MCP session %s during sync close", key, exc_info=True)


_pool: MCPSessionPool | None = None
_pool_lock = threading.Lock()


def get_session_pool() -> MCPSessionPool:
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                _pool = MCPSessionPool()
    return _pool


def reset_session_pool() -> None:
    global _pool
    _pool = None
