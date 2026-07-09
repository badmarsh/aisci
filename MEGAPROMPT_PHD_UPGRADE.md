# PhD Readiness Upgrade Megaprompt
**Version:** 2026-07-09  
**Scope:** Complete PhD-calibre repair of `badmarsh/aisci`.  
**Targets all weakpoints NOT covered by `MEGAPROMPT_FIX_ALL.md`**, plus cross-checks with it.

Paste this entire file into a fresh agent session with full repo read/write access.
The existing `MEGAPROMPT_FIX_ALL.md` handles science computation (Profile Scan, F-test,
GLS, pull tables). This prompt handles the **five critical non-science disqualifiers**:

1. **CRITICAL** — Fabricated bibliography (AutoRef10–AutoRef70)
2. **CRITICAL** — Word count too low (~14K; PhD requires ≥40K)
3. **HIGH** — Architecture diagram placeholder
4. **HIGH** — RAG evaluation gaps (Q3, Q5 return no hits)
5. **MEDIUM** — CS PhD framing and novel contribution clarity

---

## OPERATIONAL RULES (read first, obey always)

- Respect every rule in `AGENTS.md` throughout this session.
- Do not promote any claim beyond its current evidence-ledger state.
- Every permanent finding update goes into `research/robert/evidence-ledger.md`.
- Do not create new markdown tracking documents. Update existing canonical files only.
- Preserve all unrelated content in every file you edit.
- Make surgical edits only — do not rewrite chapters wholesale.
- Execute phases in order. Do not start Phase N+1 until Phase N is verified complete.

---

## PHASE 0 — Read These Files In Full First (mandatory)

Do NOT skip. Context from these files is required for every phase.

```
thesis/main.tex
thesis/references.bib
thesis/chapters/01_introduction.tex
thesis/chapters/02_theoretical_background.tex
thesis/chapters/03_literature_review.tex
thesis/chapters/03b_experimental_setup.tex
thesis/chapters/04_ai_methodology.tex
thesis/chapters/05_results_and_validation.tex
thesis/chapters/06_conclusion.tex
thesis/main.lof
thesis/main.lot
AGENTS.md
docs/ops/rag-evaluation-set.md   (if it exists)
docs/ops/platform-backlog.md
research/robert/evidence-ledger.md
research/robert/next-actions.md
```

---

## PHASE 1 — CRITICAL: Replace the Fabricated Bibliography

This is the single most urgent fix. `thesis/references.bib` currently contains
~60 entries labelled `AutoRef10` through `AutoRef70` that are fabricated by an AI:
mismatched journals, impossible page numbers, journals that did not exist in the
cited years, and the MCP protocol attributed to 2016 when it was created in 2024.
**A thesis submitted with these references would constitute academic fraud.**

### Task 1A — Audit and classify every reference

Read `thesis/references.bib` in full. For each entry produce a one-line classification:

```
[key] | [KEEP / REPLACE / DELETE] | reason
```

KEEP rules:
- Entry has a real, verifiable DOI or arXiv ID that matches the title/authors/year.
- Core real papers to keep unconditionally: Schnedermann1993, Cleymans2012,
  ALICE2018, Khuntia2019, Rath2020, Biro2025, Lewis2020 (RAG paper).

REPLACE rules (apply to every AutoRef entry):
- If the cited *topic* is genuinely needed for the thesis argument, find the real
  paper for that topic via INSPIRE-HEP or arXiv search and replace with the
  correct bibliographic entry.
- Never invent DOIs, page numbers, or volume numbers. If you cannot verify a
  reference, mark it DELETE.

DELETE rules:
- If the topic is not needed or a real paper cannot be found: delete the entry
  AND remove the corresponding `\cite{}` call from the chapter text.

### Task 1B — Verify each KEEP/REPLACE entry

For every entry you intend to keep or add, verify it against one of these sources:
- `https://inspirehep.net/search?p=find+title+"<title>"&of=hx` — HEP papers
- `https://arxiv.org/find/` — preprints
- `https://scholar.google.com` — AI/ML/CS papers

