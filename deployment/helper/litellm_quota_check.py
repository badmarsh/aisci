#!/usr/bin/env python3
"""Probe LiteLLM model routes without printing secrets.

The check sends a tiny chat completion to each selected model and reports only
status/category information. It is intended for operator health checks after
connector indexing starts returning provider quota or rate-limit errors.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict
from dataclasses import dataclass
from typing import Iterable


DEFAULT_MODELS = [
    "qwen-cloud-fast",
    "qwen-rag-fast",
    "qwen-rag-balanced",
    "qwen-rag-vision",
    "qwen-rag-local",
    "gemma2",
]

SECRET_RE = re.compile(r"(sk-)[A-Za-z0-9_-]+")


@dataclass
class ProbeResult:
    model: str
    status: str
    http_status: int | None
    elapsed_ms: int
    detail: str


def redact(text: str) -> str:
    return SECRET_RE.sub(r"\1<redacted>", text)


def classify(http_status: int | None, body: str) -> tuple[str, str]:
    text = body[:500]
    lowered = text.lower()

    if http_status == 200:
        return "ok", "completion accepted"
    if http_status == 429 or "ratelimit" in lowered or "limit_requests" in lowered:
        return "rate_limited", "provider or router rate limit"
    if http_status in {401, 403} or "authentication" in lowered:
        return "auth_error", "authentication failed"
    if http_status == 404 or "no deployments available" in lowered:
        return "unavailable", "model route unavailable"
    if "context window" in lowered:
        return "context_window", "request exceeded configured context"
    if "timed out" in lowered or "timeout" in lowered:
        return "timeout", "request timed out"
    if http_status is None:
        return "connection_error", text or "connection failed"
    return "error", text or f"http {http_status}"


def probe_model(
    base_url: str,
    model: str,
    timeout: float,
    api_key: str | None,
    prompt: str,
) -> ProbeResult:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2,
    }
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=body,
        headers=headers,
        method="POST",
    )

    start = time.monotonic()
    http_status: int | None = None
    response_text = ""
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            http_status = response.status
            response_text = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        http_status = exc.code
        response_text = exc.read().decode("utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001 - operator diagnostic surface.
        response_text = str(exc)

    elapsed_ms = int((time.monotonic() - start) * 1000)
    status, detail = classify(http_status, response_text)
    return ProbeResult(
        model=model,
        status=status,
        http_status=http_status,
        elapsed_ms=elapsed_ms,
        detail=redact(detail),
    )


def print_table(results: Iterable[ProbeResult]) -> None:
    print(f"{'model':<24} {'status':<16} {'http':<6} {'ms':<8} detail")
    print(f"{'-' * 24} {'-' * 16} {'-' * 6} {'-' * 8} {'-' * 30}")
    for result in results:
        http_status = "" if result.http_status is None else str(result.http_status)
        print(
            f"{result.model:<24} {result.status:<16} "
            f"{http_status:<6} {result.elapsed_ms:<8} {result.detail}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "models",
        nargs="*",
        help="Model names to probe. Defaults to the Onyx RAG routes.",
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:4001/v1",
        help="LiteLLM OpenAI-compatible base URL.",
    )
    parser.add_argument(
        "--api-key-env",
        default="",
        help="Optional env var containing the LiteLLM bearer token.",
    )
    parser.add_argument("--timeout", type=float, default=45.0)
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if any probed model is not ok.",
    )
    parser.add_argument(
        "--prompt",
        default="Reply with ok.",
        help="Tiny prompt to send to each model.",
    )
    args = parser.parse_args()

    models = args.models or DEFAULT_MODELS
    api_key = os.environ.get(args.api_key_env) if args.api_key_env else None
    results = [
        probe_model(args.base_url, model, args.timeout, api_key, args.prompt)
        for model in models
    ]

    if args.json:
        print(json.dumps([asdict(result) for result in results], indent=2))
    else:
        print_table(results)

    bad = [result for result in results if result.status != "ok"]
    if args.strict and bad:
        return 2
    if not any(result.status == "ok" for result in results):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
