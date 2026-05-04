# ADR: arXiv Connector — API over Web Scraping

**Date:** 2026-05-04
**Status:** Accepted
**Context:** Onyx ingestion, arXiv literature seeding for AiSci research pipeline

## Problem

The existing arXiv connector (connector ID 18, `arXiv Auto Connector`) used Onyx's recursive web scraper (`WebConnector` with `web_connector_type=recursive`). It was seeded from:

```
https://arxiv.org/search/?searchtype=all&query=Juettner+distribution+heavy+ion
```

The recursive scraper extracted all `<a href>` links from each page and followed them. On arXiv search result pages, author names are links to new search pages (`/search/?searchtype=author&query=AuthorName%2C+Initial`), causing:

- **Infinite recursion**: Each author page generates more author links
- **Hundreds of failed scrapes**: arXiv rate-limits the aggressive Playwright-based scraping
- **Useless documents**: Author search pages are not research papers
- **Error noise**: `litellm.InternalServerError: Connection error` flooded logs

## Decision

Replace the recursive web connector with a direct arXiv API integration.

**Implementation:** `deployment/onyx/arxiv_api_ingest.py`

- Queries `https://export.arxiv.org/api/query` (Atom XML API)
- Parses structured paper metadata: title, authors, abstract, DOI, categories, PDF URL
- Ingests documents via Onyx's ingestion API (`upsert_ingestion_doc`)
- Uses `INGESTION_API` connector source (structured push, no scraping)
- Supports `--verify` dry-run mode and `--query`/`--max-results` parameters
- Default query: `all:Juttner distribution`

## Consequences

### Positive
- **No recursion**: Each query returns exactly the papers requested
- **Structured data**: Abstract, authors, DOI, categories — not parsed HTML
- **Fast**: HTTP GET vs Playwright headless Chrome rendering
- **No rate-limiting**: arXiv API is designed for programmatic access
- **Reproducible**: Query parameters are explicit and auditable

### Negative
- **Manual trigger**: The ingest script must be run explicitly (no automatic scheduling). This is acceptable for now since literature ingestion is a periodic activity, not continuous.

### Trade-offs considered

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **arXiv API** (chosen) | Structured, fast, no rate limits, already partially implemented via `hep_arxiv` tool | Manual trigger | ✅ Selected |
| MCP server wrapping arXiv API | Would add another tool interface | Redundant — `hep_arxiv` OpenAPI tool already wraps the same API for persona-level use | ❌ Rejected |
| Fixed web connector (single-page mode) | Simpler code change | Still scrapes HTML, gets no structured metadata, fragile to arXiv layout changes | ❌ Rejected |
| Full arXiv OAI-PMI harvester | Complete coverage | Overkill for the specific Jüttner-distribution research scope | ❌ Rejected |

## Implementation details

- **New connector**: ID 21 (`arXiv API Connector`, source: INGESTION_API)
- **New CC pair**: ID 18 (`arXiv API CC Pair`)
- **Old connector**: CC pair ID 15 set to DELETING, unlinked from document sets
- **Document sets**: `arXiv Auto — Quarantine` and `Scite Citations` now use the new connector
- **Ingested**: 20 papers (initial run with `--max-results 20`)

## Related

- `hep_arxiv` tool (tool ID 28) — OpenAPI tool for interactive persona-level arXiv queries, shares the same API endpoint
- `deployment/onyx/hep_readonly_tools.py` — creates the `hep_arxiv`, `hep_inspire`, `hepdata` tools and baseline HEP documents
