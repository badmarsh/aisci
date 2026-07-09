# AiSci Comparative Analysis

This document benchmarks the `badmarsh/aisci` architecture against five leading frontier AI research and engineering systems as of mid-2026.

## The Contenders

1.  **OpenAI Deep Research**: An autonomous research agent optimized for long-horizon web browsing, synthesis, and report generation using `o3` or `o4-mini` models.
2.  **Gemini Deep Research**: Google's autonomous research agent, designed for deep web browsing, file synthesis, and MCP integration for specialized enterprise/scientific workflows.
3.  **OpenHands**: A premier open-source, Docker-sandboxed autonomous software engineering agent that can execute bash commands, write code, and fix bugs autonomously.
4.  **Cursor**: The leading AI-native IDE, providing codebase-aware editing, multi-file "Composer" capabilities, and tight developer-in-the-loop chat.
5.  **Roo Code (formerly Cline)**: An autonomous VS Code extension (now community-maintained as ZooCode/Cline) that uses MCP to read/write files and execute commands directly in the developer's workspace.

## Benchmark Dimensions

### 1. Epistemological Rigor (How it handles Truth)
*   **AiSci**: **Class-Leading.** AiSci's `evidence-ledger.md` provides a mathematically sound state machine for claims. It forces agents to record evidence, constraints, and statistical correlations (e.g., $T_{kin}$ and $\beta_s$ degeneracy) before a claim becomes "Validated."
*   **OpenAI / Gemini Deep Research**: **Strong.** Both produce highly cited, comprehensive reports based on web and internal data. However, their internal truth state is implicit in their context window, not durably externalized into a formal constraint matrix like AiSci.
*   **Cursor / OpenHands**: **Basic.** These are engineering tools. They assume the user dictates the "truth" (the desired feature) and they write code to fulfill it.

### 2. Autonomous Execution (How it acts)
*   **OpenHands**: **Class-Leading.** It spins up isolated Docker sandboxes, runs tests, fixes its own errors, and can iterate hundreds of times without human intervention.
*   **Roo Code**: **Strong.** Operates autonomously within the VS Code workspace, making edits and running terminal commands, though limited by local machine boundaries.
*   **AiSci**: **Weak / High Friction.** AiSci relies heavily on the heavy `DeerFlow` orchestration layer and predefined Python scripts (`fitting_pipeline.py`). Agents execute tasks off a queue (`next-actions.md`) rather than self-prompting a long-horizon research loop.
*   **Cursor**: **Moderate.** The Agentic mode is powerful but inherently designed for a human-in-the-loop developer driving the session.

### 3. Tooling & Ecosystem Integration (MCP)
*   **AiSci**: **Strong.** Excellent use of MCP for specialized scientific tools (Scite for citations, Consensus for literature, Onyx for RAG).
*   **Gemini Deep Research / Roo Code**: **Strong.** Native, primary support for MCP, allowing them to hook into arbitrary enterprise APIs seamlessly.
*   **OpenHands**: **Moderate.** Relies on its own internal "Skills" and sandboxed tools rather than a standardized, externalized MCP approach.

## Summary

**Where AiSci Wins:** AiSci is not just a generic coding agent; it is an **epistemic engine**. Its architecture is strictly designed to prevent hallucination in phenomenological physics by forcing all claims through a rigorous, statistically-backed markdown ledger. 

**Where AiSci Loses:** It is too rigid. The `fitting_pipeline.py` is hardcoded. An OpenAI or Gemini Deep Research agent would formulate new hypotheses dynamically. An OpenHands agent would write the Python code to test those hypotheses on the fly. AiSci requires a human (Robert) to build the hypothesis testing scaffolding, which the AI then merely executes.
