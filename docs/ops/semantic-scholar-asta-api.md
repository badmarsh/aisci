# Historical Semantic Scholar & Asta API Record

> Historical record only — not active operational guidance.

> **Not active control-plane configuration.** The proxy route described below
> is absent from the current checkout. Retained for historical context only.

Added 2026-06-03. Keys approved for Marek; see `.env` for `SEMANTICSCHOLAR_API_KEY` and `ASTA_API_KEY`.

Both APIs are routed through the nginx MCP proxy. Keep keys out of docs and commits.

---

## Semantic Scholar Academic Graph API

**Base URL (via proxy):** `http://onyx-mcp-proxy:80/semanticscholar/graph/v1`  
**Base URL (direct):** `https://api.semanticscholar.org/graph/v1`  
**Auth:** `x-api-key: $SEMANTICSCHOLAR_API_KEY` header  
**Rate limit:** 1 req/s (our tier). Always `time.sleep(1)` between calls.  
**Source:** https://api.semanticscholar.org/api-docs/graph

### Three separate APIs — pick the right one

| API group | Base path | Use for |
|---|---|---|
| **Academic Graph** | `/graph/v1/` | Paper lookup, citation/reference traversal, author lookup, paper search |
| **Recommendations** | `/recommendations/v1/` | "More like this" given paper IDs |
| **Datasets** | `/datasets/v1/` | Bulk corpus downloads (not for live queries) |

> **Do not mix up the three.** The session prompt previously used `/graph/v1/paper/search` with Recommendations-style framing — those are different APIs.

---

### Paper Data endpoints

All return JSON. `paperId` is always present; all other fields are opt-in via `?fields=`.

#### GET `/paper/{paper_id}` — single paper lookup

Supported ID formats (prefix:value):
- `ARXIV:1110.5526` — arXiv ID
- `DOI:10.1103/PhysRevC.87.014907` — DOI
- `PMID:19872477` — PubMed
- `PMCID:2323736` — PMC
- `CorpusId:215416146` — S2 numeric ID
- `<sha>` — S2 hex ID (40 chars)

Available `fields`:
```
paperId, corpusId, externalIds, url, title, abstract, venue, publicationVenue,
year, referenceCount, citationCount, influentialCitationCount, isOpenAccess,
openAccessPdf, fieldsOfStudy, s2FieldsOfStudy, publicationTypes,
publicationDate, journal, citationStyles, authors, citations, references,
embedding, tldr
```

Subfields (use dot notation): `citations.title`, `citations.abstract`, `citations.year`,
`authors.name`, `authors.hIndex`, `embedding.specter_v2`

**Example:**
```python
import requests, time, os
r = requests.get(
    "https://api.semanticscholar.org/graph/v1/paper/ARXIV:1110.5526",
    params={"fields": "title,year,citationCount,abstract,tldr"},
    headers={"x-api-key": os.environ["SEMANTICSCHOLAR_API_KEY"]}
)
# Returns: {"paperId": "...", "title": "...", "year": 2012, "citationCount": N, ...}
time.sleep(1)
```

---

#### GET `/paper/{paper_id}/citations` — who cites this paper

Returns paginated list. Each entry is a `{"citingPaper": {...}}` object.

```python
r = requests.get(
    "https://api.semanticscholar.org/graph/v1/paper/ARXIV:1110.5526/citations",
    params={"fields": "title,year,abstract,externalIds", "limit": 100},
    headers={"x-api-key": ...}
)
data = r.json()  # {"offset": 0, "next": 100, "data": [{"citingPaper": {...}}, ...]}
```

> Pagination: if `"next"` key is present, repeat with `offset=data["next"]`.

---

#### GET `/paper/{paper_id}/references` — what this paper cites

Same structure as citations but each entry is `{"citedPaper": {...}}`.

---

#### GET `/paper/search` — relevance search (max 1000 results)

Plain-text query against title+abstract. No special syntax. Useful filters:
- `year=2020-2026` — publication year range
- `fieldsOfStudy=Physics` — restrict to field
- `openAccessPdf` — only papers with public PDF
- `minCitationCount=5` — exclude low-impact
- `publicationTypes=JournalArticle,Review`
- `venue=Physical Review C`

```python
r = requests.get(
    "https://api.semanticscholar.org/graph/v1/paper/search",
    params={
        "query": "Tsallis distribution pseudorapidity rapidity pion ALICE",
        "fields": "title,abstract,year,externalIds,citationCount,openAccessPdf",
        "fieldsOfStudy": "Physics",
        "year": "2012-2026",
        "limit": 10
    },
    headers={"x-api-key": ...}
)
# Returns: {"total": N, "offset": 0, "next": 10, "data": [...]}
```

---

#### GET `/paper/search/bulk` — boolean bulk search (up to 10M papers)

