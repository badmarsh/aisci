#!/usr/bin/env python3
"""Clean up RAG test sessions from Onyx database.

Identifies and deletes chat sessions created by RAG tests based on description
patterns. Supports dry-run mode and age-based filtering.

Usage:
    # Dry run (preview only)
    python3 deployment/helper/cleanup_test_sessions.py --dry-run

    # Delete all test sessions
    python3 deployment/helper/cleanup_test_sessions.py

    # Delete sessions older than 24 hours
    python3 deployment/helper/cleanup_test_sessions.py --older-than-hours 24

    # Use custom base URL
    python3 deployment/helper/cleanup_test_sessions.py --base-url http://localhost:3000
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import sys
from pathlib import Path
from typing import Any

import requests


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BASE_URL = "http://localhost:3000"
DEFAULT_ENV_FILE = REPO_ROOT / "deployment" / "onyx" / ".env"

# Patterns that identify test sessions
TEST_SESSION_PATTERNS = [
    "RAG eval",
    "RAG Test",
    "RAG test",
]


def load_api_key(env_file: Path) -> str:
    """Load ONYX_API_KEY from environment or .env file."""
    api_key = os.environ.get("ONYX_API_KEY")
    if api_key:
        return api_key

    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("ONYX_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")

    print("ERROR: ONYX_API_KEY not found in environment or .env file", file=sys.stderr)
    sys.exit(1)


def get_all_sessions(base_url: str, headers: dict[str, str]) -> list[dict[str, Any]]:
    """Fetch all chat sessions for the current user."""
    try:
        resp = requests.get(
            f"{base_url}/api/chat/get-user-chat-sessions",
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        # API returns {"sessions": [...]}
        if isinstance(data, dict) and "sessions" in data:
            return data["sessions"]
        return data if isinstance(data, list) else []
    except requests.RequestException as exc:
        print(f"ERROR: Failed to fetch sessions: {exc}", file=sys.stderr)
        sys.exit(1)


def is_test_session(session: dict[str, Any]) -> bool:
    """Check if a session matches test session patterns."""
    # API uses "name" field for session description
    name = session.get("name", "") or session.get("description", "")
    if not name:
        return False

    return any(pattern in name for pattern in TEST_SESSION_PATTERNS)


def parse_timestamp(timestamp_str: str | None) -> _dt.datetime | None:
    """Parse ISO timestamp string to datetime."""
    if not timestamp_str:
        return None
    try:
        # Handle both with and without timezone
        if timestamp_str.endswith("Z"):
            timestamp_str = timestamp_str[:-1] + "+00:00"
        return _dt.datetime.fromisoformat(timestamp_str)
    except (ValueError, AttributeError):
        return None


def delete_session(base_url: str, headers: dict[str, str], session_id: str) -> bool:
    """Delete a chat session via API. Returns True if successful."""
    try:
        resp = requests.delete(
            f"{base_url}/api/chat/delete-chat-session/{session_id}",
            headers=headers,
            timeout=10,
        )
        return resp.status_code in (200, 204)
    except requests.RequestException:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--env-file",
        default=str(DEFAULT_ENV_FILE),
        help="Fallback .env file to read ONYX_API_KEY from",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview sessions to delete without actually deleting",
    )
    parser.add_argument(
        "--older-than-hours",
        type=int,
        default=None,
        help="Only delete sessions older than N hours",
    )
    args = parser.parse_args()

    api_key = load_api_key(Path(args.env_file))
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    print(f"Fetching sessions from {args.base_url}...", flush=True)
    all_sessions = get_all_sessions(args.base_url, headers)
    print(f"Found {len(all_sessions)} total sessions")

    # Filter test sessions
    test_sessions = [s for s in all_sessions if is_test_session(s)]
    print(f"Identified {len(test_sessions)} test sessions")

    if not test_sessions:
        print("No test sessions to clean up")
        return 0

    # Apply age filter if specified
    if args.older_than_hours is not None:
        cutoff = _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(hours=args.older_than_hours)
        filtered_sessions = []
        for session in test_sessions:
            created_at = parse_timestamp(session.get("time_created"))
            if created_at and created_at < cutoff:
                filtered_sessions.append(session)
        test_sessions = filtered_sessions
        print(f"After age filter (>{args.older_than_hours}h): {len(test_sessions)} sessions")

    if not test_sessions:
        print("No sessions match the age criteria")
        return 0

    # Display sessions to be deleted
    print("\nSessions to delete:")
    for session in test_sessions:
        session_id = session.get("id", "unknown")
        name = session.get("name", "") or session.get("description", "")
        created_at = session.get("time_created", "unknown")
        print(f"  - {session_id[:8]}... | {name} | created: {created_at}")

    if args.dry_run:
        print(f"\n[DRY RUN] Would delete {len(test_sessions)} sessions")
        return 0

    # Confirm deletion
    print(f"\nAbout to delete {len(test_sessions)} test sessions")
    try:
        confirm = input("Continue? [y/N]: ").strip().lower()
        if confirm not in ("y", "yes"):
            print("Aborted")
            return 0
    except (KeyboardInterrupt, EOFError):
        print("\nAborted")
        return 0

    # Delete sessions
    print("\nDeleting sessions...", flush=True)
    deleted = 0
    failed = 0
    for session in test_sessions:
        session_id = session.get("id")
        if not session_id:
            continue

        if delete_session(args.base_url, headers, session_id):
            deleted += 1
            print(f"  ✓ Deleted {session_id[:8]}...")
        else:
            failed += 1
            print(f"  ✗ Failed to delete {session_id[:8]}...")

    print(f"\nDeleted: {deleted}/{len(test_sessions)} sessions")
    if failed > 0:
        print(f"Failed: {failed} sessions")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
