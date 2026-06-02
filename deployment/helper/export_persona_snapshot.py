#!/usr/bin/env python3
"""Export Onyx persona configurations as a reproducible JSON snapshot.

The Onyx admin UI is the canonical place to edit personas, but the underlying
config (system prompt, doc sets, tools, model binding, starter messages) is
non-trivial to rebuild after a stack reset. This helper dumps each persona
into a versioned JSON snapshot that can be diffed across days, audited for
drift, and used as input to a future ``configure_onyx.py``-style restore path.

Defaults:
* Pulls the science persona stack: ids 0, 2, 3, 5, 6, 8 (Assistant, plus
  physics-validator and the four science modes that were rebuilt on
  2026-05-30). Override with ``--persona-id``.
* Writes to ``deployment/onyx/snapshots/<date>/`` with one file per persona
  plus a top-level ``personas.json`` that aggregates the run.
* Email addresses inside ``owner`` are redacted by default
  (``--keep-emails`` to disable).
* The Onyx API key is never logged or written into the snapshot.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import requests


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BASE_URL = "http://localhost:3000"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "deployment" / "onyx" / "snapshots"
DEFAULT_ENV_FILE = REPO_ROOT / "deployment" / "onyx" / ".env"

DEFAULT_PERSONA_IDS: list[int] = [0, 2, 3, 5, 6]

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
TOKEN_LIKE_RE = re.compile(r"on_[A-Za-z0-9_-]{30,}|sk-[A-Za-z0-9_-]{20,}")


def load_api_key(env_file: Path) -> str:
    key = os.environ.get("ONYX_API_KEY", "").strip()
    if key:
        return key
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("ONYX_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("ONYX_API_KEY not in env and not in .env file")


def _redact_emails(value: Any) -> Any:
    if isinstance(value, str):
        # Don't touch starter-message text — only redact the persona-owner email.
        return EMAIL_RE.sub("<redacted-email>", value)
    if isinstance(value, list):
        return [_redact_emails(v) for v in value]
    if isinstance(value, dict):
        return {k: _redact_emails(v) for k, v in value.items()}
    return value


def _scrub_tokens(text: str) -> str:
    return TOKEN_LIKE_RE.sub("<redacted-token>", text)


def fetch_persona(base_url: str, headers: dict[str, str], persona_id: int) -> dict[str, Any] | None:
    try:
        resp = requests.get(f"{base_url}/api/persona/{persona_id}", headers=headers, timeout=15)
    except requests.RequestException as exc:
        return {"_error": f"{type(exc).__name__}: {exc}"}
    if resp.status_code == 404:
        return None
    if resp.status_code != 200:
        return {"_error": f"http_{resp.status_code}", "_body": resp.text[:300]}
    try:
        return resp.json()
    except json.JSONDecodeError:
        return {"_error": "non_json_response", "_body": resp.text[:300]}


def fetch_persona_index(base_url: str, headers: dict[str, str]) -> list[dict[str, Any]]:
    """Return a thin list of all personas the API surface exposes."""
    try:
        resp = requests.get(f"{base_url}/api/persona", headers=headers, timeout=20)
        resp.raise_for_status()
        listing = resp.json()
    except (requests.RequestException, json.JSONDecodeError):
        return []
    summary = []
    for p in listing:
        summary.append({
            "id": p.get("id"),
            "name": p.get("name"),
            "is_listed": p.get("is_listed"),
            "is_public": p.get("is_public"),
            "builtin_persona": p.get("builtin_persona"),
            "default_model_configuration_id": p.get("default_model_configuration_id"),
            "document_set_ids": [
                ds.get("id") for ds in (p.get("document_sets") or []) if isinstance(ds, dict)
            ],
            "tool_ids": [
                t.get("id") for t in (p.get("tools") or []) if isinstance(t, dict)
            ],
        })
    return summary


def normalize_persona(payload: dict[str, Any], *, redact_emails: bool) -> dict[str, Any]:
    """Strip non-portable / volatile fields and apply redactions."""
    if "_error" in payload:
        return payload
    keep = {
        "id",
        "name",
        "description",
        "is_public",
        "is_listed",
        "is_featured",
        "builtin_persona",
        "display_priority",
        "icon_name",
        "user_file_ids",
        "starter_messages",
        "tools",
        "labels",
        "owner",
        "users",
        "groups",
        "document_sets",
        "default_model_configuration_id",
        "hierarchy_nodes",
        "attached_documents",
        "system_prompt",
        "task_prompt",
        "replace_base_system_prompt",
        "datetime_aware",
        "search_start_date",
    }
    snapshot = {k: payload.get(k) for k in keep if k in payload}

    # Tool entries include large transient fields like in-cluster oauth_config_id;
    # keep the durable identity fields only.
    snapshot["tools"] = [
        {
            "id": t.get("id"),
            "name": t.get("name"),
            "in_code_tool_id": t.get("in_code_tool_id"),
            "mcp_server_id": t.get("mcp_server_id"),
            "display_name": t.get("display_name"),
            "enabled": t.get("enabled"),
            "chat_selectable": t.get("chat_selectable"),
            "default_enabled": t.get("default_enabled"),
        }
        for t in (snapshot.get("tools") or [])
        if isinstance(t, dict)
    ]
    snapshot["document_sets"] = [
        {
            "id": ds.get("id"),
            "name": ds.get("name"),
            "is_public": ds.get("is_public"),
        }
        for ds in (snapshot.get("document_sets") or [])
        if isinstance(ds, dict)
    ]

    if redact_emails:
        snapshot = _redact_emails(snapshot)
    return snapshot


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--persona-id",
        type=int,
        action="append",
        help="Repeatable. If omitted, dumps the default science stack ids.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Base directory; per-run snapshots land in <output-dir>/<UTC date>/",
    )
    parser.add_argument(
        "--env-file",
        default=str(DEFAULT_ENV_FILE),
        help="Fallback .env file to read ONYX_API_KEY from",
    )
    parser.add_argument(
        "--keep-emails",
        action="store_true",
        help="Don't redact email addresses (default: redact owner.email).",
    )
    parser.add_argument(
        "--print-paths",
        action="store_true",
        help="Print the path of each written file.",
    )
    args = parser.parse_args()

    api_key = load_api_key(Path(args.env_file))
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    persona_ids = sorted(set(args.persona_id or DEFAULT_PERSONA_IDS))
    today = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")
    run_dir = Path(args.output_dir) / today
    run_dir.mkdir(parents=True, exist_ok=True)

    listing = fetch_persona_index(args.base_url, headers)
    aggregate: dict[str, Any] = {
        "schema_version": 1,
        "ran_at_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "base_url": args.base_url,
        "redact_emails": not args.keep_emails,
        "persona_index": listing,
        "personas": {},
    }

    written: list[Path] = []
    for pid in persona_ids:
        raw = fetch_persona(args.base_url, headers, pid)
        if raw is None:
            aggregate["personas"][str(pid)] = {"_error": "not_found"}
            print(f"  persona {pid}: not found", file=sys.stderr)
            continue
        snapshot = normalize_persona(raw, redact_emails=not args.keep_emails)
        aggregate["personas"][str(pid)] = snapshot
        path = run_dir / f"persona-{pid:03d}.json"
        path.write_text(
            _scrub_tokens(json.dumps(snapshot, indent=2, ensure_ascii=False)) + "\n",
            encoding="utf-8",
        )
        written.append(path)
        if args.print_paths:
            print(f"  persona {pid} -> {path}")

    aggregate_path = run_dir / "personas.json"
    aggregate_path.write_text(
        _scrub_tokens(json.dumps(aggregate, indent=2, ensure_ascii=False)) + "\n",
        encoding="utf-8",
    )
    written.append(aggregate_path)

    print(f"\nWrote {len(written)} file(s) under {run_dir}")
    print(f"Persona ids dumped: {persona_ids}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
