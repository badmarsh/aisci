# Onyx Persona IDs

- physics-validator: 2
- evidence-auditor: 5
- referee-prep: 6
- arxiv-intake: 3

<<<<<<< Updated upstream
> This file is the **authoritative** persona/docset map. Keep it in sync with the live Onyx instance;
> update it after any persona import, Onyx upgrade, or `POST /api/persona` change.
> _Reconciled with the 2026-05-30 `configure_onyx.py` persona rebuild (see `platform-status.md`),
> which reports the science stack rebuilt on the `qwen-omni-flash` model with literature tools
> Scite=14 / Consensus=13 and private doc sets (smoke test PASS). Re-verify the per-persona rows
> against the live API on the next session._ The old persona IDs 7/8 from
> `onyx-rag-optimization-2026-04-27.md` predate the v4 transition and no longer apply.

---

## Active Personas (Live — 2026-05-30)

| ID | Name | Public | Doc Sets | Tools | Model Config | Health |
|----|------|--------|----------|-------|-------------|--------|
| 0 | **Assistant** | ✅ Yes | none | generate_image, web_search, open_url, read_file, python | id=126 | ✅ OK |
| 1 | Scientific Researcher | ❌ No | Chemistry | internal_search, open_url, search, search_literature, search_patents, search_clinical_trials, get_clinical_trial, search_grants, get_grant, get_510k_summary, search_device510k, … | none | ⚠️ No model cfg |
| 2 | **physics-validator** | ✅ Yes | Robert Corpus | internal_search, read_file, Scite=14, Consensus=13 | qwen-omni-flash | ✅ Rebuilt 2026-05-30 (smoke PASS; re-verify) |
| 3 | **arxiv-intake** | ❌ No | arXiv Auto — Quarantine | _(none)_ | qwen-omni-flash | ✅ Rebuilt 2026-05-30 |
| 5 | **evidence-auditor** | ❌ No | Robert Corpus | per rebuild | qwen-omni-flash | ✅ Rebuilt 2026-05-30 (exact rows pending live confirm) |
| 6 | **referee-prep** | ❌ No | Robert Corpus | per rebuild | qwen-omni-flash | ✅ Rebuilt 2026-05-30 (exact rows pending live confirm) |

---

## Active Document Sets (Live — 2026-05-30)

| DS ID | Name | Public | Connectors | Notes |
|-------|------|--------|------------|-------|
| 1 | Chemistry | ❌ Private | — | Used by Scientific Researcher only |
| 2 | **Robert Corpus** | ❌ Private | — | Secured private 2026-05-30 — contains pre-publication HEP research |
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

## Physics Validator Persona Guardrails (id=2 — rebuilt 2026-05-30)

**Should have:**
- **Doc sets:** Robert Corpus, HEP Phenomenology References, Robert Boson Draft
- **Tools:** `internal_search`, `read_file`, `code_interpreter`, Scite MCP, Consensus MCP, `hep_arxiv` (id=28), `hep_inspire` (id=29), `hepdata` (id=30)
- **Model config:** `qwen-omni-flash` assigned in the 2026-05-30 rebuild (was NULL → all chats 404). Re-verify against live API.
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

## RAG Evaluation Status

The canonical eval questions and run results live in `rag-evaluation-set.md`. The
last recorded baseline (pre-rebuild) failed because `physics-validator` had no model;
re-run the set against the rebuilt persona and record results there, not here.
=======
## Doc Sets
- Robert Corpus: 2
- arXiv Auto — Quarantine: 3
- Scite Citations: 4
>>>>>>> Stashed changes
