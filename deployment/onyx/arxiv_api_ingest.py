#!/usr/bin/env python3
"""Ingest arXiv papers via the arXiv Atom API into Onyx.

Replaces the recursive Web Connector (connector ID 18) that scraped arXiv
search result pages and followed author links into infinite recursion,
causing hundreds of rate-limit errors.

Run inside the Onyx API container:
    docker exec onyx-api_server-1 python /workspace/aisci/deployment/onyx/arxiv_api_ingest.py

Usage:
    --query "all:Juettner distribution heavy ion"  # default
    --max-results 50
    --start 0
    --cc-pair-id 15              # existing arXiv Auto CC Pair
    --verify                     # HTTP-test the arXiv query first
"""

from __future__ import annotations

import argparse
import html
import json
import textwrap
import xml.etree.ElementTree as ET
from datetime import datetime
from datetime import timezone
from typing import Any

import requests

from onyx.configs.constants import DocumentSource
from onyx.connectors.models import DocumentBase
from onyx.connectors.models import TextSection
from onyx.db.engine.sql_engine import SqlEngine
from onyx.db.engine.sql_engine import get_session_with_tenant
from onyx.db.enums import AccessType
from onyx.db.enums import ConnectorCredentialPairStatus
from onyx.db.enums import ProcessingMode
from onyx.db.models import Connector
from onyx.db.models import ConnectorCredentialPair
from onyx.db.models import Credential
from onyx.db.models import DocumentSet
from onyx.db.models import DocumentSet__ConnectorCredentialPair
from onyx.server.onyx_api.ingestion import IngestionDocument
from onyx.server.onyx_api.ingestion import upsert_ingestion_doc
from shared_configs.configs import POSTGRES_DEFAULT_SCHEMA_STANDARD_VALUE
from shared_configs.contextvars import CURRENT_TENANT_ID_CONTEXTVAR

USER_AGENT = "aisci-arxiv-api-ingest/0.1"
DEFAULT_QUERY = "all:Juttner distribution"
DEFAULT_MAX_RESULTS = 50
ARXIV_API_URL = "https://export.arxiv.org/api/query"
ARXIV_CONNECTOR_NAME = "arXiv API Connector"
ARXIV_DOCUMENT_SET_NAME = "arXiv Auto — Quarantine"


def _request_atom(url: str, max_retries: int = 3) -> str:
    """GET an arXiv Atom feed with retries and back-off."""
    for attempt in range(max_retries):
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
        if response.status_code == 429:
            wait = min(30 * (2 ** attempt), 120)
            print(f"arXiv rate-limited (429); waiting {wait}s")
            import time

            time.sleep(wait)
            continue
        response.raise_for_status()
        return response.text
    raise RuntimeError(f"Max retries exceeded for {url}")


def _parse_atom_feed(atom_text: str) -> list[dict[str, Any]]:
    """Parse arXiv Atom XML into a list of paper dicts."""
    root = ET.fromstring(atom_text)
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }

    papers = []
    for entry in root.findall("atom:entry", ns):

        def find_text(path: str) -> str:
            node = entry.find(path, ns)
            return " ".join((node.text or "").split()) if node is not None else ""

        authors = [
            entry.findtext("atom:name", default="", namespaces=ns)
            for entry in entry.findall("atom:author", ns)
        ]
        authors = [a.strip() for a in authors if a.strip()]

        links = [link.attrib for link in entry.findall("atom:link", ns)]
        pdf_link = next(
            (l.get("href") for l in links if l.get("title") == "pdf"),
            None,
        )
        abs_link = find_text("atom:id")

        primary_category = ""
        pc_node = entry.find("arxiv:primary_category", ns)
        if pc_node is not None:
            primary_category = pc_node.attrib.get("term", "")

        papers.append(
            {
                "id": abs_link.replace("http://arxiv.org/abs/", ""),
                "title": find_text("atom:title"),
                "summary": find_text("atom:summary"),
                "published": find_text("atom:published"),
                "updated": find_text("atom:updated"),
                "journal_ref": find_text("arxiv:journal_ref"),
                "doi": find_text("arxiv:doi"),
                "primary_category": primary_category,
                "authors": authors,
                "pdf_url": pdf_link,
                "abs_url": abs_link,
            }
        )
    return papers


