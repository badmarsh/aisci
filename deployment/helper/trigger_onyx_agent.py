#!/usr/bin/env python3
"""Multica → Onyx Craft Agent integration wrapper.

This script bridges Multica task assignments to Onyx Craft agent runs.
Onyx Craft agents are sandboxed RAG-enabled agents with physics-validator
personas that write to evidence-ledger.md.

Usage:
    python trigger_onyx_agent.py --card-id <multica-issue-id>
    python trigger_onyx_agent.py --card-id <multica-issue-id> --persona physics-validator
    python trigger_onyx_agent.py --card-id <multica-issue-id> --corpus physics --output evidence-ledger.md

Environment:
    ONYX_API_URL: Onyx API endpoint (default: http://localhost:3000)
    ONYX_API_KEY: Onyx API authentication token (optional)

Exit codes:
    0: Agent run completed successfully
    1: Configuration error (missing card-id, invalid persona)
    2: Onyx API error (connection failed, authentication failed)
    3: Agent run failed (Onyx reported failure)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import requests


DEFAULT_ONYX_URL = "http://localhost:3000"
DEFAULT_PERSONA = "physics-validator"
DEFAULT_CORPUS = "physics"
DEFAULT_OUTPUT = "research/robert/evidence-ledger.md"


def load_multica_card(card_id: str) -> dict[str, Any]:
    """Fetch Multica issue details via CLI.

    Args:
        card_id: Multica issue ID (UUID or identifier like AIS-6)

    Returns:
        Issue details as dict

    Raises:
        RuntimeError: If multica CLI fails
    """
    import subprocess

    result = subprocess.run(
        ["multica", "issue", "get", card_id, "--output", "json"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Failed to fetch Multica card {card_id}: {result.stderr}")

    return json.loads(result.stdout)


def trigger_onyx_run(
    card_data: dict[str, Any],
    persona: str,
    corpus: str,
    output_path: str,
    onyx_url: str,
    api_key: str | None,
) -> dict[str, Any]:
    """Trigger an Onyx Craft agent run.

    Args:
        card_data: Multica issue data
        persona: Onyx persona to use (e.g., 'physics-validator')
        corpus: RAG corpus to query (e.g., 'physics')
        output_path: Where agent should write results
        onyx_url: Onyx API base URL
        api_key: Optional API key for authentication

    Returns:
        Onyx run response

    Raises:
        requests.RequestException: If API call fails
    """
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # Construct Onyx agent request
    # NOTE: This is a conceptual API - actual Onyx API may differ
    payload = {
        "persona": persona,
        "corpus": corpus,
        "task": {
            "title": card_data.get("title", ""),
            "description": card_data.get("description", ""),
            "issue_id": card_data.get("id", ""),
            "identifier": card_data.get("identifier", ""),
        },
        "output": {
            "path": output_path,
            "format": "markdown",
        },
        "context": {
            "source": "multica",
            "workspace_id": card_data.get("workspace_id", ""),
        },
    }

    # POST to Onyx agent endpoint
    # Adjust endpoint path based on actual Onyx API
    response = requests.post(
        f"{onyx_url}/api/agent/run",
        headers=headers,
        json=payload,
        timeout=300,  # 5 minute timeout for agent runs
    )
    response.raise_for_status()

    return response.json()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Trigger Onyx Craft agent from Multica card assignment"
    )
    parser.add_argument(
        "--card-id",
        required=True,
        help="Multica issue ID (UUID or identifier like AIS-6)",
    )
    parser.add_argument(
        "--persona",
        default=DEFAULT_PERSONA,
        help=f"Onyx persona to use (default: {DEFAULT_PERSONA})",
    )
    parser.add_argument(
        "--corpus",
        default=DEFAULT_CORPUS,
        help=f"RAG corpus to query (default: {DEFAULT_CORPUS})",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output file path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--onyx-url",
        default=os.getenv("ONYX_API_URL", DEFAULT_ONYX_URL),
        help=f"Onyx API URL (default: {DEFAULT_ONYX_URL})",
    )

    args = parser.parse_args()

    # Get API key from environment
    api_key = os.getenv("ONYX_API_KEY")

    try:
        # Fetch Multica card details
        print(f"Fetching Multica card {args.card_id}...", file=sys.stderr)
        card_data = load_multica_card(args.card_id)

        # Trigger Onyx agent run
        print(
            f"Triggering Onyx agent (persona={args.persona}, corpus={args.corpus})...",
            file=sys.stderr,
        )
        result = trigger_onyx_run(
            card_data=card_data,
            persona=args.persona,
            corpus=args.corpus,
            output_path=args.output,
            onyx_url=args.onyx_url,
            api_key=api_key,
        )

        # Report success
        print(json.dumps(result, indent=2))
        print(f"✓ Onyx agent run completed", file=sys.stderr)
        return 0

    except RuntimeError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1
    except requests.RequestException as e:
        print(f"Onyx API error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
