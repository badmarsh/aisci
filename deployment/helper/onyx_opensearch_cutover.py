#!/usr/bin/env python3
"""Audit and apply the Onyx OpenSearch cutover from the running stack.

Host mode:
- shells into the running `api_server` container through `docker compose exec`
- re-runs this same script inside the container where Onyx deps and env exist

Container mode:
- audits Postgres document counts against OpenSearch index counts
- reports tenant migration-record state
- optionally enables tenant OpenSearch retrieval when parity checks pass
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path("/home/ubuntu/aisci")
DEFAULT_COMPOSE_DIR = REPO_ROOT / "deployment" / "onyx"
DEFAULT_CONTAINER_PATH = "/workspace/aisci/deployment/helper/onyx_opensearch_cutover.py"
DEFAULT_DB_PORT = "5432"
DEFAULT_DB_NAME = "postgres"
DEFAULT_OS_PORT = "9200"
DEFAULT_OS_USER = "admin"
MAX_OPENSEARCH_DOCS = 10000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Enable tenant OpenSearch retrieval after parity checks pass.",
    )
    parser.add_argument(
        "--allow-primary-stale",
        action="store_true",
        help=(
            "Allow cutover when the active search_settings index matches the "
            "DB even if the inactive primary index still has stale or missing docs."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON instead of the text summary.",
    )
    parser.add_argument(
        "--compose-dir",
        default=str(DEFAULT_COMPOSE_DIR),
        help="Path to the Onyx docker-compose directory in host mode.",
    )
    parser.add_argument(
        "--inside-container",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.inside_container:
        result = run_inside_container(args)
    else:
        result = run_from_host(args)

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_text_summary(result))
    return int(result["exit_code"])


def run_from_host(args: argparse.Namespace) -> dict[str, Any]:
    compose_dir = Path(args.compose_dir).resolve()
    if not compose_dir.exists():
        return {
            "exit_code": 1,
            "error": f"Compose directory not found: {compose_dir}",
        }

    cmd = [
        "docker",
        "compose",
        "exec",
        "-T",
        "onyx-api",
        "python",
        DEFAULT_CONTAINER_PATH,
        "--inside-container",
    ]
    if args.apply:
        cmd.append("--apply")
    if args.allow_primary_stale:
        cmd.append("--allow-primary-stale")
    cmd.append("--json")

    try:
        completed = subprocess.run(
            cmd,
            cwd=compose_dir,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return {
            "exit_code": 1,
            "error": "docker is not installed or not on PATH.",
        }

    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError:
        if completed.returncode != 0:
            message = completed.stderr.strip() or completed.stdout.strip()
            return {
                "exit_code": 1,
                "error": message or "docker compose exec failed",
            }
        return {
            "exit_code": 1,
            "error": "Container helper did not return JSON.",
            "raw_output": completed.stdout.strip(),
        }

    return result


def run_inside_container(args: argparse.Namespace) -> dict[str, Any]:
    from sqlalchemy import create_engine  # type: ignore
    from sqlalchemy import text  # type: ignore

    db_url = build_db_url()
    engine = create_engine(db_url)

    with engine.begin() as conn:
        search_settings_columns = get_table_columns(conn, "search_settings", text)
        tenant_record_columns = get_table_columns(
            conn, "opensearch_tenant_migration_record", text
        )
        document_record_columns = get_table_columns(
            conn, "opensearch_document_migration_record", text
        )

        search_settings = get_search_settings(conn, search_settings_columns, text)
        document_columns = get_table_columns(conn, "document", text)
        db_documents = get_db_documents(conn, document_columns, text)
        tenant_record = get_tenant_record(
            conn, tenant_record_columns, document_record_columns, text
        )

        primary_index_name, alt_index_name = derive_index_names(search_settings)
        active_index_name = str(search_settings.get("index_name") or primary_index_name)

        primary_index = fetch_opensearch_index(primary_index_name)
        alt_index = fetch_opensearch_index(alt_index_name)
        db_summary = summarize_db_documents(db_documents)
        primary_summary = compare_index_to_db(primary_index, db_summary)
        alt_summary = compare_index_to_db(alt_index, db_summary)

        active_summary = (
            alt_summary if active_index_name == alt_index_name else primary_summary
        )
        strict_ready = active_summary["ready"]
        if active_index_name == alt_index_name:
            strict_ready = primary_summary["ready"] and active_summary["ready"]
        active_only_ready = active_summary["ready"]
        ready_for_cutover = (
            active_only_ready if args.allow_primary_stale else strict_ready
        )

        result: dict[str, Any] = {
            "mode": "container",
            "exit_code": 0,
            "search_settings": {
                "id": search_settings.get("id"),
                "model_name": search_settings.get("model_name"),
                "model_dim": search_settings.get("model_dim"),
                "status": search_settings.get("status"),
                "enable_contextual_rag": bool(
                    search_settings.get("enable_contextual_rag")
                ),
                "primary_index_name": primary_index_name,
                "alt_index_name": alt_index_name,
                "active_index_name": active_index_name,
            },
            "db": db_summary,
            "tenant_record": tenant_record,
            "indexes": {
                "primary": primary_summary,
                "alt": alt_summary,
            },
            "ready_for_cutover": ready_for_cutover,
            "checks": {
                "strict_ready": strict_ready,
                "active_only_ready": active_only_ready,
                "allow_primary_stale": bool(args.allow_primary_stale),
            },
            "applied": False,
        }

        if args.apply:
            if not ready_for_cutover:
                result["exit_code"] = 2
                result["error"] = (
                    "Parity checks failed; refusing to enable tenant OpenSearch retrieval."
                )
                return result

            apply_cutover(conn, db_summary["total_chunks"], tenant_record_columns, text)
            updated_record = get_tenant_record(
                conn, tenant_record_columns, document_record_columns, text
            )
            result["tenant_record"] = updated_record
            result["applied"] = True

        return result


def build_db_url() -> str:
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "")
    host = os.environ.get("POSTGRES_HOST", "relational_db")
    port = os.environ.get("POSTGRES_PORT", DEFAULT_DB_PORT)
    db_name = os.environ.get("POSTGRES_DB", DEFAULT_DB_NAME)
    quoted_password = urllib.parse.quote_plus(password)
    return f"postgresql+psycopg2://{user}:{quoted_password}@{host}:{port}/{db_name}"


def get_table_columns(conn: Any, table_name: str, text_fn: Any) -> list[str]:
    rows = conn.execute(
        text_fn(
            """
            select column_name
            from information_schema.columns
            where table_schema = 'public' and table_name = :table_name
            order by ordinal_position
            """
        ),
        {"table_name": table_name},
    ).fetchall()
    return [row[0] for row in rows]


def get_search_settings(conn: Any, columns: list[str], text_fn: Any) -> dict[str, Any]:
    select_columns = ["id", "model_name", "model_dim", "status"]
    if "enable_contextual_rag" in columns:
        select_columns.append("enable_contextual_rag")
    if "index_name" in columns:
        select_columns.append("index_name")

    query = f"""
        select {", ".join(select_columns)}
        from search_settings
        order by (case when status::text = 'PRESENT' then 0 else 1 end), id desc
        limit 1
    """
    row = conn.execute(text_fn(query)).mappings().first()
    if row is None:
        raise RuntimeError("search_settings is empty.")
    return dict(row)


def derive_index_names(search_settings: dict[str, Any]) -> tuple[str, str]:
    if search_settings.get("index_name"):
        index_name = str(search_settings["index_name"])
        if index_name.endswith("__danswer_alt_index"):
            primary = index_name[: -len("__danswer_alt_index")]
            return primary, index_name
        return index_name, f"{index_name}__danswer_alt_index"

    model_name = str(search_settings["model_name"])
    sanitized = re.sub(r"[^a-z0-9]+", "_", model_name.lower()).strip("_")
    primary = f"danswer_chunk_{sanitized}"
    return primary, f"{primary}__danswer_alt_index"


def get_db_documents(
    conn: Any, columns: list[str], text_fn: Any
) -> list[dict[str, Any]]:
    where_clauses = ["semantic_id is not null", "chunk_count is not null", "chunk_count > 0"]
    if "hidden" in columns:
        where_clauses.append("coalesce(hidden, false) = false")

    rows = conn.execute(
        text_fn(
            f"""
            select id, semantic_id, link, chunk_count
            from document
            where {" and ".join(where_clauses)}
            order by semantic_id nulls last, id
            """
        )
    ).mappings()
    return [
        {
            "document_id": row["id"],
            "semantic_id": row["semantic_id"],
            "link": row["link"],
            "chunk_count": int(row["chunk_count"]),
        }
        for row in rows
    ]


def get_tenant_record(
    conn: Any,
    tenant_columns: list[str],
    document_columns: list[str],
    text_fn: Any,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "table_exists": bool(tenant_columns),
        "columns": tenant_columns,
        "document_record_columns": document_columns,
        "document_record_row_count": 0,
        "rows": [],
    }

    if not tenant_columns:
        return record

    rows = conn.execute(
        text_fn("select * from opensearch_tenant_migration_record")
    ).mappings()
    record["rows"] = [normalize_mapping(dict(row)) for row in rows]

    if document_columns:
        record["document_record_row_count"] = int(
            conn.execute(
                text_fn("select count(*) from opensearch_document_migration_record")
            ).scalar_one()
        )

    return record


def summarize_db_documents(db_documents: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "documents": db_documents,
        "document_count": len(db_documents),
        "total_chunks": sum(doc["chunk_count"] for doc in db_documents),
        "counts_by_document_id": {
            doc["document_id"]: doc["chunk_count"] for doc in db_documents
        },
        "labels_by_document_id": {
            doc["document_id"]: doc.get("semantic_id") or doc.get("link") or doc["document_id"]
            for doc in db_documents
        },
    }


def fetch_opensearch_index(index_name: str) -> dict[str, Any]:
    payload = {
        "size": MAX_OPENSEARCH_DOCS,
        "track_total_hits": True,
        "_source": False,
        "fields": ["document_id", "chunk_index"],
        "query": {"match_all": {}},
    }
    try:
        response = opensearch_request(
            "POST", f"/{index_name}/_search", body=payload, allow_not_found=True
        )
    except RuntimeError as exc:
        return {
            "index_name": index_name,
            "exists": False,
            "error": str(exc),
            "hits": [],
            "truncated": False,
        }

    if response["status"] == 404:
        return {
            "index_name": index_name,
            "exists": False,
            "hits": [],
            "truncated": False,
        }

    hits = response["body"]["hits"]["hits"]
    total = response["body"]["hits"]["total"]
    total_value = int(total["value"] if isinstance(total, dict) else total)
    return {
        "index_name": index_name,
        "exists": True,
        "hits": hits,
        "total_hits": total_value,
        "truncated": total_value > len(hits),
    }


def compare_index_to_db(
    index_data: dict[str, Any], db_summary: dict[str, Any]
) -> dict[str, Any]:
    counts_by_document_id = count_index_chunks(index_data.get("hits", []))
    db_counts = db_summary["counts_by_document_id"]

    missing = sorted(doc_id for doc_id in db_counts if doc_id not in counts_by_document_id)
    extra = sorted(doc_id for doc_id in counts_by_document_id if doc_id not in db_counts)
    mismatched = [
        {
            "document_id": doc_id,
            "db_chunk_count": db_counts[doc_id],
            "index_chunk_count": counts_by_document_id[doc_id],
        }
        for doc_id in sorted(db_counts)
        if doc_id in counts_by_document_id
        and db_counts[doc_id] != counts_by_document_id[doc_id]
    ]

    ready = (
        index_data.get("exists", False)
        and not index_data.get("truncated", False)
        and not missing
        and not extra
        and not mismatched
    )

    return {
        "index_name": index_data["index_name"],
        "exists": index_data.get("exists", False),
        "total_hits": index_data.get("total_hits", len(index_data.get("hits", []))),
        "document_count": len(counts_by_document_id),
        "counts_by_document_id": counts_by_document_id,
        "missing_documents": preview_items(missing),
        "extra_documents": preview_items(extra),
        "mismatched_documents": preview_items(mismatched),
        "missing_document_count": len(missing),
        "extra_document_count": len(extra),
        "mismatched_document_count": len(mismatched),
        "truncated": index_data.get("truncated", False),
        "ready": ready,
    }


def count_index_chunks(hits: list[dict[str, Any]]) -> dict[str, int]:
    chunk_ids_by_doc: dict[str, set[str]] = defaultdict(set)
    raw_counts: dict[str, int] = defaultdict(int)

    for hit in hits:
        fields = hit.get("fields") or {}
        source = hit.get("_source") or {}
        document_id = first_field_value(fields.get("document_id"))
        if document_id is None:
            document_id = source.get("document_id")
        if not document_id:
            continue

        document_id = str(document_id)
        raw_counts[document_id] += 1

        chunk_id = first_field_value(fields.get("chunk_index"))
        if chunk_id is None:
            chunk_id = source.get("chunk_id")
        if chunk_id is not None:
            chunk_ids_by_doc[document_id].add(str(chunk_id))

    counts: dict[str, int] = {}
    for document_id, count in raw_counts.items():
        unique_chunks = chunk_ids_by_doc.get(document_id)
        counts[document_id] = len(unique_chunks) if unique_chunks else count
    return counts


def first_field_value(value: Any) -> Any:
    if isinstance(value, list):
        return value[0] if value else None
    return value


def opensearch_request(
    method: str,
    path: str,
    *,
    body: dict[str, Any] | None = None,
    allow_not_found: bool = False,
) -> dict[str, Any]:
    host = os.environ.get("OPENSEARCH_HOST", "opensearch")
    port = os.environ.get("OPENSEARCH_PORT", DEFAULT_OS_PORT)
    password = os.environ.get("OPENSEARCH_ADMIN_PASSWORD")
    if not password:
        raise RuntimeError("OPENSEARCH_ADMIN_PASSWORD is not set in the container env.")

    url = f"https://{host}:{port}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Authorization", basic_auth_header(DEFAULT_OS_USER, password))
    request.add_header("Content-Type", "application/json")
    request.add_header("Accept", "application/json")

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(request, context=ssl_context, timeout=60) as resp:
            payload = resp.read().decode("utf-8")
            return {
                "status": resp.status,
                "body": json.loads(payload) if payload else {},
            }
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8")
        if allow_not_found and exc.code == 404:
            return {
                "status": exc.code,
                "body": json.loads(body_text) if body_text else {},
            }
        raise RuntimeError(f"OpenSearch request failed: {exc.code} {body_text}") from exc


def basic_auth_header(username: str, password: str) -> str:
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def apply_cutover(
    conn: Any,
    total_chunks: int,
    tenant_columns: list[str],
    text_fn: Any,
) -> None:
    if not tenant_columns:
        raise RuntimeError("opensearch_tenant_migration_record does not exist.")

    row_count = int(
        conn.execute(
            text_fn("select count(*) from opensearch_tenant_migration_record")
        ).scalar_one()
    )
    if row_count == 0:
        conn.execute(text_fn("insert into opensearch_tenant_migration_record default values"))

    updates: dict[str, Any] = {}
    if "enable_opensearch_retrieval" in tenant_columns:
        updates["enable_opensearch_retrieval"] = True
    if "total_chunks_migrated" in tenant_columns:
        updates["total_chunks_migrated"] = total_chunks
    if "total_chunks_errored" in tenant_columns:
        updates["total_chunks_errored"] = 0
    if "total_chunks_in_vespa" in tenant_columns:
        updates["total_chunks_in_vespa"] = total_chunks
    if "approx_chunk_count_in_vespa" in tenant_columns:
        updates["approx_chunk_count_in_vespa"] = total_chunks

    completed_status = resolve_completed_enum_value(
        conn,
        "opensearch_tenant_migration_record",
        "overall_document_migration_status",
        text_fn,
    )
    if completed_status and "overall_document_migration_status" in tenant_columns:
        updates["overall_document_migration_status"] = completed_status

    populated_status = resolve_completed_enum_value(
        conn,
        "opensearch_tenant_migration_record",
        "document_migration_record_table_population_status",
        text_fn,
    )
    if (
        populated_status
        and "document_migration_record_table_population_status" in tenant_columns
    ):
        updates["document_migration_record_table_population_status"] = populated_status

    if not updates:
        return

    set_clause = ", ".join(f"{column} = :{column}" for column in updates)
    conn.execute(
        text_fn(f"update opensearch_tenant_migration_record set {set_clause}"),
        updates,
    )


def resolve_completed_enum_value(
    conn: Any, table: str, column: str, text_fn: Any
) -> str | None:
    row = conn.execute(
        text_fn(
            """
            select data_type, udt_name
            from information_schema.columns
            where table_schema = 'public'
              and table_name = :table_name
              and column_name = :column_name
            """
        ),
        {"table_name": table, "column_name": column},
    ).mappings().first()
    if row is None or row["data_type"] != "USER-DEFINED":
        return None

    labels = [
        value[0]
        for value in conn.execute(
            text_fn(
                """
                select enumlabel
                from pg_enum
                join pg_type on pg_enum.enumtypid = pg_type.oid
                where pg_type.typname = :udt_name
                order by enumsortorder
                """
            ),
            {"udt_name": row["udt_name"]},
        ).fetchall()
    ]

    for candidate in ("COMPLETED", "COMPLETE", "DONE", "SUCCESS", "SUCCEEDED"):
        if candidate in labels:
            return candidate
    return None


def normalize_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in mapping.items():
        if hasattr(value, "isoformat"):
            normalized[key] = value.isoformat()
        else:
            normalized[key] = value
    return normalized


def preview_items(items: list[Any], limit: int = 10) -> list[Any]:
    if len(items) <= limit:
        return items
    preview = items[:limit]
    preview.append({"truncated": len(items) - limit})
    return preview


def render_text_summary(result: dict[str, Any]) -> str:
    if result.get("error"):
        return f"Error: {result['error']}"

    search_settings = result["search_settings"]
    db = result["db"]
    primary = result["indexes"]["primary"]
    alt = result["indexes"]["alt"]
    tenant = result["tenant_record"]

    lines = [
        "Onyx OpenSearch Cutover Audit",
        f"Search settings: id={search_settings['id']} status={search_settings['status']} "
        f"model={search_settings['model_name']} dim={search_settings['model_dim']} "
        f"contextual={search_settings['enable_contextual_rag']}",
        f"DB indexed documents: {db['document_count']} documents / {db['total_chunks']} chunks",
        (
            f"Primary index `{primary['index_name']}`: exists={primary['exists']} "
            f"docs={primary['document_count']} hits={primary['total_hits']} "
            f"missing={primary['missing_document_count']} extra={primary['extra_document_count']} "
            f"mismatched={primary['mismatched_document_count']}"
        ),
        (
            f"Alt index `{alt['index_name']}`: exists={alt['exists']} "
            f"docs={alt['document_count']} hits={alt['total_hits']} "
            f"missing={alt['missing_document_count']} extra={alt['extra_document_count']} "
            f"mismatched={alt['mismatched_document_count']}"
        ),
        f"Active index: {search_settings['active_index_name']}",
        f"Ready for cutover: {result['ready_for_cutover']}",
        f"Tenant migration rows: {len(tenant['rows'])}; document migration rows: {tenant['document_record_row_count']}",
    ]

    if tenant["rows"]:
        current = tenant["rows"][0]
        if "enable_opensearch_retrieval" in current:
            lines.append(
                f"Tenant enable_opensearch_retrieval: {current['enable_opensearch_retrieval']}"
            )

    if primary["missing_document_count"] or primary["mismatched_document_count"]:
        lines.append(
            f"Primary index issues: missing={primary['missing_documents']} mismatched={primary['mismatched_documents']}"
        )
    if alt["missing_document_count"] or alt["mismatched_document_count"]:
        lines.append(
            f"Alt index issues: missing={alt['missing_documents']} mismatched={alt['mismatched_documents']}"
        )
    if primary["extra_document_count"]:
        lines.append(f"Primary extra docs: {primary['extra_documents']}")
    if alt["extra_document_count"]:
        lines.append(f"Alt extra docs: {alt['extra_documents']}")

    if result.get("applied"):
        lines.append("Applied: tenant OpenSearch retrieval enabled.")

    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
