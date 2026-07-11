#!/usr/bin/env python3
"""Canonical Onyx RAG eval runner.

Runs the Q1–Q5 evaluation set from docs/ops/rag-evaluation-set.md against a
named persona, captures per-question answer text and retrieved document
metadata, and emits a JSON baseline artifact for diffing.

Designed to run unattended from cron after monitoring/check_health.sh:

    python3 deployment/helper/run_rag_tests.py \
        --persona-id 2 \
        --output-dir docs/ops/rag-baselines/

Onyx API key is read from ONYX_API_KEY env var, then from
deployment/onyx/.env. The key is never printed.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import requests


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BASE_URL = "http://localhost:3000"
DEFAULT_PERSONA_ID = 2
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "ops" / "rag-baselines"
DEFAULT_ENV_FILE = REPO_ROOT / "deployment" / "onyx" / ".env"

QUESTIONS: list[dict[str, str]] = [
    {
        "id": "Q1",
        "topic": "Blast-Wave Fit Parameters",
        "question": (
            "What are the typical transverse velocity and freeze-out temperature "
            "parameters used in Blast-Wave fits for 13 TeV pp collisions?"
        ),
    },
    {
        "id": "Q2",
        "topic": "Tsallis Distribution Baseline",
        "question": (
            "How does the Tsallis-Pareto distribution handle high-pT tails "
            "compared to standard Boltzmann-Juttner?"
        ),
    },
    {
        "id": "Q3",
        "topic": "Onyx OpenSearch Cutover Check",
        "question": "What is the command to run the OpenSearch parity regression check?",
    },
    {
        "id": "Q4",
        "topic": "Manuscript Model Comparison",
        "question": (
            "Does the manuscript compare the boson probability distribution model "
            "against a Tsallis or Blast-Wave baseline? If so, what is the stated motivation?"
        ),
    },
    {
        "id": "Q5",
        "topic": "System Architecture Boundary",
        "question": "Why shouldn't I use internal_search to check the status of the evidence ledger?",
    },
]


def load_api_key(env_file: Path) -> str:
    key = os.environ.get("ONYX_API_KEY", "").strip()
    if key:
        return key
    if not env_file.exists():
        raise SystemExit(f"ONYX_API_KEY not in env and {env_file} missing")
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("ONYX_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("ONYX_API_KEY not found in env or .env file")


def _summarize_top_documents(top_docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Strip large blobs from retrieved-doc metadata; keep what's useful for diffs."""
    summarized: list[dict[str, Any]] = []
    for doc in top_docs[:8]:
        if not isinstance(doc, dict):
            continue
        summarized.append({
            "document_id": doc.get("document_id"),
            "semantic_identifier": doc.get("semantic_identifier"),
            "link": doc.get("link"),
            "score": doc.get("score"),
            "source_type": doc.get("source_type"),
            "blurb": (doc.get("blurb") or "")[:200],
            "chunk_ind": doc.get("chunk_ind"),
        })
    return summarized


def parse_stream(text: str) -> dict[str, Any]:
    """Parse Onyx send-chat-message NDJSON stream into a structured record."""
    answer = ""
    top_documents: list[dict[str, Any]] = []
    search_queries: list[str] = []
    errors: list[str] = []
    event_kinds: dict[str, int] = {}
    citations: list[dict[str, Any]] = []

    for line in text.strip().split("\n"):
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue

        if "error" in data:
            errors.append(str(data.get("error"))[:500])
            event_kinds["error"] = event_kinds.get("error", 0) + 1
            continue

        # Some Onyx versions wrap events in {"obj": {...}}, others stream flat.
        payload = data.get("obj") if isinstance(data.get("obj"), dict) else data
        kind = payload.get("type") or payload.get("event_type")
        if kind:
            event_kinds[kind] = event_kinds.get(kind, 0) + 1

        if kind == "message_delta":
            answer += payload.get("content", "") or ""
        elif kind == "search_tool_documents_delta":
            docs = payload.get("documents") or payload.get("top_documents")
            if isinstance(docs, list):
                top_documents = docs
        elif kind == "search_tool_queries_delta":
            qs = payload.get("queries")
            if isinstance(qs, list):
                search_queries.extend(str(q) for q in qs)
        elif "answer_piece" in payload:
            answer += payload.get("answer_piece") or ""
        elif "top_documents" in payload and isinstance(payload["top_documents"], list):
            top_documents = payload["top_documents"]
        elif kind in {"tool_result", "tool"} and isinstance(payload.get("tool_result"), dict):
            tr = payload["tool_result"]
            if isinstance(tr.get("top_documents"), list):
                top_documents = tr["top_documents"]
        elif "citations" in payload and isinstance(payload["citations"], list):
            citations = payload["citations"]
        elif kind == "citation_info":
            cites = payload.get("citations")
            if isinstance(cites, list):
                citations = cites

    return {
        "answer": answer.strip(),
        "top_documents": _summarize_top_documents(top_documents),
        "search_queries": search_queries,
        "citations": citations[:8],
        "errors": errors,
        "event_kinds": event_kinds,
    }


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


