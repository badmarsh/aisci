#!/usr/bin/env python3
"""Read-only liveness probe for Scite + Consensus MCP routes.

This is the cron/health-check companion to the interactive
``scite_oauth_probe.py`` and ``consensus_oauth_probe.py``: it never opens a
browser, never requests new tokens, and never prints token values.

For each configured upstream (``scite``, ``consensus``):

1. Check whether a token is available.
   * Default sources, in order:
     - ``$SCITE_MCP_BEARER_TOKEN`` / ``$CONSENSUS_MCP_BEARER_TOKEN``
     - ``/tmp/scite_mcp_access_token`` / ``/tmp/consensus_mcp_access_token``
       (the paths referenced by the live ``extensions_config.json``)
   * If no token is found → report ``not_configured``.

2. POST a tiny MCP ``initialize`` request to the local proxy.
   * 200/2xx → ``ok``
   * 401/403 → ``token_expired``  (most common when ``/tmp`` was wiped on host
     reboot but ``extensions_config.json`` still references the file path)
   * Other non-2xx → ``upstream_error``
   * Connection error → ``proxy_unreachable``

Exit code:
  * ``0`` if every configured probe is ``ok``.
  * ``1`` if any probe is in a hard-failure state (``proxy_unreachable``,
    ``upstream_error``).
  * ``0`` if the only non-``ok`` states are ``not_configured`` /
    ``token_expired`` AND ``--strict`` is not set. Token absence is treated as
    a warning by default so the cron health check does not flap the moment
    ``/tmp`` is wiped.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import requests


PROBES: dict[str, dict[str, str]] = {
    "scite": {
        "url": "http://127.0.0.1:8095/scite/",
        "env_var": "SCITE_MCP_BEARER_TOKEN",
        "token_file": "/tmp/scite_mcp_access_token",
    },
    "consensus": {
        "url": "http://127.0.0.1:8095/consensus/",
        "env_var": "CONSENSUS_MCP_BEARER_TOKEN",
        "token_file": "/tmp/consensus_mcp_access_token",
    },
}


def _load_token(env_var: str, token_file: str) -> tuple[str | None, str]:
    """Return (token_or_None, source_label). Never logs the token itself."""
    env_val = os.environ.get(env_var, "").strip()
    if env_val:
        return env_val, f"env:{env_var}"
    path = Path(token_file)
    if path.exists():
        try:
            value = path.read_text(encoding="utf-8").strip()
        except OSError as exc:
            return None, f"file_read_error:{exc.strerror or 'io'}"
        if value:
            return value, f"file:{token_file}"
    return None, "missing"


def _probe(name: str, cfg: dict[str, str]) -> dict[str, Any]:
    token, source = _load_token(cfg["env_var"], cfg["token_file"])
    record: dict[str, Any] = {
        "name": name,
        "url": cfg["url"],
        "token_source": source,
    }
    if not token:
        record["status"] = "not_configured"
        record["detail"] = (
            f"no token in ${cfg['env_var']} or {cfg['token_file']}; "
            "complete OAuth flow with deployment/helper/"
            f"{name}_oauth_probe.py to populate"
        )
        return record

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "aisci-mcp-liveness", "version": "0.1"},
        },
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": "2025-03-26",
        "Authorization": f"Bearer {token}",
    }
    try:
        resp = requests.post(cfg["url"], headers=headers, json=payload, timeout=12)
    except requests.RequestException as exc:
        record["status"] = "proxy_unreachable"
        record["detail"] = f"{type(exc).__name__}: {exc}"[:200]
        return record

    record["http_status"] = resp.status_code
    if 200 <= resp.status_code < 300:
        record["status"] = "ok"
    elif resp.status_code in (401, 403):
        record["status"] = "token_expired"
        record["detail"] = "MCP returned auth error; rerun the OAuth probe"
    else:
        record["status"] = "upstream_error"
        record["detail"] = resp.text[:200].replace("\n", " ")
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--probe",
        action="append",
        choices=sorted(PROBES.keys()),
        help="Limit to specific probes; repeatable. Default: all.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat not_configured / token_expired as failures.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="text",
        help="Output format. text is default for human/cron readability.",
    )
    args = parser.parse_args()

    selected = args.probe or list(PROBES.keys())
    results = [_probe(name, PROBES[name]) for name in selected]

    if args.format == "json":
        print(json.dumps({"results": results}, indent=2))
    else:
        for r in results:
            tag = "PASS" if r["status"] == "ok" else "WARN" if r["status"] in (
                "not_configured", "token_expired"
            ) else "FAIL"
            line = f"  {tag:<4}  {r['name']:<10} status={r['status']}"
            if r.get("http_status") is not None:
                line += f" http={r['http_status']}"
            line += f" source={r['token_source']}"
            if r.get("detail"):
                line += f" detail={r['detail']}"
            print(line)

    hard_fail = any(r["status"] in ("proxy_unreachable", "upstream_error") for r in results)
    soft_fail = any(r["status"] in ("not_configured", "token_expired") for r in results)

    if hard_fail:
        return 1
    if args.strict and soft_fail:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
