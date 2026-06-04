#!/usr/bin/env python3
"""Discover the sandbox URL for the current thread.

This script queries the DeerFlow gateway to find the sandbox URL
for the current thread, so that deployed web apps can be embedded
in artifact browser iframes.

Usage:
    python discover_sandbox_url.py [--thread-id <ID>]

The script looks for thread_id in this order:
1. --thread-id CLI argument
2. DEER_FLOW_THREAD_ID environment variable
3. Scanning sandbox info files on disk
"""

import argparse
import json
import os
import sys
import urllib.request


def find_thread_id():
    """Try to discover the current thread ID."""
    # Check environment variable first
    tid = os.environ.get("DEER_FLOW_THREAD_ID")
    if tid:
        return tid

    # Check for sandbox info files in the default data directory
    data_dirs = [
        os.path.expanduser("~/.deer-flow/data"),
        "/app/backend/.deer-flow/data",
        os.path.join(os.environ.get("DEER_FLOW_PROJECT_ROOT", ""), ".deer-flow", "data"),
    ]

    for data_dir in data_dirs:
        state_file = os.path.join(data_dir, "sandbox_state.json")
        if os.path.exists(state_file):
            with open(state_file) as f:
                state = json.load(f)
                # The state file maps thread_id -> sandbox_id
                if state:
                    return list(state.keys())[0]

    return None


def get_sandbox_info(thread_id, gateway_url="http://localhost:2026"):
    """Query the gateway for sandbox info."""
    url = f"{gateway_url}/api/sandbox/info?thread_id={thread_id}"
    req = urllib.request.Request(url)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def main():
    parser = argparse.ArgumentParser(description="Discover the sandbox URL for the current thread")
    parser.add_argument("--thread-id", help="Thread ID (auto-detected if not provided)")
    parser.add_argument("--gateway-url", default="http://localhost:2026", help="Gateway URL")
    args = parser.parse_args()

    thread_id = args.thread_id or find_thread_id()

    if not thread_id:
        print("ERROR: Could not determine thread_id.", file=sys.stderr)
        print("Pass --thread-id <ID> or set DEER_FLOW_THREAD_ID env var.", file=sys.stderr)
        sys.exit(1)

    try:
        info = get_sandbox_info(thread_id, args.gateway_url)
        print(info.get("sandbox_url", ""))
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
