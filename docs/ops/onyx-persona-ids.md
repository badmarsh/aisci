# Onyx Persona and Document Set Registry

_Last verified against live API: 2026-05-30_

> This file is the **authoritative** persona/docset map. Keep it in sync with the live Onyx instance.
> Update it after any persona import, Onyx upgrade, or `POST /api/persona` change.
> The older persona IDs (7, 8) referenced in `onyx-rag-optimization-2026-04-27.md` are **aspirational
> targets that were lost during the v4.0.0-beta.0 transition (2026-05-20)**. They must be recreated.

---

## Active Personas (Live — 2026-05-30)

| ID | Name | Public | Doc Sets | Tools | Model Config | Health |
|----|------|--------|----------|-------|-------------|--------|
| 0 | **Assistant** | ✅ Yes | none | generate_image, web_search, open_url, read_file, python | id=126 | ✅ OK |
| 1 | Scientific Researcher | ❌ No | Chemistry | internal_search, open_url, search, search_literature, search_patents, search_clinical_trials, get_clinical_trial, search_grants, get_grant, get_510k_summary, search_device510k, … | none | ⚠️ No model cfg |
| 2 | **physics-validator** | ✅ Yes | Robert Corpus | _(none)_ | none | ❌ BROKEN — no model, no tools |
| 3 | **arxiv-intake** | ❌ No | arXiv Auto — Quarantine | _(none)_ | none | ⚠️ No model cfg |

### ⚠️ Critical Gaps (personas from v4 transition that are missing)

The following personas existed in the pre-v4 deployment and are referenced in
`docs/ops/onyx-rag-optimization-2026-04-27.md`. They were **wiped during the v4.0.0-beta.0
upgrade on 2026-05-20** and need to be recreated. See GitHub Issue **#F-persona-rebuild**.

| Target ID (old) | Name | Why Needed |
|---|---|---|
| 7 | Physics Validation Mode | HEP workflow with source-routing guardrails, Scite/Consensus/HEP tools, claim-tier enforcement |
| 3 (new target) | Science Deep-Dive Mode | Literature scout, same HEP tools, role distinct from Physics Validation Mode |
| 8 | AiSci Wiki Agent | Needs `read_file` (id=9) so it can verify `evidence-ledger.md` before writing wiki output |

---

## Active Document Sets (Live — 2026-05-30)

| DS ID | Name | Public | Connectors | Notes |
|-------|------|--------|------------|-------|
| 1 | Chemistry | ❌ Private | — | Used by Scientific Researcher only |
| 2 | **Robert Corpus** | ⚠️ **PUBLIC** | — | **Should be Private** — contains pre-publication HEP research |
| 3 | arXiv Auto — Quarantine | ❌ Private | — | Used by arxiv-intake persona |
| 4 | Scite Citations | ✅ Public | — | Acceptable if Scite content is not sensitive |

### ⚠️ Missing Document Sets

| Name | Was DS ID | Status | Action |
|------|-----------|--------|--------|
| HEP Phenomenology References | 6 (old) | **Deleted** during v4 transition | Recreate and add Tsallis/Blast-Wave baselines |
| Robert Boson Draft | — (old) | **Deleted** | Recreate if manuscript PDF is current |

---

## Assistant Persona Guardrails (id=0)

**Keep:** `generate_image`, `web_search`, `open_url`, `read_file`, `python`

**Must NOT have:**
- `internal_search` unless anchored to an explicit document set
- HEP MCP tools (`hep_arxiv`, `hep_inspire`, `hepdata`) without grounding doc sets

---

## Physics Validator Persona Guardrails (id=2 — needs rebuilding)

**Should have:**
- **Doc sets:** Robert Corpus, HEP Phenomenology References, Robert Boson Draft
- **Tools:** `internal_search`, `read_file`, `code_interpreter`, Scite MCP, Consensus MCP, `hep_arxiv` (id=28), `hep_inspire` (id=29), `hepdata` (id=30)
- **Model config:** Must assign a working LLM (currently NULL → all chats 404)
- **Prompt guardrails:** Source-routing block (canon files via `read_file`, RAG only for literature grounding), Bose-Einstein/Boltzmann-Jüttner wording, chi²/ndf gate, baseline gate

---

## Tool ID Reference (last confirmed 2026-05-30)

| Tool ID | Name | In-Code ID |
|---------|------|-----------|
| 2 | generate_image | ImageGenerationTool |
| 3 | web_search | WebSearchTool |
| 6 | python / Code Interpreter | PythonTool |
| 7 | open_url | OpenURLTool |
| 9 | read_file | FileReaderTool |
| 28 | hep_arxiv | (MCP custom) |
| 29 | hep_inspire | (MCP custom) |
| 30 | hepdata | (MCP custom) |

---

## RAG Evaluation Status (2026-05-30)

| Question | Target Persona | Status | Notes |
|----------|---------------|--------|-------|
| Q1 — Blast-Wave parameters | physics-validator (id=2) | ❌ FAIL — HTTP 404 | Persona has no model config |
| Q2 — Tsallis-Pareto vs BJ | physics-validator (id=2) | ❌ FAIL — HTTP 404 | Same — no model |
| Q3 — OpenSearch parity command | physics-validator (id=2) | ❌ FAIL — HTTP 404 | Same — no model |
| Q4 — Visual table extraction | physics-validator (id=2) | ⏭️ Skipped | Vision model also misconfigured |
| Q5 — RAG-vs-Canon boundary | physics-validator (id=2) | ❌ FAIL — HTTP 404 | Same — no model |

**All RAG eval questions fail because `physics-validator` has no model configuration.**
Assign a model and re-run the eval set once the persona is rebuilt.