def _arxiv_doc(paper: dict[str, Any]) -> DocumentBase:
    """Convert a parsed arXiv paper into an Onyx DocumentBase."""
    arxiv_id = paper["id"]
    return DocumentBase(
        id=f"arxiv-api-{arxiv_id}",
        semantic_identifier=paper["title"],
        title=paper["title"],
        source=DocumentSource.INGESTION_API,
        metadata={
            "source_type": "arxiv_api",
            "arxiv_id": arxiv_id,
            "doi": paper.get("doi", ""),
            "journal_ref": paper.get("journal_ref", ""),
            "primary_category": paper.get("primary_category", ""),
            "authors": paper.get("authors", []),
        },
        doc_updated_at=datetime.now(timezone.utc),
        sections=[
            TextSection(
                text=textwrap.dedent(
                    f"""\
                    arXiv paper (ingested via API, not web scraping)
                    arXiv ID: {arxiv_id}
                    Title: {paper['title']}
                    Authors: {', '.join(paper['authors'])}
                    Published: {paper['published']}
                    Updated: {paper['updated']}
                    DOI: {paper['doi']}
                    Journal ref: {paper['journal_ref']}
                    Primary category: {paper['primary_category']}
                    PDF: {paper['pdf_url']}
                    Abstract:
                    {paper['summary']}
                    """
                ).strip(),
                link=paper["abs_url"],
            ),
        ],
    )


def _ensure_arxiv_connector(db_session: Any) -> ConnectorCredentialPair:
    """Create or update the arXiv API connector + CC pair.

    Replaces the old Web Connector (ID 18, recursive scraper) with an
    INGESTION_API connector that receives documents from this script.
    """
    connector = db_session.query(Connector).filter(
        Connector.name == ARXIV_CONNECTOR_NAME,
        Connector.source == DocumentSource.INGESTION_API,
    ).first()

    if connector is None:
        connector = Connector(
            name=ARXIV_CONNECTOR_NAME,
            source=DocumentSource.INGESTION_API,
            input_type="load_state",
            connector_specific_config={},
            refresh_freq=None,
            prune_freq=None,
        )
        db_session.add(connector)
        db_session.flush()
        print(f"Created connector: {ARXIV_CONNECTOR_NAME} (id={connector.id})")
    else:
        print(f"Using existing connector: {ARXIV_CONNECTOR_NAME} (id={connector.id})")

    credential = db_session.query(Credential).get(0)
    if credential is None:
        raise RuntimeError("Default credential id 0 was not found")

    cc_pair = db_session.query(ConnectorCredentialPair).filter(
        ConnectorCredentialPair.connector_id == connector.id,
        ConnectorCredentialPair.credential_id == credential.id,
    ).first()

    if cc_pair is None:
        cc_pair = ConnectorCredentialPair(
            name="arXiv API CC Pair",
            connector_id=connector.id,
            credential_id=credential.id,
            status=ConnectorCredentialPairStatus.ACTIVE,
            access_type=AccessType.PUBLIC,
            processing_mode=ProcessingMode.REGULAR,
            auto_sync_options=None,
            indexing_trigger=None,
        )
        db_session.add(cc_pair)
        db_session.flush()
        print(f"Created CC pair (id={cc_pair.id})")
    else:
        print(f"Using existing CC pair (id={cc_pair.id})")

    # Link to document set
    ds = db_session.query(DocumentSet).filter(
        DocumentSet.name == ARXIV_DOCUMENT_SET_NAME,
    ).first()
    if ds is None:
        raise RuntimeError(f"Document set not found: {ARXIV_DOCUMENT_SET_NAME}")

    existing = db_session.query(DocumentSet__ConnectorCredentialPair).filter_by(
        document_set_id=ds.id,
        connector_credential_pair_id=cc_pair.id,
        is_current=True,
    ).first()
    if existing is None:
        db_session.add(
            DocumentSet__ConnectorCredentialPair(
                document_set_id=ds.id,
                connector_credential_pair_id=cc_pair.id,
                is_current=True,
            )
        )
    ds.is_up_to_date = False
    db_session.flush()
    return cc_pair


