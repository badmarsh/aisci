---
name: physics-paper-analysis
description: Use this skill to analyze a physics paper (especially High Energy Physics / HEP), download it from arXiv, cross-check citations via Scite, run SymPy formula verification, and generate a comprehensive referee report.
---

# Physics Paper Analysis Workflow

## Overview
This skill defines a comprehensive workflow for analyzing physics papers (e.g., ATLAS 13 TeV data, Tsallis distribution). It leverages arXiv, Onyx (RAG), Scite, and SymPy to perform a rigorous peer-review analysis and generate a referee report.

## Workflow Steps

### Step 1: Download Paper from arXiv
- **Action**: Use the arXiv MCP or web search to find the specified physics paper.
- **Goal**: Retrieve the paper's full text, abstract, and metadata.

### Step 2: RAG Query against Onyx
- **Action**: Query the Onyx knowledge base to ground the paper's claims in the existing evidence ledger and physics baselines (e.g., Tsallis, Blast-Wave).
- **Goal**: Contextualize the paper against verified HEP phenomenology references and local project data.

### Step 3: Citation Cross-Check via Scite
- **Action**: Use the Scite MCP integration (`/scite/`) to analyze the paper's key citations.
- **Goal**: Verify if the cited literature supports, mentions, or contrasts with the paper's claims.

### Step 4: SymPy Formula Verification
- **Action**: Extract key mathematical formulas from the paper. Use the built-in `python-repl` (Python Code Interpreter) to run SymPy verifications.
- **Goal**: Validate dimensional consistency, limit behaviors (e.g., velocity $v \to c$, $p_T \to 0$ or $\infty$), and structural correctness of the equations.

### Step 5: Generate Referee Report
- **Action**: Synthesize the findings from Steps 1-4 into a structured referee report.
- **Format**:
  1. Summary of Claims
  2. Literature & Citation Context (Scite & Onyx RAG results)
  3. Mathematical Validation (SymPy results)
  4. Strengths and Weaknesses
  5. Conclusion & Recommendation

## Integration Notes
- **Onyx**: Query via the established `Physics Validation Mode` RAG persona.
- **Scite / Consensus**: Access through the MCP proxy at `http://localhost:8095/scite/` and `http://localhost:8095/consensus/`.
- **SymPy**: Use the `bash` or `python` tool to run verification scripts.
