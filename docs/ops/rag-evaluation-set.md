# Onyx RAG Evaluation Set

This document maintains the canonical set of retrieval test questions used to evaluate Onyx RAG performance. Run this set before and after any changes to embeddings, rerankers, parsing logic, or chunk size.

## Evaluation Questions

### Q1: Blast-Wave Fit Parameters
- **Question**: "What are the typical transverse velocity and freeze-out temperature parameters used in Blast-Wave fits for 13 TeV pp collisions?"
- **Expected source**: Baseline literature (e.g., Khuntia 2019 or Rath 2020)
- **Required answer type**: Numerical extraction and scientific context
- **Pass/fail criteria**: PASS if the model extracts exact parameters and cites the correct baseline paper. FAIL if it hallucinates numbers or fails to find the paper.
- **Notes on missing coverage**: None.

### Q2: Tsallis Distribution Baseline
- **Question**: "How does the Tsallis-Pareto distribution handle high-pT tails compared to standard Boltzmann-Juttner?"
- **Expected source**: Tsallis baseline literature
- **Required answer type**: Theoretical explanation
- **Pass/fail criteria**: PASS if the model successfully retrieves the mathematical justification for the Tsallis q-parameter handling high-pT tails.
- **Notes on missing coverage**: Ensure Tsallis reference papers are indexed.

### Q3: Onyx OpenSearch Cutover Check
- **Question**: "What is the command to run the OpenSearch parity regression check?"
- **Expected source**: `docs/ops/onyx-rag-optimization-2026-04-27.md` or `docs/decisions/2026-04-26-parser-and-rag-choice.md`
- **Required answer type**: Exact command extraction
- **Pass/fail criteria**: PASS if it retrieves `deployment/helper/onyx_opensearch_cutover.py --json`.
- **Notes on missing coverage**: Must test `internal_search` on internal `.md` docs (though Canon rules say to use `read_file`, this tests index synchronization).

### Q4: Visual Table Analysis (Visual RAG Test)
- **Question**: "According to the HUBY AKO BIOINDIKATORY paper, what was the crown length of the SM-4 spruce tree on the degraded plot?"
- **Expected source**: Table 7 in `HUBY AKO BIOINDIKATORY.pdf`
- **Required answer type**: Specific numerical extraction from a visual table
- **Pass/fail criteria**: PASS if the Qwen vision model successfully summarized Table 7 and retrieved the correct value. FAIL if the table is invisible to the index.
- **Notes on missing coverage**: Validates the `qwen2.5vl:7b` LiteLLM routing.

### Q5: System Architecture Boundary
- **Question**: "Why shouldn't I use internal_search to check the status of the evidence ledger?"
- **Expected source**: `docs/ops/onyx-rag-optimization-2026-04-27.md`
- **Required answer type**: Architectural explanation
- **Pass/fail criteria**: PASS if it explains the RAG-vs-Canon boundary and the risk of stale, chunked copies.
- **Notes on missing coverage**: Tests meta-knowledge of the RAG system itself.