def ingest_arxiv_papers(query: str, max_results: int, start: int, cc_pair_id: int) -> None:
    """Query arXiv API and ingest results into Onyx."""
    query_encoded = query.replace(" ", "+")
    url = f"{ARXIV_API_URL}?search_query={query_encoded}&start={start}&max_results={max_results}"

    print(f"Querying arXiv API: {url}")
    atom_text = _request_atom(url)
    papers = _parse_atom_feed(atom_text)
    print(f"Found {len(papers)} papers from arXiv API")

    if not papers:
        print("No papers found — nothing to ingest.")
        return

    token = CURRENT_TENANT_ID_CONTEXTVAR.set(POSTGRES_DEFAULT_SCHEMA_STANDARD_VALUE)
    try:
        SqlEngine.init_engine(
            pool_size=5,
            max_overflow=2,
            app_name="aisci_arxiv_api_ingest",
        )
        with get_session_with_tenant(
            tenant_id=POSTGRES_DEFAULT_SCHEMA_STANDARD_VALUE,
        ) as db_session:
            for paper in papers:
                doc = _arxiv_doc(paper)
                result = upsert_ingestion_doc(
                    IngestionDocument(document=doc, cc_pair_id=cc_pair_id),
                    None,
                    db_session,
                )
                status = "existed" if result.already_existed else "new"
                print(f"  [{status}] {paper['id']}: {paper['title'][:80]}")

            db_session.commit()
            print(f"Ingested {len(papers)} papers into Onyx (cc_pair_id={cc_pair_id})")
    finally:
        CURRENT_TENANT_ID_CONTEXTVAR.reset(token)


def verify_query(query: str, max_results: int = 3) -> None:
    """Dry-run: query arXiv API and print paper summaries without ingesting."""
    query_encoded = query.replace(" ", "+")
    url = f"{ARXIV_API_URL}?search_query={query_encoded}&start=0&max_results={max_results}"
    print(f"Verifying arXiv query: {url}")
    atom_text = _request_atom(url)
    papers = _parse_atom_feed(atom_text)
    print(f"Found {len(papers)} papers:")
    for p in papers:
        print(f"  - [{p['id']}] {p['title'][:100]} ({', '.join(p['authors'][:3])})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest arXiv papers into Onyx via the arXiv Atom API",
    )
    parser.add_argument("--query", default=DEFAULT_QUERY, help="arXiv search query")
    parser.add_argument(
        "--max-results",
        type=int,
        default=DEFAULT_MAX_RESULTS,
        help="Max papers to fetch",
    )
    parser.add_argument("--start", type=int, default=0, help="Start offset")
    parser.add_argument(
        "--cc-pair-id",
        type=int,
        default=None,
        help="Existing CC pair ID (default: create one)",
    )
    parser.add_argument("--verify", action="store_true", help="Dry-run mode")
    args = parser.parse_args()

    if args.verify:
        verify_query(args.query, max_results=min(args.max_results, 5))
        return

    if args.cc_pair_id is not None:
        print(f"Using existing CC pair ID: {args.cc_pair_id}")
        cc_pair_id = args.cc_pair_id
    else:
        token = CURRENT_TENANT_ID_CONTEXTVAR.set(POSTGRES_DEFAULT_SCHEMA_STANDARD_VALUE)
        try:
            SqlEngine.init_engine(
                pool_size=5,
                max_overflow=2,
                app_name="aisci_arxiv_api_ingest",
            )
            with get_session_with_tenant(
                tenant_id=POSTGRES_DEFAULT_SCHEMA_STANDARD_VALUE,
            ) as db_session:
                cc_pair = _ensure_arxiv_connector(db_session)
                cc_pair_id = cc_pair.id
                db_session.commit()
        finally:
            CURRENT_TENANT_ID_CONTEXTVAR.reset(token)

    ingest_arxiv_papers(args.query, args.max_results, args.start, cc_pair_id)


if __name__ == "__main__":
    main()
