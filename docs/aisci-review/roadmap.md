# AiSci Roadmap: Closing the Frontier Gap

**Date:** 2026-07-09  
**Source:** Phase 2 Comparative Analysis and Gap Scorecard (`docs/aisci-review/gap-analysis-scorecard.md`)  
**Purpose:** Concrete, sequenced work items to bring AiSci from a rigorous-but-static analytical bench to a self-sustaining autonomous scientific research system.

---

## Strategic Framing

AiSci's core competitive advantage — the `evidence-ledger.md` epistemic state machine — must be preserved at all costs. Every change in this roadmap must leave the ledger and its promotion gates intact.

The three gaps identified in Phase 2 define three tracks of work:

| Track | Gap | Target State |
| :--- | :--- | :--- |
| **A** | Static Sandbox | Agents can write, run, and iterate on new physics code autonomously |
| **B** | DeerFlow Bloat | Lean runtime: direct SDK calls + MCP, no web-app overhead |
| **C** | Broken Research Loop | Agents autonomously extend `next-actions.md` based on ledger anomalies |

---

## Track A — Dynamic Code Execution Sandbox

**Problem:** All fit models are hardcoded in `physics/src/`. If data suggests a new model, a human must write the code. Frontier agents (OpenHands) would write it on the fly.

### A1 — Sandboxed Jupyter Kernel (P1)
- Provision a persistent, isolated Jupyter/IPython kernel (or `subprocess`-based sandbox) reachable by agents via a DeerFlow tool or MCP endpoint.
- Agents can write, submit, and receive output from arbitrary Python cells without touching the `physics/src/` tracked files.
- Hard constraints: kernel must have read access to `physics/data/` and write access only to `research/robert/runs/YYYY-MM-DD-*/scratch/`. No direct writes to `physics/src/`.
- **Acceptance:** Agent autonomously derives and tests a new Tsallis variant (adding a temperature-dependent power-law prefactor) in a scratch notebook, confirms chi²/ndf, and proposes promoting the model as a new `FitSpec` to `physics/src/`.

### A2 — Auto-FitSpec Promotion Gate (P2)
- When a new model tested in scratch produces chi²/ndf lower than the current best by > 2σ on ≥ 8/10 bins, the agent is permitted to propose a `git diff` for `physics/src/fitting_pipeline.py` adding the new `FitSpec`.
- This diff must be reviewed by Robert via PR before merge. The agent writes the PR body documenting the chi²/ndf comparison and AIC/BIC delta.
- **Acceptance:** PR template for auto-proposed `FitSpec` additions exists in `.github/pull_request_template.md`.

---

## Track B — DeerFlow De-Vendoring

**Problem:** The entire `deployment/deer-flow/` subtree (~50K lines of vendored code) is gitignored, making reproducible deploys fragile and CI impossible to verify for the core orchestration layer.

### B1 — Decision: Commit to De-Vendor Timeline (P0)
- Create `docs/decisions/2026-07-09-deerflow-devendoring.md` recording the decision to de-vendor DeerFlow over Q3 2026.
- Define the "AiSci Runtime Minimal" target: direct calls to LLM SDK (e.g., `google-genai`, `anthropic`) + MCP proxy + `agent-skills/` skills. No web-app backend required for the science loop.
- **Acceptance:** Decision doc merged to `main`.

### B2 — Extract AiSci-Specific Skills from DeerFlow (P1)
- Audit `deployment/deer-flow/skills/` and `deployment/deer-flow/agents/` for any AiSci-specific workflows (physics agents, SOUL prompt, etc.).
- Move extracted skills into `agent-skills/` as standard `SKILL.md`-based skills.
- **Acceptance:** All AiSci-specific orchestration logic lives in vendor-neutral `agent-skills/` and is not dependent on the DeerFlow runtime.

### B3 — Wire `reproducible-physics-runner` as a Standalone CLI (P1)
- The `agent-skills/reproducible-physics-runner/SKILL.md` currently instructs agents to run `python physics/src/fitting_pipeline.py`. Wrap this in a tiny CLI entrypoint (`physics/cli.py`) so it can be called identically from DeerFlow, a bare Python session, or a GitHub Actions job.
- **Acceptance:** `python physics/cli.py --run-dir research/robert/runs/YYYY-MM-DD-test` runs cleanly in CI.

---

## Track C — Autonomous Research Loop

**Problem:** The research loop is human-triggered. Robert must inspect `evidence-ledger.md` and add items to `next-actions.md`. Frontier agents (OpenAI/Gemini Deep Research) formulate and initiate new investigation branches autonomously.

### C1 — Ledger Anomaly Detector Skill (P1)
- Create `agent-skills/ledger-anomaly-detector/SKILL.md`.
- The skill instructs an agent to:
  1. Read `evidence-ledger.md` in full.
  2. For any claim where `Status = Sanity checked` and the `Next Gate` has been met by evidence already present in `runs/`, automatically draft a new `next-actions.md` entry to promote it to `Validated` — subject to Robert's approval.
  3. For any claim where `Next Gate` has **not** been met and no active `next-actions.md` item addresses it, draft a new proposed action and add it to a `## 🤖 Agent-Proposed (Pending Robert Approval)` section of `next-actions.md`.
- **Acceptance:** Skill runs nightly (via `/schedule` or GitHub Actions cron), and Robert can approve/reject its proposals via a simple PR review.

### C2 — Agent Self-Queuing Rule in AGENTS.md (P1)
- Add an explicit rule to `AGENTS.md` under a new `## Autonomous Queue Management` section.
- Rule text: agents that complete a fit run and observe an unexpected result (e.g., chi²/ndf > 10 on a model previously below 5, or a new |ρ| > 0.9 correlation) **must** append a proposed follow-up item to `next-actions.md` under `## 🤖 Agent-Proposed` rather than silently proceeding.

### C3 — Iterative LLM-Driven Literature-to-Hypothesis Pipeline (P2)
- When a Tsallis or BGBW fit produces a surprising result, the agent should autonomously:
  1. Query Scite/Consensus MCP for literature where the same observable was measured.
  2. Identify candidate physical explanations from the retrieved papers.
  3. Translate the leading explanation into a candidate model modification (documented in a scratch cell, per Track A).
  4. Append the candidate to `next-actions.md`.
- **Acceptance:** End-to-end test case documented in `docs/aisci-review/` showing the loop running from an anomalous fit result to a draft `next-actions.md` entry.

---

## Immediate Backlog Items (add to `platform-backlog.md`)

1. **[P1] Create `docs/decisions/2026-07-09-deerflow-devendoring.md`** — decision and timeline for de-vendoring.
2. **[P1] Provision Jupyter kernel MCP endpoint** — expose a sandboxed Python kernel as a DeerFlow/MCP tool.
3. **[P1] Create `agent-skills/ledger-anomaly-detector/`** — skill that auto-proposes `next-actions.md` entries based on evidence-ledger gaps.
4. **[P1] Add `## Autonomous Queue Management` to `AGENTS.md`** — rule requiring agents to self-queue after anomalous results.
5. **[P2] `physics/cli.py` wrapper** — make the physics pipeline invocable identically from CLI, DeerFlow, and CI.
6. **[P2] `.github/pull_request_template.md` for FitSpec proposals** — standard template for auto-proposed model additions.
