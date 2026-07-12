# Historical Onyx RAG Evaluation Set

> **Historical integration record.** This evaluation set belongs to a removed
> Onyx RAG deployment and is not a current test or operational gate.

This document maintains the canonical set of retrieval test questions used to evaluate Onyx RAG performance. Run this set before and after any changes to embeddings, rerankers, parsing logic, or chunk size.

## Evaluation Questions

### Q1: Blast-Wave Fit Parameters
- **Question**: "What are the typical transverse velocity and freeze-out temperature parameters used in Blast-Wave fits for 13 TeV pp collisions?"
- **Expected source**: Baseline literature (e.g., Khuntia 2019 or Rath 2020)
- **Required answer type**: Numerical extraction and scientific context
- **Pass/fail criteria**: PASS if the model extracts exact parameters and cites the correct baseline paper. FAIL if it hallucinates numbers or fails to find the paper.
- **Notes on missing coverage**: Requires `Khuntia_2019_1808.02383.pdf` and `Rath_2020_1908.04208.pdf` indexed in Robert Corpus.

### Q2: Tsallis Distribution Baseline
- **Question**: "How does the Tsallis-Pareto distribution handle high-pT tails compared to standard Boltzmann-Juttner?"
- **Expected source**: Tsallis baseline literature (Khuntia 2019 or Rath 2020 discuss Tsallis comparison)
- **Required answer type**: Theoretical explanation
- **Pass/fail criteria**: PASS if the model successfully retrieves the mathematical justification for the Tsallis q-parameter handling high-pT tails.
- **Notes on missing coverage**: Requires Khuntia/Rath PDFs indexed; Tsallis-specific standalone reference not yet in corpus.

### Q3: Onyx OpenSearch Cutover Check
- **Question**: "What is the command to run the OpenSearch parity regression check?"
- **Expected source**: `docs/ops/onyx-rag-optimization-2026-04-27.md` or `docs/decisions/2026-04-26-parser-and-rag-choice.md`
- **Required answer type**: Exact command extraction
- **Pass/fail criteria**: PASS if it retrieves `deployment/helper/onyx_opensearch_cutover.py --json`.
- **Notes on missing coverage**: `docs/ops/` markdown files are not indexed in Onyx. Q3 tests `internal_search` on internal docs — this will FAIL until a docs/ file connector is added. This is a known structural gap, not a retrieval failure.

### Q4: Manuscript Model Comparison (replaces Visual Table Test)
- **Question**: "Does the manuscript compare the boson probability distribution model against a Tsallis or Blast-Wave baseline? If so, what is the stated motivation?"
- **Expected source**: `PhD Thesis 2.pdf` (indexed, 187 chunks)
- **Required answer type**: Direct quote from the manuscript about baseline comparison or the absence thereof
- **Pass/fail criteria**: PASS if the model quotes a relevant passage from the manuscript about model comparison, baseline fits, or goodness-of-fit. FAIL if it returns NOT FOUND IN CORPUS or hallucinates.
- **Notes on missing coverage**: Replaces the HUBY bioindicator Q4 which referenced a PDF (`HUBY AKO BIOINDIKATORY.pdf`) that was never in the corpus. The original visual-RAG test should be redesigned once a suitable table-heavy PDF is indexed. `qwen2.5vl:7b` vision routing is tested by the existing image-analysis pipeline during indexing.

### Q5: System Architecture Boundary
- **Question**: "Why shouldn't I use internal_search to check the status of the evidence ledger?"
- **Expected source**: `docs/ops/onyx-rag-optimization-2026-04-27.md`
- **Required answer type**: Architectural explanation
- **Pass/fail criteria**: PASS if it explains the RAG-vs-Canon boundary and the risk of stale, chunked copies.
- **Notes on missing coverage**: `docs/ops/` is not indexed. This question reliably FAILs until a docs/ connector is created. Record result as STRUCTURAL GAP — corpus missing, not retrieval failure.

---

## Baseline Run Results

### Run 2026-05-30 (Attempt 1 — corpus gap discovered)

| Q | Result | Root Cause |
|---|---|---|
| Q1 | ❌ NOT FOUND | Khuntia/Rath PDFs not in corpus (purged, not re-uploaded) |
| Q2 | ❌ NOT FOUND | Same — literature PDFs absent |
| Q3 | ❌ Stream error | `APIConnectionError` from LiteLLM (transient); `docs/` also not indexed |
| Q4 | ❌ NOT FOUND | HUBY paper never existed in corpus |
| Q5 | ❌ NOT FOUND | `docs/ops/` markdown not indexed |

**Action taken**: Re-uploaded `Khuntia_2019_1808.02383.pdf` and `Rath_2020_1908.04208.pdf` via `deployment/helper/upload_literature_pdfs.py`. Replaced Q4 with a manuscript-grounded question. Index attempt 42 triggered 2026-05-30.

### Run 2026-05-30 (Attempt 2 — pending)

To be recorded after index attempt 42 completes and `run_rag_tests.py` is re-run.
