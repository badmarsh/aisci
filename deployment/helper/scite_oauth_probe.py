#!/usr/bin/env python3
"""Interactive Scite MCP OAuth probe.

Generates a Scite OAuth URL, exchanges the returned authorization code for an
MCP access token, and verifies the local MCP proxy. Tokens are not printed
unless --print-token is explicitly passed.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import shutil
import subprocess
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from pathlib import Path
from typing import Any

import requests


SCITE_AUTH_BASE = "https://api.scite.ai"
SCITE_RESOURCE = "https://api.scite.ai/mcp"
SCITE_SCOPE = "mcp"
SCITE_MCP_PROXY = "http://127.0.0.1:8095/scite/"
REDIRECT_HOST = "127.0.0.1"
REDIRECT_PORT = 8766
REDIRECT_URI = f"http://{REDIRECT_HOST}:{REDIRECT_PORT}/callback"
DEFAULT_TRANSACTION_PATH = "/tmp/scite_oauth_transaction.json"


class CallbackState:
    def __init__(self) -> None:
        self.code: str | None = None
        self.error: str | None = None
        self.state: str | None = None


def _b64url_random(length: int = 32) -> str:
    return base64.urlsafe_b64encode(os.urandom(length)).decode().rstrip("=")


def _code_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")


def _register_client() -> str:
    payload = {
        "client_name": "aisci-scite-mcp",
        "redirect_uris": [REDIRECT_URI],
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
        "scope": SCITE_SCOPE,
        "token_endpoint_auth_method": "none",
    }
    response = requests.post(
        f"{SCITE_AUTH_BASE}/mcp/oauth/register",
        json=payload,
        timeout=20,
    )
    response.raise_for_status()
    client_id = response.json().get("client_id")
    if not client_id:
        raise RuntimeError("Scite OAuth registration did not return client_id")
    return client_id


def _start_callback_server(callback: CallbackState) -> HTTPServer:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - stdlib callback name.
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            callback.code = params.get("code", [None])[0]
            callback.error = params.get("error", [None])[0]
            callback.state = params.get("state", [None])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Scite OAuth callback received. You can return to the terminal.")

        def log_message(self, fmt: str, *args: Any) -> None:
            return

    server = HTTPServer((REDIRECT_HOST, REDIRECT_PORT), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def _exchange_code(client_id: str, code: str, verifier: str) -> dict[str, Any]:
    response = requests.post(
        f"{SCITE_AUTH_BASE}/mcp/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": client_id,
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "code_verifier": verifier,
            "resource": SCITE_RESOURCE,
        },
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    if not data.get("access_token"):
        raise RuntimeError("Scite token exchange did not return access_token")
    return data


def _build_authorization() -> tuple[str, dict[str, Any]]:
    client_id = _register_client()
    verifier = _b64url_random()
    challenge = _code_challenge(verifier)
    oauth_state = _b64url_random(16)
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "scope": SCITE_SCOPE,
        "state": oauth_state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "resource": SCITE_RESOURCE,
    }
    auth_url = f"{SCITE_AUTH_BASE}/mcp/oauth/authorize?" + urllib.parse.urlencode(params)
    transaction = {
        "client_id": client_id,
        "code_verifier": verifier,
        "state": oauth_state,
        "redirect_uri": REDIRECT_URI,
        "resource": SCITE_RESOURCE,
        "created_at": int(time.time()),
    }
    return auth_url, transaction


def _write_private_json(path: str, data: dict[str, Any]) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    output_path.chmod(0o600)
    return output_path


def _parse_redirect_url(redirect_url: str) -> tuple[str | None, str | None, str | None]:
    parsed = urllib.parse.urlparse(redirect_url.strip())
    params = urllib.parse.parse_qs(parsed.query)
    return (
        params.get("code", [None])[0],
        params.get("state", [None])[0],
        params.get("error", [None])[0],
    )


def _test_mcp(access_token: str) -> tuple[int, str]:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": "2025-03-26",
        "Authorization": f"Bearer {access_token}",
    }
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "aisci-scite-probe", "version": "0.1"},
        },
    }
    response = requests.post(SCITE_MCP_PROXY, headers=headers, json=payload, timeout=20)
    return response.status_code, response.text[:500].replace("\n", " ")


def _finish_token_flow(
    client_id: str,
    code: str,
    verifier: str,
    token_output: str | None,
    print_token: bool,
) -> int:
    token_data = _exchange_code(client_id, code, verifier)
    access_token = token_data["access_token"]
    status, body = _test_mcp(access_token)

    print(json.dumps({
        "access_token_obtained": True,
        "expires_in": token_data.get("expires_in"),
        "mcp_initialize_status": status,
        "mcp_initialize_body_preview": body,
    }, indent=2))

    if token_output:
        token_path = Path(token_output).expanduser().resolve()
        token_path.write_text(access_token, encoding="utf-8")
        token_path.chmod(0o600)
        print(f"Token written to {token_path}")
    if print_token:
        print(access_token)

    return 0 if 200 <= status < 300 else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=180, help="Seconds to wait for browser approval")
    parser.add_argument("--print-token", action="store_true", help="Print the MCP access token")
    parser.add_argument(
        "--system-browser",
        action="store_true",
        help="Open OAuth URL in normal Chrome/xdg-open and wait for localhost callback",
    )
    parser.add_argument(
        "--token-output",
        help="Optional non-repo path to write the MCP access token with chmod 600",
    )
    parser.add_argument(
        "--manual-start",
        action="store_true",
        help="Print an OAuth URL and save transaction state for manual browser completion",
    )
    parser.add_argument(
        "--transaction-output",
        default=DEFAULT_TRANSACTION_PATH,
        help="Path for --manual-start transaction state",
    )
    parser.add_argument(
        "--manual-exchange",
        action="store_true",
        help="Exchange a manually captured redirect URL for an MCP access token",
    )
    parser.add_argument(
        "--transaction",
        default=DEFAULT_TRANSACTION_PATH,
        help="Transaction state path for --manual-exchange",
    )
    parser.add_argument(
        "--redirect-url-file",
        help="File containing the full callback URL after browser approval",
    )
    args = parser.parse_args()

    if args.manual_start and args.manual_exchange:
        raise ValueError("--manual-start and --manual-exchange are mutually exclusive")

    if args.manual_start:
        auth_url, transaction = _build_authorization()
        transaction_path = _write_private_json(args.transaction_output, transaction)
        print(json.dumps({
            "authorization_url": auth_url,
            "transaction_path": str(transaction_path),
            "redirect_capture": "After approval, save the full failed callback URL to a local file and run --manual-exchange with --redirect-url-file.",
        }, indent=2))
        return 0

    if args.manual_exchange:
        if not args.redirect_url_file:
            raise ValueError("--manual-exchange requires --redirect-url-file")
        transaction = json.loads(Path(args.transaction).expanduser().read_text(encoding="utf-8"))
        redirect_url = Path(args.redirect_url_file).expanduser().read_text(encoding="utf-8").strip()
        code, callback_state, callback_error = _parse_redirect_url(redirect_url)
        if callback_error:
            raise RuntimeError(f"OAuth callback error: {callback_error}")
        if not code:
            raise RuntimeError("Redirect URL did not contain a code parameter")
        if callback_state != transaction.get("state"):
            raise RuntimeError("OAuth state mismatch")
        return _finish_token_flow(
            transaction["client_id"],
            code,
            transaction["code_verifier"],
            args.token_output,
            args.print_token,
        )

    auth_url, transaction = _build_authorization()
    callback = CallbackState()
    server = _start_callback_server(callback)
    print("Opening Scite OAuth consent in a system browser.", flush=True)
    print("Sign in and approve access if prompted. Token values will not be printed.", flush=True)

    try:
        opener = shutil.which("google-chrome") or shutil.which("xdg-open")
        if not opener:
            raise RuntimeError("No google-chrome or xdg-open command found")
        subprocess.Popen([opener, auth_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + args.timeout
        while time.monotonic() < deadline and not callback.code and not callback.error:
            time.sleep(0.5)
    finally:
        server.shutdown()

    if callback.error:
        raise RuntimeError(f"OAuth callback error: {callback.error}")
    if not callback.code:
        raise TimeoutError("Timed out waiting for Scite OAuth approval")
    if callback.state != transaction["state"]:
        raise RuntimeError("OAuth state mismatch")

    return _finish_token_flow(
        transaction["client_id"],
        callback.code,
        transaction["code_verifier"],
        args.token_output,
        args.print_token,
    )


if __name__ == "__main__":
    raise SystemExit(main())
