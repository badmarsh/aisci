# Onyx Persona IDs
# Last updated: 2026-05-02 — onyx-configure run; system prompts applied, LLM overrides corrected
# Do not edit manually — update by running the configure prompt in docs/ops/onyx-configure.md

## Core Research Personas

| Persona | ID | LLM Override | Is Public |
|---|---|---|---|
| physics-validator | 9 | *(default — qwen-cloud-fast)* | true |
| evidence-auditor | 10 | qwen2.5:32b | true |
| referee-prep | 11 | *(default — qwen-cloud-fast)* | true |
| arxiv-intake | 12 | *(default — qwen-cloud-fast)* | false |

## Supporting Personas

| Persona | ID | Notes |
|---|---|---|
| workflow-auditor | 13 | AiSci GitHub + Internal Whitepapers |
| AiSci Wiki Agent | 8 | Private; no doc sets |
| Science Deep-Dive Mode | 3 | HEP Phenomenology References |
| Physics Validation Mode | 7 | HEP Phenomenology References |

## Document Sets

| Name | ID | Public | Notes |
|---|---|---|---|
| Robert Corpus | 11 | false | Manuscript PDF + corpus papers; file connector |
| arXiv Auto — Quarantine | 12 | false | Gate: arxiv-intake triage required before promotion |
| Scite Citations | 13 | true | Label only — no indexed docs; used in persona prompts |
| HEP Phenomenology References | 6 | false | Tsallis_statistics + HEP Native API Sources connectors |
| AiSci GitHub | 39 | false | GitHub connector (no path filter — full repo) |
| Internal Whitepapers | 40 | false | AI/Science PDF connector |
| Gretka - testing | 2 | false | Active working set for Grétenka group — not an orphan |

## Tools

| Name | ID | Notes |
|---|---|---|
| internal_search | 1 | Onyx RAG search |
| generate_image | 2 | ⚠ Dead — Vertex AI providers have no API keys; remove from Assistant |
| web_search | 3 | General web search |
| search_literature | 11 | Scite MCP via proxy |
| search | 12 | Consensus MCP via proxy |
| open_url | 7 | URL fetcher |
| hep_arxiv | 28 | HEP arXiv readonly |
| hep_inspire | 29 | HEP INSPIRE readonly |
| hepdata | 30 | HEPData readonly |

## Deleted Sets

| Name | Former ID | Deleted | Reason |
|---|---|---|---|
| Physics | 1 | 2026-05-02 | Legacy duplicate of Robert Corpus; self-described as such |

## Change Log

| Date | Change |
|---|---|
| 2026-05-02 | System prompts applied to personas 9/10/11/12 (were empty); LLM overrides corrected on 9/11/12 (gemma2:2b → default); HEP Phenomenology References (id=6) flipped private; Physics (id=1) deleted |
| 2026-04-30 | Initial persona IDs recorded after first configure run |