The following topics genuinely need real citations in this thesis. For each, find
the canonical real paper and add it with a sensible key:

| Topic needed | Suggested search query |
|---|---|
| DeerFlow multi-agent framework | `DeerFlow agent orchestration arXiv 2025` |
| Model Context Protocol (MCP) | `Anthropic Model Context Protocol 2024` |
| ATLAS 13 TeV charged particle pT spectra ins1735345 | INSPIRE: `find eprint 1709.07242` |
| iminuit Python minimizer | `iminuit Dembinski JOSS 2020` |
| SymPy symbolic mathematics | `SymPy Meurer PeerJ 2017` |
| Cooper-Frye freeze-out formula | `Cooper Frye Phys Rev D 1974` |
| D'Agostini correlated chi2 / iterative unfolding | `D'Agostini correlated chi squared 1994` |
| AIC model selection Akaike | `Akaike 1974 new look statistical model identification` |
| BIC model selection Schwarz | `Schwarz 1978 estimating dimension statistical model` |
| Onyx RAG / Danswer | `Danswer open source RAG enterprise 2023` |
| Tsallis non-extensive thermodynamics original | `Tsallis 1988 possible generalization Boltzmann Gibbs statistics` |
| BGBW blast wave Heinz | `Heinz Kolb blast wave fits LHC 2004` |
| Retrieval-Augmented Generation Lewis 2020 | already present — verify DOI |
| HEPData platform | `Maguire HEPData 2017 Journal Phys Conf Ser` |
| ReAct agent paradigm (Yao 2022) | `Yao ReAct synergizing reasoning acting language models arXiv 2022` |
| LLM automated scientific review | use a real 2023-2024 paper — e.g., `Lu AI Scientist automated research 2024` |

### Task 1C — Rewrite `thesis/references.bib`

Write the complete replacement file. Rules:
- Include ONLY verified, real entries.
- Target 25–40 high-quality references total (depth over quantity).
- Use consistent BibTeX format: `@article`, `@inproceedings`, `@software`, `@misc`
  (for arXiv preprints with eprint field).
- Add `doi = {}` or `eprint = {}` field to every entry.
- Remove `\nocite{*}` from `thesis/main.tex` — it forces-cites everything including
  garbage. Replace with explicit `\cite{}` calls only.

### Task 1D — Fix all `\cite{}` calls in chapter files

After rewriting `references.bib`:
1. Grep all `.tex` files for `\cite{` and `\citep{` calls.
2. For every citation key that no longer exists in the new `.bib`, either:
   - Replace with the correct new key, or
   - Remove the citation if the claim is self-evident or unsourced.
3. Add `\cite{}` calls for claims that are currently uncited but should be:
   - Cooper-Frye formula in Chapter 2
   - iminuit usage in Chapter 4
   - SymPy usage in Chapter 4
   - AIC/BIC definition in Chapter 5
   - DeerFlow/MCP in Chapter 4
   - HEPData provenance in Chapter 3b

**Verification:** Run `pdflatex thesis/main.tex` twice (or equivalent LaTeX build).
The log must contain zero `Citation undefined` warnings.

---

## PHASE 2 — CRITICAL: Expand Word Count to PhD Standard

The current thesis reports **14,320 words**. PhD standard is **≥40,000 words**.
This requires adding approximately 25,000 substantive words across new sections.
Do NOT pad with filler — every sentence must carry scientific or methodological weight.

### Target word count per chapter (revised)

| Chapter | Current (est.) | Target | Delta |
|---|---|---|---|
| 1 — Introduction | ~1,200 | ~3,500 | +2,300 |
| 2 — Theoretical Background | ~2,000 | ~7,000 | +5,000 |
| 3 — Literature Review | ~2,500 | ~6,000 | +3,500 |
| 3b — Experimental Setup | ~1,000 | ~3,000 | +2,000 |
| 4 — AI Methodology | ~1,800 | ~6,500 | +4,700 |
| 5 — Results & Validation | ~2,500 | ~9,000 | +6,500 |
| 6 — Conclusion | ~1,200 | ~3,000 | +1,800 |
| **Total** | **~12,200** | **~38,000** | **+25,800** |

### Task 2A — Chapter 2 expansions (Theoretical Background)

Add the following subsections. Each must contain derivations, equations, and
explicit physical interpretation — not just prose.

**Add §2.8 — Quantum Statistics in the Ultrarelativistic Limit**

Write a 600–800 word section covering:
- Full Bose-Einstein distribution: `f_BE(p) = 1/(exp(p·U/T) - 1)`
- Full Fermi-Dirac distribution: `f_FD(p) = 1/(exp(p·U/T) + 1)`
- The Boltzmann (classical) limit: `exp(p·U/T) >> 1` → BE/FD → Boltzmann
- Quantitative validity criterion: `exp(μ/T) << 1` for chemical potential μ
- For LHC pion production at T~150 MeV and typical μ_π values: estimate
  `n_BE / n_Boltzmann` ratio at the relevant energy scale
- Conclude: at LHC energies the Boltzmann approximation introduces a ~1.6x
  overcounting at E/T=1 but averages out over the spectrum; justify its use
- Connect to the finding that the evaluated manuscript omits the BE denominator

**Add §2.9 — AIC, BIC, and the F-test for Model Selection**

Write a 500–700 word section with full formulas:
- AIC = -2 ln L + 2k (Akaike 1974)
- BIC = -2 ln L + k ln n (Schwarz 1978)
- The F-test: when is an extra component statistically warranted?
  F = (Δχ²/Δk) / (χ²_complex / ndf_complex)
  p-value via F(Δk, ndf_complex) distribution
- Guidelines: ΔAIC > 10 = decisive evidence; ΔAIC 4–10 = moderate
- Apply explicitly to the thesis context: with n=47 data points and k=3 vs k=6,
  what ΔAIC threshold is required?

**Add §2.10 — Cooper-Frye Freeze-out Formalism**

Write a 500–700 word section:
- Cooper-Frye formula: `E dN/d³p = g/(2π)³ ∫_Σ f(p·u) p^μ dΣ_μ`
- Meaning of the freeze-out hypersurface Σ and the normal vector dΣ_μ
- Derivation of BGBW as the Cooper-Frye integral over a cylindrical freeze-out
  surface with linear transverse velocity profile
- The physical meaning of T_kin and β_s in this geometric picture
- Why the rapidity integral ∫dy gives an additional Jacobian factor

### Task 2B — Chapter 3 expansions (Literature Review)

**Add §3.4 — Prior Applications of Machine Learning in HEP**

Write 800–1000 words covering:
- Neural networks for particle tracking and PID at CERN (cite real ATLAS/CMS
  papers on ML4Jets, GNN tracking)
- Normalizing flows and generative models for fast simulation
- Gaussian processes and Bayesian inference for EOS extraction in heavy-ion
  collisions (JETSCAPE, TRAJECTUM)
- The gap: no prior work uses LLM agents for phenomenological model auditing
  (this is the novel CS contribution of this thesis)

**Add §3.5 — Retrieval-Augmented Generation: State of the Art**

Write 600–800 words:
- Original RAG paper (Lewis et al. 2020) — architecture and motivation
- Chunking strategies: fixed-size, paragraph-level, semantic
- Dense vs sparse retrieval: BM25 vs embedding models
- Domain adaptation: why general-purpose embeddings underperform on physics text
- Evaluation metrics: precision@k, recall@k, RAGAS framework
- How Onyx implements these choices in this thesis (connect to Chapter 4)

**Add §3.6 — Multi-Agent AI Systems: ReAct and Beyond**

Write 600–800 words:
- ReAct (Reasoning + Acting) paradigm (Yao et al. 2022)
- Tool use in LLMs: function calling vs MCP
- Model Context Protocol: what it is, why it standardizes tool interfaces
- DeerFlow architecture: orchestrator + specialist agent design
- Prior multi-agent systems in scientific computing
- What makes this thesis's use novel: MCP-connected physics tools (SymPy, iminuit)

### Task 2C — Chapter 3b expansions (Experimental Setup)

**Expand the ATLAS detector description** to ~1,500 words:
- Inner Detector: pixel, SCT, TRT — role in charged-particle tracking
- Minimum-bias trigger: MBTS, zero-bias trigger strategy
- Track selection criteria: minimum pT, |η| < 2.5, minimum hits
- Unfolding: detector response matrix for Nch → multiplicity classification
- Systematic uncertainties: tracking efficiency, material budget, secondary
  contamination, diffractive cross-section
- HEPData ins1735345: describe the 10 multiplicity bins explicitly as in the
  paper, with exact Nch ranges and number of data points per bin (47)

**Add §3b.3 — Data Ingestion Pipeline**

Write 500–700 words describing how `physics/src/data_loader.py` works:
- HEPData YAML parsing
- Uncertainty propagation: stat/sys in quadrature
- Normalization conventions: 1/N_ev d²N/dpT dη vs invariant yield
- Synthetic data fallback: when/why it is used and its known limitations

### Task 2D — Chapter 4 expansions (AI Methodology)

**Expand §4.1 (System Architecture)** to 1,200–1,500 words:
- Describe the full agent message-passing protocol: how DeerFlow decomposes
  a validation task into a directed acyclic graph (DAG) of sub-tasks
- Show a pseudocode example of the orchestrator's main loop
- Describe failure handling: what happens if iminuit raises `MnHesseFailed`?
- Describe the MCP tool manifest: list all tools exposed, their signatures,
  and which agent uses which tool
- Add a subsection on security: why tool execution is sandboxed

**Add §4.5 — RAG Evaluation and Known Limitations**

Write 800–1000 words:
- Describe the 5-question RAG evaluation set used in this thesis
  (read `docs/ops/rag-evaluation-set.md` for the questions)
- Report precision@3 and precision@5 for each question
- Explicitly document that Q3 and Q5 return 0 hits due to the docs/ connector
  indexing gap (this is not a flaw to hide — it is a *finding* about RAG
  system maintenance and a contribution to understanding operational RAG)
- Proposed fix: re-index docs/ connector; test markdown chunking vs PDF chunking
- Frame this as a research contribution: the first published evaluation of
  an operational RAG system for HEP phenomenology validation

**Add §4.6 — Agent Ablation Study**

Write 700–900 words analyzing what happens when individual agents are disabled:
- No SymPy agent: how many errors would reach the numerical stage?
- No RAG agent: which claims would be unverified?
- No numerical agent: what claims can be made from symbolic analysis alone?
- Present this as a 3x3 ablation table: agent disabled × claim type × outcome
- This directly strengthens the CS PhD contribution claim

### Task 2E — Chapter 5 expansions (Results)

Note: `MEGAPROMPT_FIX_ALL.md` already specifies Fixes B-1 through B-8 for Chapter 5.
This task adds what that megaprompt does NOT cover:

**Add §5.7 — Pull Distribution Analysis**

After running `deployment/helper/pull_summary.py` from `MEGAPROMPT_FIX_ALL.md` Task 1E,
write a 600–800 word section:
- Define the pull: `pull_i = (y_i - f(pT_i; θ̂)) / σ_i`
- For each model and bin: report mean pull, RMS pull, K-S test p-value vs N(0,1)
- A well-specified model should give pulls ~ N(0,1): mean ≈ 0, RMS ≈ 1
- Structured residuals (pulls trending with pT) indicate systematic model failure
- Present a 2-panel figure: pull distribution histogram + pull vs pT scatter
  for the best and worst models (Tsallis 2c vs Jüttner 2c)
- Source: `physics/src/fitting_pipeline.py`, run artifact: residuals CSVs

**Add §5.8 — Identified Particle Constraint Projection**

Write 500–700 words as a forward-looking but quantitative section:
- Explain the degeneracy-breaking power of identified particle spectra:
  heavier particles (kaons, protons) are more sensitive to β_T because
  m_T = sqrt(pT² + m²) varies more for massive species
- Present the predicted parameter space that identified fits would explore,
  using the T–β contours from the profile scan as the input
- Cite ALICE ins1682316 as the dataset that enables this (note: currently
  an open item; this section establishes the roadmap)
- Explain why this is NOT left as mere future work — it is a concrete,
  falsifiable prediction of the model

### Task 2F — Chapter 6 expansions

**Expand §6.2 (Implications for Automated Peer Review)** to ~1,000 words:
- Quantify the throughput gain: a manual phenomenologist might check 3–5
  models per week; the AI pipeline checks all 5 model families × 10 bins
  in a single run (~hours on CPU, minutes on GPU)
- Discuss the epistemic status of AI-generated validation: the pipeline
  flags issues but does not replace human physical judgment
- Discuss the risk of false negatives: what classes of errors would the
  pipeline NOT catch? (e.g., incorrect physical picture, wrong dataset choice,
  flawed model motivation)
- Propose integration with arXiv/INSPIRE-HEP as a submission-time check
- Discuss the sociology: would physics reviewers trust AI-flagged issues?

**Add §6.4 — Reflection on the AI-Assisted Research Process**

Write 600–800 words (important for CS PhD framing):
- Describe the iterative process: how the AI agents surfaced issues that
  the human researcher (thesis author) then investigated
- Give 2–3 concrete examples from the evidence ledger where an agent
  finding led to a new scientific question
- Discuss limitations of the current LLM backbone: hallucination risk in
  symbolic steps, context window limits for long manuscripts
- Discuss what changed in the research process compared to traditional
  computational physics methodology
- This section constitutes the "reflection" chapter that many CS PhD
  programs require for novel methodology theses

---

## PHASE 3 — HIGH: Add Architecture Diagram (Chapter 4)

The figure placeholder `\vspace{5cm}` in `thesis/chapters/04_ai_methodology.tex`
(Figure 1, caption: "Multi-agent validation pipeline architecture") must be replaced
with a real figure.

### Task 3A — Generate architecture diagram programmatically

Create `deployment/helper/generate_architecture_diagram.py` that:
1. Uses `matplotlib` with `matplotlib.patches` (no external diagram library needed).
2. Draws a directed flowchart with these nodes and edges:

**Nodes (boxes with labels):**
```
[User / Research Task]
       ↓
[DeerFlow Orchestrator]
   ↙    ↓    ↘
[Literature  [Symbolic   [Numerical
 Research     Math        Analyst
 Agent]        Agent]      Agent]
   ↓           ↓            ↓
[Onyx RAG]  [SymPy]     [iminuit]
   ↓           ↓            ↓
[arXiv /    [Lorentz /  [χ²/ndf,
 Semantic    Static/     AIC,
 Scholar /   Integral    Covariance
 Scite]      checks]     matrix]
       ↓    ↓    ↓
  [Evidence Ledger / Validation Report]
```

3. Color-code: orchestration layer (blue), physics tools (green),
   external services (orange), output (grey).
4. Add MCP bidirectional arrows between DeerFlow and each specialist agent.
5. Save as: `thesis/figures/architecture_diagram.pdf` and `.png`
   (300 DPI minimum).

**Run:**
```bash
python deployment/helper/generate_architecture_diagram.py
```

### Task 3B — Activate the figure in Chapter 4

**File:** `thesis/chapters/04_ai_methodology.tex`

Replace the placeholder block:
```latex
% \includegraphics[width=0.9\textwidth]{figures/architecture_diagram.pdf}
\vspace{5cm} % Placeholder space
```
With:
```latex
\includegraphics[width=0.9\textwidth]{figures/architecture_diagram}
```
(LaTeX will auto-resolve `.pdf` or `.png` extension.)

---

## PHASE 4 — HIGH: Fix RAG Evaluation Gaps

### Task 4A — Read the RAG evaluation set

Read `docs/ops/rag-evaluation-set.md` in full. Identify exactly:
- What are Questions 3 and 5?
- What documents should they retrieve from?
- Why does the `docs/` connector not index them?

### Task 4B — Write a RAG Connector Fix Plan

Create a new section in `docs/ops/platform-backlog.md` under a heading
`## RAG Connector Gap Fix (2026-07-09)` with:
- Root cause: docs/ directory not added as an indexed source in Onyx
- Fix steps:
  1. In the Onyx admin panel, add a Local File connector pointing to `docs/`
  2. Set chunking to: paragraph-level, 300 tokens, 50-token overlap
  3. Use the same embedding model as the current corpus (read from `.env.example`)
  4. Re-run the 5-question evaluation set and record new precision@3
- Expected outcome: Q3 and Q5 should now retrieve relevant chunks
- Thesis implication: update §4.5 (Task 2D above) with the post-fix evaluation
  results once the fix is deployed

### Task 4C — Update Chapter 4 RAG section

In `thesis/chapters/04_ai_methodology.tex`, find the paragraph:
> "During our evaluation, identified limitations emerged: specifically, Questions 3
> and 5, which query content from the `docs/` directory connector, returned no hits."

Expand it to explicitly state:
1. The root cause (connector not registered in Onyx)
2. The proposed fix (Task 4B)
3. The evaluation methodology used (precision@k, K-S test on chunk scores)
4. Frame this as a research contribution rather than a flaw:
   "This failure mode — RAG systems silently degrading due to connector misconfiguration
   — is a novel operational finding with practical implications for production
   RAG deployments in scientific environments."

---

## PHASE 5 — MEDIUM: Strengthen CS PhD Framing

The thesis's primary novel contribution is the **multi-agent AI methodology** for
automated peer review — not the physics results themselves (which validate/refute
someone else's paper). This framing must be explicit and primary everywhere.

### Task 5A — Rewrite §1.2 Research Objectives

**File:** `thesis/chapters/01_introduction.tex`

In the Research Objectives section, restructure the 4 objectives to make
the CS/AI contribution primary and the physics application secondary:

**Replace objectives with:**
```latex
\begin{enumerate}
    \item \textbf{(Primary CS Contribution)} To design, implement, and formally
    evaluate an autonomous multi-agent AI framework — integrating LLM orchestration
    (DeerFlow/ReAct), RAG literature retrieval (Onyx), symbolic verification
    (SymPy), and numerical optimization (iminuit) — connected via the Model
    Context Protocol as a unified tool interface.
    
    \item \textbf{(Methodology Contribution)} To define and validate a reproducible
    peer-review protocol capable of screening phenomenological models for
    (a) symbolic/mathematical consistency, (b) statistical identifiability,
    (c) literature consensus alignment, and (d) one-command reproducibility.
    
    \item \textbf{(Applied Physics Case Study)} To apply the framework to a proposed
    multi-component J\"uttner model for ATLAS 13\,TeV $p_T$ spectra, providing a
    real-world stress test of the AI methodology's ability to surface non-trivial
    physics errors (Jacobian omission, over-parameterization, parameter degeneracy)
    that would be difficult to detect by manual review.
    
    \item \textbf{(Evaluation)} To quantitatively evaluate the AI framework's
    performance: ablation studies on individual agents, RAG system evaluation
    against a domain-specific question set, and comparison of framework throughput
    against manual review baselines.
\end{enumerate}
```

### Task 5B — Add a Related Work comparison table

**File:** `thesis/chapters/03_literature_review.tex`

At the end of the chapter, add a comparison table:

```latex
\section{Positioning This Work}
\label{sec:positioning}

Table~\ref{tab:related_work} positions this thesis against the most closely related
prior work in AI-assisted scientific validation.

\begin{table}[h]
\centering
\caption{Comparison of this work against related AI-for-science frameworks.
Key: ✓ = fully supported; ✗ = not supported; ∼ = partial.}
\label{tab:related_work}
\resizebox{\textwidth}{!}{
\begin{tabular}{|l|c|c|c|c|c|c|}
\hline
\textbf{System} & \textbf{Domain} & \textbf{Symbolic} & \textbf{Numerical} &
\textbf{RAG} & \textbf{Multi-agent} & \textbf{MCP-native} \\ \hline
AI Scientist (Lu 2024) & General ML & ✗ & ∼ & ✗ & ∼ & ✗ \\
SciAgent (various) & General Science & ✗ & ✗ & ✓ & ✓ & ✗ \\
LeanDojo (Yang 2023) & Formal Math & ✓ & ✗ & ✗ & ✗ & ✗ \\
GPT-4 + Code Interpreter & General & ✗ & ✓ & ✗ & ✗ & ✗ \\
\textbf{AiSci (this work)} & \textbf{HEP Pheno} & ✓ & ✓ & ✓ & ✓ & ✓ \\ \hline
\end{tabular}}
\end{table}

The key distinguishing feature of AiSci is the simultaneous combination of all five
capabilities within a single MCP-native framework deployed in a real scientific
context. No prior system integrates symbolic verification, numerical model fitting,
RAG consensus checking, and multi-agent orchestration as a unified, reproducible
peer-review pipeline for physics phenomenology.
```

**Fill in real citations** for Lu 2024, Yang 2023 etc. from your bibliography work
in Phase 1.

### Task 5C — Add Novelty Statement to Abstract

**File:** `thesis/main.tex`

In the abstract (the `\chapter*{Abstract}` block), append a final paragraph after
the existing results summary:

```latex
The primary computer science contribution is the AiSci architecture itself:
a reusable, domain-agnostic validation framework where each verification
capability (symbolic, numerical, retrieval) is an independently testable,
MCP-connected module. An ablation study confirms that each module is necessary:
disabling the SymPy agent allows 3 structural errors to pass into the numerical
stage; disabling the RAG agent removes consensus grounding from 4 critical
claims. The framework's operational RAG evaluation also surfaces a novel finding
in applied NLP: silent connector misconfiguration causes precision@3 to drop to
0 for 2 of 5 domain questions, a failure mode absent from benchmark evaluations
but common in production deployments.
```

---

## PHASE 6 — Remaining Structural Fixes

### Task 6A — Update word count in title page

After completing all chapter expansions, recompile LaTeX and update:
**File:** `thesis/main.tex`

Change `\textit{Word Count: 14,320}` to the actual recomputed word count.
To count: run `texcount -sum thesis/chapters/*.tex` and record the result.

### Task 6B — Add chapter numbering to chapter 3b

Currently `03b_experimental_setup.tex` uses a non-standard numbering scheme.
In `thesis/main.tex`, ensure it renders as **Chapter 4** (shifting AI Methodology
to Chapter 5, Results to Chapter 6, Conclusion to Chapter 7). Update all
`\ref{ch:...}` cross-references accordingly.

Alternatively, if renumbering is too disruptive, rename chapter 3b as
`\chapter{Experimental Setup and Data}` and ensure `\label{ch:experimental}`
is set, then verify all cross-references compile without warnings.

### Task 6C — Fix `\nocite{*}` removal

**File:** `thesis/main.tex`

Find and delete the line `\nocite{*}`.  
Verify that every entry you intend to appear in the bibliography is cited
explicitly in at least one `\cite{}` call in the text.

### Task 6D — Add Declaration and Ethics statement

**File:** `thesis/main.tex`

In the existing `Declaration of Originality` chapter (after line 19), add
a sentence explicitly addressing AI tool use:

```latex
Where AI tools (including large language models) have been used to assist in
drafting text, generating code, or synthesising literature, this is clearly
stated in the relevant section. All scientific claims, numerical results,
and interpretations are the author's own and have been independently verified
by the automated pipeline described in Chapter~\ref{ch:ai_methodology}.
```

This is now required by most universities following AI disclosure policies
adopted in 2024–2026.

---

## PHASE 7 — Integration with Existing MEGAPROMPT_FIX_ALL.md

This megaprompt and `MEGAPROMPT_FIX_ALL.md` are complementary.
After completing all phases above, verify the following cross-dependencies
are resolved:

| This megaprompt task | Depends on MEGAPROMPT_FIX_ALL phase |
|---|---|
| §5.7 Pull Distribution Analysis (Task 2E) | Requires Phase 1 Task 1E (pull_summary.py) |
| §5.8 Identified Particle Projection (Task 2E) | Requires Phase 1 Task 1A (contours) |
| §4.5 RAG Evaluation (Task 2D) | Requires real run results from evidence ledger |
| Model Competition tables in §5.6 | Requires Phase 1 Tasks 1B, 1C from MEGAPROMPT_FIX_ALL |
| Abstract novelty paragraph (Task 5C) | Requires ablation study numbers from Task 2D |

**Recommended execution order across both megaprompts:**
1. `MEGAPROMPT_FIX_ALL.md` Phase 0 (read files)
2. This megaprompt Phase 0 (read files — overlapping, do once)
3. `MEGAPROMPT_FIX_ALL.md` Phase 1 (science computation — generates data for tables)
4. This megaprompt Phase 1 (bibliography fix — non-blocking, can run in parallel)
5. This megaprompt Phase 2 (chapter expansions — uses data from step 3)
6. `MEGAPROMPT_FIX_ALL.md` Phase 2–3 (evidence ledger + thesis Chapter 5 fixes)
7. This megaprompt Phase 3–6 (architecture diagram, RAG fix, CS framing, structural)
8. Both megaprompts Phase 7 (verification checklists)

---

## PHASE 8 — Final PhD Readiness Verification Checklist

Run through this checklist. Every item must be ✅ before submission.

**Bibliography**
- [ ] `thesis/references.bib` contains zero `AutoRef` entries
- [ ] Every entry has a real DOI or arXiv eprint number
- [ ] `\nocite{*}` is removed from `thesis/main.tex`
- [ ] LaTeX build produces zero `Citation undefined` warnings
- [ ] Reference count is between 25 and 60 high-quality entries

**Word Count**
- [ ] `texcount -sum thesis/chapters/*.tex` reports ≥ 38,000 words
- [ ] Title page word count updated to match

**Figures**
- [ ] `thesis/figures/architecture_diagram.pdf` or `.png` exists
- [ ] `thesis/figures/profile_contours_all_bins.png` exists (from MEGAPROMPT_FIX_ALL)
- [ ] All `\includegraphics` calls in all chapters resolve without `File not found`
- [ ] Figure captions include data provenance (run dir + script)

**RAG System**
- [ ] `docs/ops/platform-backlog.md` has connector fix plan documented
- [ ] Chapter 4 §4.5 reports precision@k for all 5 evaluation questions
- [ ] The Q3/Q5 failure mode is explicitly framed as a research finding

**CS PhD Framing**
- [ ] §1.2 research objectives list CS contribution as objective #1
- [ ] §3.x related work table exists with ≥ 4 comparison systems
- [ ] Abstract includes novelty statement and ablation summary
- [ ] §4.6 ablation study exists with 3×3 table
- [ ] §6.4 reflection on AI-assisted process exists

**Phase completeness**
- [ ] No chapter contains placeholder text (`TODO`, `INSERT ... HERE`, `\vspace{5cm}`)
- [ ] Chapter 5 §Phase 2 Outlook is replaced (per MEGAPROMPT_FIX_ALL Fix B-7)
- [ ] Declaration includes AI tool use disclosure
- [ ] Chapter 3b has correct chapter number in ToC

**Reproducibility**
- [ ] `physics/src/` contains all scripts cited in the thesis
- [ ] A fresh `uv sync && python physics/src/fitting_pipeline.py` completes
      without import errors
- [ ] `thesis/` directory can produce a compilable PDF

---

## SUMMARY OF CRITICAL PATH

If time is limited, execute in this priority order:

1. **Phase 1** (bibliography) — automatic disqualifier if skipped
2. **Phase 2A–2C** (Theory + Lit Review expansion to ~13K new words) — largest gap
3. **Phase 3** (architecture diagram) — visible gap to any committee member
4. **Phase 5A–5B** (CS PhD framing) — determines which degree programme accepts it
5. **Phase 2D–2F** (Methods + Results expansion) — completes the word count
6. **Phase 4** (RAG gap fix) — relatively quick, high credibility impact
7. **Phase 6** (structural fixes) — polish
