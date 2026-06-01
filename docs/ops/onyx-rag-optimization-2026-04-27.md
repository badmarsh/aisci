# Onyx RAG Optimization — 2026-04-27

This document captures the RAG-vs-canon source-routing boundary, persona audit findings, and retrieval-stack decisions made on 2026-04-27. It is the live reference for any future persona sync, prompt change, or retrieval-cutover decision. Do not put scientific claim conclusions here; those belong in `research/robert/evidence-ledger.md`.

## RAG-vs-Canon Routing Boundary

The Onyx retrieval stack (`internal_search`) is for **grounding external literature and project documents in the indexed corpus**. It must NOT be queried for questions whose authoritative answer lives in a tracked canonical file. Routing `internal_search` at a canon file question produces hallucinated or stale answers because the index is a lagging, chunked copy.

| Question type | Correct source | Must NOT use |
|---|---|---|
| Claim status, evidence tier, next gate | `research/robert/evidence-ledger.md` (read directly via `read_file`) | `internal_search` |
| Active fit parameters, run artifacts | `research/robert/runs/<dated-run>/` (read directly) | `internal_search` |
| Platform task status, port bindings | `docs/ops/platform-backlog.md` (read directly) | `internal_search` |
| HEP literature context, paper abstracts | `internal_search` → Scite / Consensus / arXiv / INSPIRE | canonical files |
| pT spectra, HEPData tables | `hepdata` tool → `physics/data/` | `internal_search` |
| Formula retrieval from manuscript | `read_file` on manuscript export | `internal_search` |

This boundary is enforced via the **source-routing block** in the HEP validation persona's system prompt (see `onyx-persona-ids.md` for the current persona ID). Re-check the prompt after any persona import or upstream Onyx upgrade.

## RAG Audit Findings (2026-04-27)

### Structural scoping failures

The following RAG audit IDs were classified as **structural failures** (wrong source selected by the agent), not model failures:

| ID | Root cause | Resolution |
|---|---|---|
| RAG-07 | Agent used `internal_search` for `evidence-ledger.md` claim status | Source-routing block added to Physics Validation Mode prompt |
| RAG-08 | Agent used `internal_search` for fit run artifact content | Same fix |
| RAG-09 | Agent used `internal_search` for claim tier promotion check | Same fix |
| RAG-10 | Agent used `internal_search` for manuscript equation lookup | Same fix |
| RAG-11 | Agent used `internal_search` for backlog task status | Same fix |
| RAG-24 | Science Deep-Dive Mode retrieved stale persona-level context via internal search | Scope narrowed; RAG-vs-canon boundary added to persona id `3` prompt |
| RAG-25 | Assistant persona (id `0`) queried HEP tools with no grounding doc sets | HEP tools removed from persona id `0` |

### Document-set seeding findings

| ID | Finding | Action |
|---|---|---|
| RAG-12 | Physics doc set lacked core HEP phenomenology references | Seeded and verified |
| RAG-13 | HEP Phenomenology References set lacked arXiv/INSPIRE grounding | Seeded and verified |
| RAG-14 | Tsallis and Blast-Wave baseline literature absent from RAG corpus | Seeded and verified |
| RAG-15 | Small-system radial-flow gap in HEP set | Partially closed — see `platform-backlog.md` |
| RAG-19 | Citation-context gap for Consensus-retrieved papers | Partially closed — see `platform-backlog.md` |

> **Persona state moved.** The persona/tool tables that used the pre-v4 IDs
> (7, 8) once lived here. Current personas, doc sets, and tool IDs are tracked in
> `onyx-persona-ids.md` — refer there. The source-routing and claim-wording
> guardrails above remain the design intent for any HEP persona.

## Retrieval-Stack Status (2026-05-02)

- **Embedding model**: `Alibaba-NLP/gte-Qwen2-1.5B-instruct`, `EMBEDDING_DIM=1536` — active Alibaba/OpenSearch retrieval target for both `inference_model_server` and `indexing_model_server`
- **Primary retrieval**: Vespa (active)
- **OpenSearch active index**: `danswer_chunk_alibaba_nlp_gte_qwen2_1_5b_instruct`; parity gate is green as of 2026-05-02 with `279` documents, `629` chunks, and `0` missing, mismatched, or extra documents. Keep `deployment/helper/onyx_opensearch_cutover.py --json` as the regression check after future reindexes or backend recreates.
- **LiteLLM contextual-summary timeout**: raised to `timeout=300`, `retry_after=10` to unblock indexing of large local models
- **Ollama models required**: `gemma2:27b` (weight-1 fallback in `qwen-cloud-fast`), `qwen2.5:32b`, and `qwen2.5vl:7b`. `nomic-embed-text:latest` remains useful for rollback but is no longer the active rebuild embedding target.

## Routing Rules — Future Change Protocol

Before modifying the source-routing boundary or persona prompt:
1. Document the change rationale in `docs/decisions/` as a new ADR.
2. Update the routing table in this file.
3. Re-run the affected RAG audit IDs against the updated prompt.
4. Update `platform-backlog.md` with the new status.

Before adding or removing a document set:
1. Verify the connector is syncing and the chunk count is stable.
2. Record the doc-set ID and connector pair in `platform-backlog.md`.
3. Run at least one representative query per persona that uses that set and record pass/fail in the backlog.