def run_question(
    base_url: str, headers: dict[str, str], persona_id: int, q: dict[str, str],
    *, message_timeout: int = 240,
) -> dict[str, Any]:
    started = time.monotonic()
    try:
        sess_resp = requests.post(
            f"{base_url}/api/chat/create-chat-session",
            headers=headers,
            json={"persona_id": persona_id, "description": f"RAG eval {q['id']}"},
            timeout=30,
        )
    except requests.RequestException as exc:
        return {
            "id": q["id"],
            "topic": q["topic"],
            "question": q["question"],
            "persona_id": persona_id,
            "status": "session_create_failed",
            "error": f"{type(exc).__name__}: {exc}"[:300],
            "elapsed_ms": int((time.monotonic() - started) * 1000),
        }
    if sess_resp.status_code != 200:
        return {
            "id": q["id"],
            "topic": q["topic"],
            "question": q["question"],
            "persona_id": persona_id,
            "status": "session_create_failed",
            "http_status": sess_resp.status_code,
            "error": sess_resp.text[:300],
            "elapsed_ms": int((time.monotonic() - started) * 1000),
        }

    session_id = sess_resp.json().get("chat_session_id")
    try:
        msg_resp = requests.post(
            f"{base_url}/api/chat/send-chat-message",
            headers=headers,
            json={
                "chat_session_id": session_id,
                "message": q["question"],
                "parent_message_id": None,
                "file_descriptors": [],
                "prompt_id": None,
                "search_doc_ids": [],
                "query_override": None,
            },
            timeout=message_timeout,
        )
    except requests.RequestException as exc:
        return {
            "id": q["id"],
            "topic": q["topic"],
            "question": q["question"],
            "persona_id": persona_id,
            "chat_session_id": session_id,
            "status": "send_message_timeout",
            "error": f"{type(exc).__name__}: {exc}"[:300],
            "elapsed_ms": int((time.monotonic() - started) * 1000),
        }
    parsed = parse_stream(msg_resp.text)
    elapsed_ms = int((time.monotonic() - started) * 1000)

    return {
        "id": q["id"],
        "topic": q["topic"],
        "question": q["question"],
        "persona_id": persona_id,
        "chat_session_id": session_id,
        "http_status": msg_resp.status_code,
        "elapsed_ms": elapsed_ms,
        "answer_chars": len(parsed["answer"]),
        "answer_preview": parsed["answer"][:400],
        "answer": parsed["answer"],
        "top_documents": parsed["top_documents"],
        "search_queries": parsed.get("search_queries") or [],
        "citations": parsed["citations"],
        "errors": parsed["errors"],
        "event_kinds": parsed["event_kinds"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--persona-id", type=int, default=DEFAULT_PERSONA_ID)
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory to write the JSON baseline artifact",
    )
    parser.add_argument(
        "--label",
        default=None,
        help="Optional label suffix for the artifact filename, e.g. 'post-reindex'",
    )
    parser.add_argument(
        "--env-file",
        default=str(DEFAULT_ENV_FILE),
        help="Fallback .env file to read ONYX_API_KEY from",
    )
    parser.add_argument(
        "--print-stdout",
        action="store_true",
        help="Echo per-question Q/A summary to stdout in addition to writing JSON",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        default=True,
        help="Delete test sessions after completion (default: True)",
    )
    parser.add_argument(
        "--no-cleanup",
        dest="cleanup",
        action="store_false",
        help="Keep test sessions after completion",
    )
    args = parser.parse_args()

    api_key = load_api_key(Path(args.env_file))
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    suffix = f"-{args.label}" if args.label else ""
    output_path = output_dir / f"rag-baseline-{timestamp}-persona-{args.persona_id}{suffix}.json"

    results: list[dict[str, Any]] = []
    session_ids: list[str] = []

    try:
        for q in QUESTIONS:
            if args.print_stdout:
                print(f"[{q['id']}] {q['topic']}", flush=True)
            result = run_question(args.base_url, headers, args.persona_id, q)
            results.append(result)

            # Track session ID for cleanup
            if result.get("chat_session_id"):
                session_ids.append(result["chat_session_id"])

            if args.print_stdout:
                preview = result.get("answer_preview", "")
                print(f"  http={result.get('http_status')} elapsed_ms={result.get('elapsed_ms')}")
                print(f"  answer: {preview[:200]}")
                print(f"  retrieved={len(result.get('top_documents') or [])} errors={len(result.get('errors') or [])}")
                print("---")
    finally:
        # Cleanup test sessions if requested
        if args.cleanup and session_ids:
            if args.print_stdout:
                print(f"\nCleaning up {len(session_ids)} test sessions...", flush=True)
            deleted = 0
            for session_id in session_ids:
                if delete_session(args.base_url, headers, session_id):
                    deleted += 1
            if args.print_stdout:
                print(f"Deleted {deleted}/{len(session_ids)} sessions")

    artifact = {
        "schema_version": 1,
        "ran_at_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "base_url": args.base_url,
        "persona_id": args.persona_id,
        "label": args.label,
        "results": results,
        "summary": {
            "total": len(results),
            "with_answer": sum(1 for r in results if (r.get("answer_chars") or 0) > 0),
            "with_retrieval": sum(1 for r in results if r.get("top_documents")),
            "with_errors": sum(1 for r in results if r.get("errors")),
        },
    }
    output_path.write_text(json.dumps(artifact, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote baseline artifact: {output_path}")
    print(json.dumps(artifact["summary"], indent=2))

    # Exit non-zero if any question erroneously failed at the transport layer.
    transport_failures = sum(
        1 for r in results if r.get("http_status") not in (200, None) or r.get("status") == "session_create_failed"
    )
    return 0 if transport_failures == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