Supports boolean syntax: `+` AND, `|` OR, `-` NOT, `"phrase"`, `*` prefix, `~N` fuzzy.

```python
r = requests.get(
    "https://api.semanticscholar.org/graph/v1/paper/search/bulk",
    params={
        "query": '"Tsallis distribution" + pseudorapidity',
        "fields": "title,year,externalIds",
        "sort": "citationCount:desc"
    },
    headers={"x-api-key": ...}
)
# Returns: {"total": N, "token": "...", "data": [...]}
# Paginate: repeat with &token=data["token"]
```

> **Note:** bulk search does NOT return nested citations/references. Use `/paper/{id}/citations` for those.

---

#### GET `/paper/search/match` — single best title match

Returns the one paper whose title best matches the query. Returns 404 if no match.

```python
r = requests.get(
    "https://api.semanticscholar.org/graph/v1/paper/search/match",
    params={"query": "The Tsallis Distribution in Proton-Proton Collisions"},
    headers={"x-api-key": ...}
)
# Returns single paper with matchScore field
```

---

#### POST `/paper/batch` — fetch up to 500 papers at once

```python
r = requests.post(
    "https://api.semanticscholar.org/graph/v1/paper/batch",
    params={"fields": "title,year,citationCount,abstract"},
    json={"ids": ["ARXIV:1110.5526", "ARXIV:nucl-th/0305084"]},
    headers={"x-api-key": ...}
)
```

---

### Author Data endpoints

#### GET `/author/{author_id}` — author details
#### GET `/author/{author_id}/papers` — paginated paper list  
#### GET `/author/search?query=name` — search by name
#### POST `/author/batch` — up to 1000 authors at once

Available author `fields`: `name, aliases, affiliations, homepage, paperCount, citationCount, hIndex, papers`

---

## Asta Scientific Corpus Tool (Allen AI)

**Base URL (via proxy):** `http://onyx-mcp-proxy:80/asta/`  
**Base URL (direct):** `https://asta-tools.allen.ai/mcp/v1`  
**Auth:** `x-api-key: $ASTA_API_KEY` header  
**Rate limit:** 1 req/s  
**Protocol:** MCP (Model Context Protocol) — JSON-RPC style, not REST  
**Corpus:** 200M+ papers with full-text search capability  
**Source:** https://allenai.org (Ai2)

### Key difference from Semantic Scholar

Asta has **full-text snippet search** — it searches inside the body of papers, not just
title and abstract. Use Asta when you need to find specific passages, equations, or
methodological details that may not appear in abstracts.

### Primary tools

#### `get_paper` — retrieve paper by ID

Supported ID formats: S2 hash, CorpusId, DOI, arXiv ID, PMID, PMCID, URLs.

```json
{
  "tool": "get_paper",
  "params": {
    "paper_id": "arXiv:1110.5526",
    "fields": "title,abstract,tldr,year,authors"
  }
}
```

#### `search_snippets` — full-text search returning passages

Returns text passages from inside papers, with source citation.
Unique capability — Semantic Scholar does not have this.

```json
{
  "tool": "search_snippets",
  "params": {
    "query": "Tsallis distribution rapidity pseudorapidity Jacobian dy deta pion",
    "limit": 5
  }
}
```

Response includes: snippet text, paper title, arXiv ID, publication year, DOI.

---

## Which API to use for which task

| Task | Use |
|---|---|
| Look up a paper by arXiv ID | S2 `/paper/ARXIV:{id}` |
| Get citation count and TLDR | S2 `/paper/{id}?fields=citationCount,tldr` |
| Find who cites a paper | S2 `/paper/{id}/citations` |
| Find what a paper cites | S2 `/paper/{id}/references` |
| Search by topic/keyword (title+abstract) | S2 `/paper/search` |
| Boolean full-corpus bulk search | S2 `/paper/search/bulk` |
| Best single match for a title | S2 `/paper/search/match` |
| Search *inside* paper bodies for passages | **Asta** `search_snippets` |
| Get paper details with full-text context | **Asta** `get_paper` |
| Find papers mentioning an equation or method not in abstract | **Asta** `search_snippets` |

---

## Endpoint status

| Service | Proxy route | Auth | Status |
|---|---|---|---|
| Semantic Scholar | `http://127.0.0.1:8095/semanticscholar/` → `https://api.semanticscholar.org/` | `x-api-key` | ✅ Key approved 2026-06-02 |
| Asta | `http://127.0.0.1:8095/asta/` → `https://asta-tools.allen.ai/mcp/v1/` | `x-api-key` | ✅ Key approved 2026-06-02 |

Both pass through the hardened MCP proxy (TLS 1.2/1.3, `ssl_verify on`) per AIS-66.
