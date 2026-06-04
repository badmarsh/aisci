"""Context7 Tool — fetch up-to-date library documentation via Streamable HTTP MCP server."""

import json
import logging
import os
import re
import subprocess
import threading
import time

from langchain.tools import tool

logger = logging.getLogger(__name__)

CONTEXT7_API_KEY = os.environ.get("CONTEXT7_API_KEY", "")
_CONTEXT7_PORT = 3456
_CONTEXT7_LOCK = threading.Lock()
_CONTEXT7_STARTED = False


def _find_context7_mcp() -> str:
    """Find the context7-mcp index.js file, installing it if needed."""
    import glob
    for base in ["/root/.npm/_npx"]:
        matches = sorted(glob.glob(f"{base}/*/node_modules/@upstash/context7-mcp/dist/index.js"))
        if matches:
            return matches[-1]  # Use latest
    # Not found — install via npx
    import subprocess
    subprocess.run(["npx", "-y", "@upstash/context7-mcp@latest", "--version"],
                   capture_output=True, timeout=60)
    # Retry find
    for base in ["/root/.npm/_npx"]:
        matches = sorted(glob.glob(f"{base}/*/node_modules/@upstash/context7-mcp/dist/index.js"))
        if matches:
            return matches[-1]
    raise RuntimeError("context7-mcp not found after npx install")


def _ensure_server():
    """Start the Context7 MCP server on Streamable HTTP if not already running."""
    global _CONTEXT7_STARTED
    if _CONTEXT7_STARTED:
        return

    with _CONTEXT7_LOCK:
        if _CONTEXT7_STARTED:
            return

        node_path = _find_context7_mcp()
        env = os.environ.copy()
        if CONTEXT7_API_KEY:
            env["CONTEXT7_API_KEY"] = CONTEXT7_API_KEY

        subprocess.Popen(
            ["node", node_path, "--transport", "http", "--port", str(_CONTEXT7_PORT)],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Wait for server to start
        import http.client
        for _ in range(20):
            time.sleep(0.5)
            try:
                conn = http.client.HTTPConnection("localhost", _CONTEXT7_PORT, timeout=2)
                conn.request("GET", "/mcp")
                resp = conn.getresponse()
                if resp.status in (200, 400, 405, 406):
                    _CONTEXT7_STARTED = True
                    return
            except Exception:
                continue

        raise RuntimeError(f"Context7 MCP server failed to start on port {_CONTEXT7_PORT}")


def _parse_sse_response(raw: str) -> dict:
    """Parse Server-Sent Events response into the last JSON data object."""
    # SSE format: "event: message\ndata: {...}\n\n"
    for line in raw.split("\n"):
        if line.startswith("data: "):
            try:
                return json.loads(line[6:])
            except json.JSONDecodeError:
                continue
    # Fallback: try to find JSON in the raw text
    for match in re.finditer(r"\{[^{}]*\}", raw):
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            continue
    raise ValueError(f"No valid JSON found in SSE response: {raw[:500]}")


def _mcp_call(method: str, params: dict) -> dict:
    """Call a Context7 MCP tool via Streamable HTTP transport."""
    import httpx

    _ensure_server()

    url = f"http://localhost:{_CONTEXT7_PORT}/mcp"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params,
    }
    resp = httpx.post(url, json=body, headers=headers, timeout=60)
    resp.raise_for_status()

    # Response may be SSE or plain JSON
    content_type = resp.headers.get("Content-Type", "")
    if "text/event-stream" in content_type:
        return _parse_sse_response(resp.text)
    return resp.json()


@tool("resolve_library", parse_docstring=True)
def context7_resolve_library_tool(
    library_name: str,
) -> str:
    """Resolve a library name to its Context7 ID and supported versions.
    Use this FIRST to find the exact library ID before fetching docs.

    Args:
        library_name: The name of the library or framework (e.g., "react", "pydantic", "langchain").
    """
    try:
        result = _mcp_call("tools/call", {
            "name": "resolve-library-id",
            "arguments": {"query": library_name, "libraryName": library_name},
        })
        content = result.get("result", {}).get("content", [])
        text = "\n".join(c.get("text", "") for c in content if c.get("type") == "text")
        return text if text else json.dumps({"error": "No results found", "library_name": library_name}, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Context7 resolve failed: {e}")
        return json.dumps({"error": str(e), "library_name": library_name}, ensure_ascii=False)


@tool("get_library_docs", parse_docstring=True)
def context7_get_library_docs_tool(
    library_id: str,
    topic: str | None = None,
) -> str:
    """Fetch up-to-date documentation for a library from Context7.
    Use resolve_library first to get the library_id. Returns markdown-formatted docs.

    Args:
        library_id: The Context7 library ID (e.g., "pydantic/pydantic" or "anthropic-ai/mcp-sdk-python").
        topic: Optional topic to narrow the documentation (e.g., "tools", "authentication").
    """
    try:
        params = {
            "libraryId": library_id,
            "query": topic or f"Get documentation for {library_id}",
        }
        result = _mcp_call("tools/call", {
            "name": "query-docs",
            "arguments": params,
        })
        content = result.get("result", {}).get("content", [])
        if not content:
            return json.dumps({"error": "No documentation found", "library_id": library_id}, ensure_ascii=False)
        return "\n".join(c.get("text", "") for c in content if c.get("type") == "text")
    except Exception as e:
        logger.error(f"Context7 docs failed: {e}")
        return json.dumps({"error": str(e), "library_id": library_id}, ensure_ascii=False)
