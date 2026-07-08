#!/usr/bin/env python3
"""
OAuth Token Startup Check

Reads CONSENSUS_MCP_BEARER_TOKEN and SCITE_MCP_BEARER_TOKEN from environment.
Prints clear warnings if either is empty or missing.
Exits with code 1 if either is missing, so Docker health checks can catch it.

Usage:
    python check_oauth_tokens.py
"""

import os
import sys


def check_token(name: str) -> bool:
    """Check if a token environment variable is set and non-empty."""
    value = os.environ.get(name, "").strip()

    if not value:
        print(f"❌ ERROR: {name} is empty or missing", file=sys.stderr)
        return False

    print(f"✓ {name} is set")
    return True


def main() -> int:
    """Check both OAuth tokens and exit with appropriate code."""
    print("Checking OAuth tokens...")
    print()

    consensus_ok = check_token("CONSENSUS_MCP_BEARER_TOKEN")
    scite_ok = check_token("SCITE_MCP_BEARER_TOKEN")

    print()

    if not consensus_ok or not scite_ok:
        print("⚠️  OAuth tokens are missing. Literature search tools will fail.", file=sys.stderr)
        print()
        print("To complete OAuth flows:", file=sys.stderr)
        print("  1. Consensus: https://consensus.app (OAuth login → copy token)", file=sys.stderr)
        print("  2. Scite: https://scite.ai (OAuth login → copy token)", file=sys.stderr)
        print()
        print("Then set the tokens in your .env file:", file=sys.stderr)
        print("  CONSENSUS_MCP_BEARER_TOKEN=<your-token>", file=sys.stderr)
        print("  SCITE_MCP_BEARER_TOKEN=<your-token>", file=sys.stderr)
        print()
        return 1

    print("✅ All OAuth tokens are set")
    return 0


if __name__ == "__main__":
    sys.exit(main())
