#!/usr/bin/env python3
"""Regenerate ``deployment/deer-flow/extensions_config.example.json``
from the live (gitignored) ``extensions_config.json``.

The live file is the source of truth for which MCP servers DeerFlow is
actually wired up to. The ``.example.json`` next to it is the tracked
reference. They drift constantly because:

* The live file gets new entries (e.g. ``playwright`` was added in May 2026).
* Tokens get baked in: ``"GITHUB_TOKEN": "ghp_XXXXXXXXX"`` instead of
  ``"$GITHUB_TOKEN"``; ``Bearer $file:/tmp/scite_mcp_access_token`` references
  paths that don't survive container restarts.
* Field shapes diverge: the live writer adds ``"url": null, "headers": {},
  "oauth": null`` keys to every entry, while the example doesn't carry them.

What this helper does:

1. Read the live file.
2. Re-abstract any secret-shaped values back to ``$ENV_VAR`` form using
   the rules in ``SECRET_REWRITES`` below.
3. Convert ``Bearer $file:/tmp/<thing>_mcp_access_token`` to ``Bearer
   $<UPPER>_MCP_BEARER_TOKEN`` so the example stops referencing
   non-portable host paths.
4. Strip null/empty placeholder fields the live writer adds for entries
   that don't use them (``url=null`` on a stdio server, etc.) — the
   example stays human-readable.
5. Write the result to ``extensions_config.example.json``.

Run:

    python3 deployment/helper/regenerate_extensions_config_example.py

Pass ``--check`` to compare without writing — non-zero exit means the
example is stale.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_PATH = REPO_ROOT / "deployment" / "deer-flow" / "extensions_config.json"
EXAMPLE_PATH = REPO_ROOT / "deployment" / "deer-flow" / "extensions_config.example.json"


# Pattern → ENV var. Matched against env values inside each MCP entry.
SECRET_REWRITES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^ghp_[A-Za-z0-9]{20,}$"), "$GITHUB_TOKEN"),
    (re.compile(r"^github_pat_[A-Za-z0-9_]{20,}$"), "$GITHUB_TOKEN"),
    (re.compile(r"^BSA[A-Za-z0-9_-]{15,}$"), "$BRAVE_SEARCH_API_KEY"),
    (re.compile(r"^sk-ant-[A-Za-z0-9_-]{20,}$"), "$ANTHROPIC_API_KEY"),
    (re.compile(r"^sk-or-[A-Za-z0-9_-]{20,}$"), "$OPENROUTER_API_KEY"),
    (re.compile(r"^sk-[A-Za-z0-9_-]{20,}$"), "$OPENAI_API_KEY"),
]

# These keys are explicit env-var bindings; if the value matches a secret-shape
# regex above, replace it with the env-var form. The example must never carry
# a literal token, even a placeholder ``ghp_XXX...``.
ENV_KEY_HINTS: dict[str, str] = {
    "GITHUB_TOKEN": "$GITHUB_TOKEN",
    "GITHUB_PERSONAL_ACCESS_TOKEN": "$GITHUB_TOKEN",
    "BRAVE_API_KEY": "$BRAVE_SEARCH_API_KEY",
    "BRAVE_SEARCH_API_KEY": "$BRAVE_SEARCH_API_KEY",
    "ANTHROPIC_API_KEY": "$ANTHROPIC_API_KEY",
    "OPENAI_API_KEY": "$OPENAI_API_KEY",
    "OPENROUTER_API_KEY": "$OPENROUTER_API_KEY",
    "NOTION_API_KEY": "$NOTION_API_KEY",
    "LINEAR_API_KEY": "$LINEAR_API_KEY",
    "EXA_API_KEY": "$EXA_API_KEY",
}

FILE_BEARER_RE = re.compile(r"^Bearer\s+\$file:/tmp/(?P<upstream>[a-z]+)_mcp_access_token$")


def _scrub_env(name: str, env: dict[str, str]) -> dict[str, str]:
    """Return env with literal secrets re-abstracted to $VAR form."""
    out: dict[str, str] = {}
    for k, v in env.items():
        if not isinstance(v, str):
            out[k] = v
            continue

        # Already env-var form? Preserve it.
        if v.startswith("$"):
            out[k] = v
            continue

        # Known env-var name on a literal value → bind back to the canonical var.
        if k in ENV_KEY_HINTS and v:
            out[k] = ENV_KEY_HINTS[k]
            continue

        # Secret-shape regex catches stray tokens with non-standard key names.
        rewrote = False
        for pattern, replacement in SECRET_REWRITES:
            if pattern.search(v):
                out[k] = replacement
                rewrote = True
                break
        if rewrote:
            continue

        out[k] = v
    return out


def _scrub_headers(headers: dict[str, str], server_name: str) -> dict[str, str]:
    """Convert ``Bearer $file:/tmp/<x>_mcp_access_token`` to ``Bearer $X_MCP_BEARER_TOKEN``."""
    out: dict[str, str] = {}
    for k, v in headers.items():
        if isinstance(v, str):
            m = FILE_BEARER_RE.match(v)
            if m:
                upstream = m.group("upstream").upper()
                out[k] = f"Bearer ${upstream}_MCP_BEARER_TOKEN"
                continue
        out[k] = v
    return out


def _normalize_entry(name: str, entry: dict[str, Any]) -> dict[str, Any]:
    """Drop null placeholders and re-abstract secrets."""
    out: dict[str, Any] = {}
    for k, v in entry.items():
        if k in {"url", "headers", "oauth", "command", "args", "env"} and v in (None, [], {}):
            # Keep "url" only when this is an HTTP/SSE entry.
            entry_type = entry.get("type", "stdio")
            if entry_type in {"http", "sse"} and k == "url":
                out[k] = v  # null url on http/sse is a real bug, but preserve
            elif entry_type == "stdio" and k in {"url", "headers", "oauth"}:
                continue
            elif entry_type in {"http", "sse"} and k in {"command", "args", "env"}:
                continue
            else:
                out[k] = v
        else:
            out[k] = v

    # Apply secret scrubbing.
    if isinstance(out.get("env"), dict):
        out["env"] = _scrub_env(name, out["env"])
    if isinstance(out.get("headers"), dict):
        out["headers"] = _scrub_headers(out["headers"], name)

    return out


def regenerate(live: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {"mcpServers": {}}
    for name, entry in (live.get("mcpServers") or {}).items():
        if not isinstance(entry, dict):
            continue
        out["mcpServers"][name] = _normalize_entry(name, entry)
    if "skills" in live:
        out["skills"] = live["skills"]
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        default=str(LIVE_PATH),
        help=f"Live extensions_config.json path (default: {LIVE_PATH})",
    )
    parser.add_argument(
        "--example",
        default=str(EXAMPLE_PATH),
        help=f"Tracked example output path (default: {EXAMPLE_PATH})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Don't write — exit 1 if regenerated content differs from current example.",
    )
    args = parser.parse_args()

    live_path = Path(args.live)
    example_path = Path(args.example)

    if not live_path.exists():
        raise SystemExit(f"Live file not found: {live_path}")

    live = json.loads(live_path.read_text(encoding="utf-8"))
    regenerated = regenerate(live)
    rendered = json.dumps(regenerated, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        existing = example_path.read_text(encoding="utf-8") if example_path.exists() else ""
        if existing == rendered:
            print(f"OK  {example_path} is up to date with {live_path}")
            return 0
        print(f"DRIFT  {example_path} is stale; rerun without --check to regenerate")
        return 1

    example_path.write_text(rendered, encoding="utf-8")
    server_count = len(regenerated.get("mcpServers") or {})
    print(f"Wrote {example_path} ({server_count} mcpServers)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
