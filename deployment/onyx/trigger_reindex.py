#!/usr/bin/env python3
"""Trigger one or more Onyx connector reindex runs without hardcoded secrets."""

from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass


DEFAULT_BASE_URL = "http://localhost:8080"


@dataclass
class TriggerResult:
    connector_id: int
    ok: bool
    status: int
    body: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default=os.environ.get("ONYX_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
        help="Onyx API base URL, usually the api_server directly on :8080.",
    )
    parser.add_argument(
        "--username",
        default=os.environ.get("ONYX_USERNAME"),
        help="Onyx admin username. Falls back to ONYX_USERNAME.",
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("ONYX_PASSWORD"),
        help="Onyx admin password. Falls back to ONYX_PASSWORD.",
    )
    parser.add_argument(
        "--connector-id",
        type=int,
        action="append",
        dest="connector_ids",
        help="Connector id to trigger. Repeat this flag for multiple connectors.",
    )
    parser.add_argument(
        "--credential-id",
        type=int,
        action="append",
        default=[],
        help="Credential id to pass through to every trigger call.",
    )
    parser.add_argument(
        "--from-beginning",
        action="store_true",
        help="Request a full rebuild instead of an incremental run.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.username or not args.password:
        print(
            "Missing Onyx credentials. Provide --username/--password or "
            "set ONYX_USERNAME and ONYX_PASSWORD.",
            file=sys.stderr,
        )
        return 1

    if not args.connector_ids:
        print("Provide at least one --connector-id.", file=sys.stderr)
        return 1

    opener = build_opener()
    login(opener, args.base_url, args.username, args.password)

    failures = 0
    for connector_id in args.connector_ids:
        result = trigger_connector(
            opener=opener,
            base_url=args.base_url,
            connector_id=connector_id,
            credential_ids=args.credential_id,
            from_beginning=args.from_beginning,
        )
        status = "ok" if result.ok else "error"
        print(
            f"[{status}] connector_id={result.connector_id} "
            f"status={result.status} body={result.body}"
        )
        failures += 0 if result.ok else 1

    return 0 if failures == 0 else 2


def build_opener() -> urllib.request.OpenerDirector:
    cookie_jar = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))


def login(
    opener: urllib.request.OpenerDirector,
    base_url: str,
    username: str,
    password: str,
) -> None:
    data = urllib.parse.urlencode({"username": username, "password": password}).encode(
        "utf-8"
    )
    request = urllib.request.Request(
        f"{base_url}/auth/login",
        data=data,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with opener.open(request, timeout=30) as response:
            if response.status != 204:
                body = response.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"Login failed: {response.status} {body}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Login failed: {exc.code} {body}") from exc


def trigger_connector(
    *,
    opener: urllib.request.OpenerDirector,
    base_url: str,
    connector_id: int,
    credential_ids: list[int],
    from_beginning: bool,
) -> TriggerResult:
    payload = {
        "connector_id": connector_id,
        "credential_ids": credential_ids,
        "from_beginning": from_beginning,
    }
    request = urllib.request.Request(
        f"{base_url}/manage/admin/connector/run-once",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json"},
    )

    try:
        with opener.open(request, timeout=30) as response:
            body = response.read().decode("utf-8", errors="replace")
            return TriggerResult(
                connector_id=connector_id,
                ok=response.status == 200,
                status=response.status,
                body=body,
            )
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return TriggerResult(
            connector_id=connector_id,
            ok=False,
            status=exc.code,
            body=body,
        )


if __name__ == "__main__":
    raise SystemExit(main())
