# Onyx Persona IDs

> **Authoritative** persona/doc-set map.  
> Last updated: 2026-06-04 by `restore_v4_docsets.py`.  
> Re-run after any persona import, Onyx upgrade, or `POST /api/persona` change.

---

## Active Personas

| ID | Name | Public | Doc Sets | Notes |
|----|------|--------|----------|-------|
| 2 | **physics-validator** | ✅ Yes | Robert Corpus · HEP Phenomenology References · Robert Boson Draft | Restored 2026-06-04 |
| 5 | **evidence-auditor** | ❌ No | Robert Corpus · Scite Citations | |
| 6 | **referee-prep** | ❌ No | Robert Corpus · Scite Citations | |
| 3 | **arxiv-intake** | ❌ No | arXiv Auto — Quarantine | |
| 1 | **Scientific Researcher** | ❌ No | Chemistry | Has Scite + Consensus MCP |
| 0 | **Assistant** | ✅ Yes | none | |

> ⚠️ **physics-validator** does NOT have Scite/Consensus MCP.  
> Use **Scientific Researcher** (id=1) for external MCP literature queries.

---

## Active Document Sets

| DS ID | Name | Public | CC Pair | Contents |
|-------|------|--------|---------|----------|
| 2 | **Robert Corpus** | ❌ Private | CC pair 6 + 1 | Baseline literature + Ingestion API |
| 7 | **HEP Phenomenology References** | ❌ Private | CC pair 4 | Khuntia 2019 · Rath 2020 |
| 8 | **Robert Boson Draft** | ❌ Private | CC pair 10 | Pre-publication manuscript PDF |
| 3 | **arXiv Auto — Quarantine** | ❌ Private | CC pair 1 | arxiv-intake triage queue |
| 4 | **Scite Citations** | ✅ Public | CC pair 1 | Live citation snippets label |

---

## physics-validator Guardrails (id=2)

**Has:** Robert Corpus (DS 2) · HEP Phenomenology References (DS 7) · Robert Boson Draft (DS 8)  
**Tools:** `internal_search`, `read_file`  
**Model:** `qwen-omni-flash`  
**Must NOT have:** Scite/Consensus MCP → route those to Scientific Researcher (id=1)

---

## Connector / Credential Map

| Connector ID | Name | CC Pair ID | Credential ID |
|---|---|---|---|
| 0 | Ingestion API | 1 | 0 (DefaultCCPair) |
| 3 | Literature PDFs | 4 | 1 (PDF) |
| 4 | AiSci-System-Docs | 6 | 0 |
| 14 | Manuscript-File-Connector | 10 | 1 |

---

## Verification

```bash
python3 deployment/helper/inspect_connectors.py
python3 deployment/helper/run_rag_tests.py --persona-id 2 --label post-v4-restore
```
