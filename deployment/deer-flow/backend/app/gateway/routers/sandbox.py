"""Sandbox info endpoint — exposes the current thread's sandbox URL to the agent."""

import logging

from fastapi import APIRouter, HTTPException, Query, Request

from deerflow.sandbox.sandbox_provider import get_sandbox_provider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sandbox", tags=["sandbox"])


@router.get("/info")
async def get_sandbox_info(
    request: Request,
    thread_id: str = Query(None),
):
    """Return the sandbox URL for the current thread's sandbox.

    The agent can call this from inside the sandbox via bash:
    ```
    curl -s http://localhost:8001/api/sandbox/info?thread_id=<id>
    ```
    to discover the sandbox URL needed for artifact preview iframes.

    Args:
        request: The FastAPI request object (injected automatically).
        thread_id: The thread ID to look up sandbox info for.

    Returns:
        JSON with sandbox_url, sandbox_id, and optional container_name.
    """
    if not thread_id:
        # Try to extract from x-thread-id header
        thread_id = request.headers.get("x-thread-id")

    if not thread_id:
        raise HTTPException(
            status_code=400,
            detail="thread_id is required. Pass it as ?thread_id=<id> or in x-thread-id header.",
        )

    try:
        provider = get_sandbox_provider()
        # Look up the sandbox by thread_id in the known sandbox registry
        info = provider._sandbox_infos.get(thread_id)

        if info is None:
            # Sandbox hasn't been created for this thread yet
            raise HTTPException(
                status_code=404,
                detail="No sandbox has been created for this thread yet. A sandbox is created on first tool call.",
            )

        return {
            "sandbox_id": info.sandbox_id,
            "sandbox_url": info.sandbox_url,
            "container_name": info.container_name,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get sandbox info for thread {thread_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
