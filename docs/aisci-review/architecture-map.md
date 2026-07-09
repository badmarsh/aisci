# AiSci Architectural Map

This document models the `badmarsh/aisci` repository as it exists today. It breaks down every major subsystem, its responsibilities, limitations, dependencies, and interactions based on direct evidence from the codebase.

## 1. The Physics Core (`physics/src/`)
**Purpose:** The analytical engine of the project. It handles data loading, model fitting (Blast-Wave, Tsallis, Bose-Einstein, Jüttner), and statistical validation.
**Key Components:**
*   `fitting_pipeline.py`: A highly rigorous, 900+ line Python script utilizing `iminuit` for LeastSquares fitting. It tests multiple phenomenological models across 10 multiplicity bins, calculates chi2/ndf, AIC/BIC, covariance matrices, and extracts correlations.
*   `rag_claim_verifier.py`: Integrates with the Onyx RAG system (via REST API) and a local LLM to verify physics claims against ingested literature. Classifies claims as Supported, Contradicted, Nuanced, or Unsupported.
*   `bgbw_fit.py`, `bgbw_identified_fit.py`, `bgbw_covariance.py`: Specialized scripts for specific variants of the Blast-Wave model, addressing identified particle species and covariance matrix generation.
*   `sympy_validation_agent.py`: Symbolic math verification.
**Strengths:** Extremely high statistical rigor. Computes robust uncertainties, correlations (e.g., discovering the T-beta degeneracy in the BGBW model), and residuals. Follows best practices for high-energy physics phenomenological analysis.
**Limitations:** It is fundamentally a collection of static Python scripts, not an autonomous agentic framework. An AI agent might write or run these scripts, but the scripts themselves do not plan, reason, or self-correct dynamically.

## 2. The Orchestration & Deployment Layer (`deployment/`)
**Purpose:** Infrastructure for running agents, retrieval systems, and environment provisioning.
**Key Components:**
*   `deer-flow/`: Appears to be the primary agent orchestration framework. Contains its own `agents/`, `skills/`, `backend/`, and `frontend/` subdirectories. The `ACTION_PLAN.md` mentions a pending decision on "DeerFlow de-vendoring," suggesting it might be an external fork or a heavy dependency they are considering stripping out.
*   `onyx/`: The RAG and retrieval layer. Uses `nomic-embed-text-v1` and OpenSearch to index and retrieve physics literature.
*   `mcp_config.yaml`: Model Context Protocol configuration linking the agent environment to:
    *   **Consensus**: For broad literature consensus via OAuth.
    *   **Scite**: For citation context (Smart Citations) via OAuth.
    *   **Onyx**: Local server-side bearer token access for RAG.
**Strengths:** Strong isolation of concerns. Explicit configuration for modern AI tools (MCP).
**Limitations:** Highly complex infrastructure footprint (Docker compose stacks for Onyx, DeerFlow, LLMs, Postgres). DeerFlow seems to dominate the orchestration layer, which might conflict with a leaner, more native autonomous architecture.

## 3. The Research Canon (`research/robert/`)
**Purpose:** The persistent, stateful memory and truth-tracker for the scientific endeavor.
**Key Components:**
*   `evidence-ledger.md`: The crown jewel of the repo. A meticulously maintained table tracking claims (e.g., "The main exponential form is Lorentz-covariant"), the evidence required, the current evidence, its status (e.g., "Sanity checked", "Validated", "Blocked"), and the next gate.
*   `next-actions.md`: The active task queue.
*   `runs/YYYY-MM-DD-*/`: Immutable execution environments. Every fit or experiment dumps its configuration, diagnostics, and raw outputs here (as mandated by `AGENTS.md`).
**Strengths:** Solves the LLM "hallucination and context-loss" problem perfectly. By forcing agents to serialize their claims, evidence, and confidence into a living ledger, it creates a verifiable, reviewable state machine for scientific discovery.
**Limitations:** Relies on human (or highly disciplined AI) compliance to maintain. It is a passive Markdown document, not an active database that enforces its own constraints programmatically.

## 4. Agent Governance & Skills (`AGENTS.md` and `agent-skills/`)
**Purpose:** The "operating constitution" for any AI agent touching the repo.
**Key Components:**
*   `AGENTS.md`: Defines strict rules for evidence, file hygiene, and GitHub workflow. It explicitly forbids fabricating citations or promoting claims without ledger backing.
*   `agent-skills/`: Contains 15 subdirectories (e.g., `science-ledger-manager`, `reproducible-physics-runner`), each with a `SKILL.md`. These are vendor-neutral markdown prompts that agents load to understand how to execute specific operational workflows.
**Strengths:** Phenomenal prompt engineering and behavioral constraint design. Treats the AI as a junior scientist who must show their work, rather than a magic oracle.
**Limitations:** Again, these are passive documents. The system relies on the LLM's context window and obedience to adhere to them, rather than programmatic guardrails (though DeerFlow may implement some of this).

## Summary of Interactions
The architecture operates in a loop defined by human-AI collaboration:
1. **Planning**: Driven by `AGENTS.md` rules, logged in `next-actions.md`.
2. **Execution**: Agents (via DeerFlow) or humans execute Python scripts in `physics/src/`.
3. **Verification**: Outputs are stored in `runs/`, literature is checked via `rag_claim_verifier.py` (Onyx) and MCPs (Scite/Consensus).
4. **Knowledge Accumulation**: Results are distilled into `evidence-ledger.md`. Only when evidence is overwhelming does a claim become "Validated".
