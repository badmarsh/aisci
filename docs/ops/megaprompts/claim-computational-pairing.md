# Megaprompt: Claim-Computational Pairing & Verification Pipeline

## Context
This megaprompt outlines the target architecture and agent workflow for AiSci's Paper Studio and Canvas modes. It bridges the gap between raw scientific claims extracted from literature and the advanced computer science (CS) pipelines required to formally prove or empirically validate them.

## 1. Representing and Classifying Claims
The first step is to parse manuscripts into machine-readable claims with metadata: domain, variables, asserted relationships, and required evidence type (theory, simulation, empirical).

Extend the existing extraction logic (inspired by systems like CliVER, SciClaims, and SemanticCite) by adding a **"Computational Affordance"** classifier that labels each claim as:
- **Simulation-testable:** (e.g., heavy-ion spectra, CFD, MD)
- **Algorithmic/complexity-theoretic:** (e.g., new algorithm, hardness result)
- **Data-analytic:** (e.g., claims about correlations or model performance)
- **Formally provable:** (e.g., properties of models, protocols, combinatorial objects)

These labels instruct the AI on exactly what kind of advanced CS pipeline might prove or refute the claim.

## 2. Searching and Pairing Articles with Computational Methods
Once claims are classified, use FireCrawl + Local Deep Research (LDR) to search across:
- **Literature corpora** (arXiv, PubMed, INSPIRE, conference proceedings) for papers whose methods section mentions relevant solvers, algorithms, or formal tools.
- **Code corpora** (GitHub, GitLab) for repositories tagged with matching domains and tools (e.g., OpenFOAM solvers, Lean 4 libraries, probabilistic programming frameworks).

### The Pairing Pipeline
1. **Candidate Retrieval:**
   - Use keyword + embedding search over titles/abstracts to get papers whose methods match the claim's domain (e.g., "Tsallis blast-wave Monte Carlo", "CFD Spalart-Allmaras", "Lean 4 theorem proving").
   - Use FireCrawl to index GitHub READMEs/docs to pull repos matching required tools.
2. **Method-Level Matching:**
   - Extract method signatures (solver names, theorem provers, algorithm families) and computational constraints from candidates.
   - Compare against the claim's computational affordance label. Discard mathematically incompatible articles.
3. **Ranking by "Provability Fit":**
   - Score candidates by how tightly their methods align with the claim's variables and physical regime (e.g., collision system and energy in AISCI).
   - *Heuristic:* Prefer articles with open-source code or precise algorithm specs that can be executed or formally reasoned over.

**Output:** A set of article + repo pairs for each claim, ranked by computational utility.

## 3. Advanced CS Pipelines to "Prove" Claims
For matched claims, the AI orchestrates domain-appropriate CS pipelines grounded in real code and formal systems:

- **High-fidelity simulation & numerical analysis:** Run blast-wave or Tsallis fits, GPU Monte Carlo, or transport simulations that directly test heavy-ion claims. Record chi²/AIC/BIC and anomaly metrics back into the evidence ledger.
- **Formal verification and theorem proving:** For algorithmic/model-theory claims, pair with Lean/Coq/Isabelle libraries, generate candidate proofs, and rely on kernels to certify correctness (yielding machine-checkable certificates).
- **Economic/empirical computational engines:** AI chooses and interprets analyses, but every reported figure comes from reproducible computation (the physics core) that a human can re-run.

*AI's Role:* Selection, orchestration, and explanation. The "proof" comes from reproducible computation or formally verified logic.

## 4. Claim-Article Pairing Logic in Canvas Studio
Mapped onto the Paper Studio / Canvas:
- **ClaimNodes:** Each receives a computational affordance label and a list of paired articles/repos (scored for fit and reproducibility).
- **PipelineNodes:** Correspond to specific advanced CS methods (GPU Monte Carlo, symbolic auto-diff check, Lean 4 proof).
- **EvidenceNodes:** Represent the external literature retrieved by LDR.

**Agent Behaviors:**
- Propose Claim–Pipeline bindings by matching affordance labels to available methods and code.
- Trigger runs, collect outputs, and convert them into **ResultNodes**.
- Claims backed by strong computational evidence move from "Proposed" to "Validated" in the ledger. Weak/contradicted claims are flagged.

## 5. Guardrails and Verification Standards
Verification is the hard part of AI-driven science. Systems must strictly separate retrieval, computation, and LLM reasoning to avoid hallucinated proofs.

**Mandatory Trust Requirements:**
Every "proven" claim MUST have:
1. A pointer to the exact article(s) and code used.
2. Logged configuration and inputs.
3. Either a machine-checked proof (for formal work) or reproducible numerical evidence (for simulations and data).

**Multi-Agent Pattern:**
Use specialized agents to enforce rigor:
- *Agent A:* Classifies claim types.
- *Agent B:* Retrieves authoritative sources via LDR.
- *Agent C:* Scores credibility based on explicit evidence and transparent reasoning.

This ensures AiSci pairs claims with correct CS machinery and verifiable workflows, making "proven by advanced computer science" concrete, reproducible, and inspectable.
