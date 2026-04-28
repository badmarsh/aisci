# ⚛️ AiSci Research Workspace

> **Active Project:** Validation of Robert's "Boson probability function for the moving system" paper.
> **Current Focus:** $p_T$ spectrum analysis against ATLAS 13 TeV data.

---

## 🔍 Research Dashboard

### Science Status: **PHASE 1 (Sanity Checks)**
The model's Lorentz covariance has been verified. We are currently awaiting full $p_T$ data tables to proceed with formal fitting and baseline comparisons.

- **Claim Tracker:** [`research/robert/evidence-ledger.md`](research/robert/evidence-ledger.md)
- **Active Task Queue:** [`research/robert/next-actions.md`](research/robert/next-actions.md)
- **Validation Plan:** [`research/robert/validation-plan.md`](research/robert/validation-plan.md)

### 🧪 Core Tools
- **[Onyx RAG](http://localhost:3000):** Use the **"Physics Validation Mode"** persona for literature search and manuscript extraction.
- **[DeerFlow](http://localhost:2026):** Orchestration for complex multi-tool research workflows.
- **[Evidence Ledger](research/robert/evidence-ledger.md):** The source of truth for all scientific claims and validation statuses.

---

## 📂 Workspace Navigation

- `research/robert/` — **The Primary Research Hub.** Contains workflow, evidence, next actions, and run reports.
- `physics/src/` — Symbolic and numerical validation scripts (Python/SymPy).
- `docs/decisions/` — Methodological and architectural decisions.
- `docs/ops/` — Infrastructure and deployment details.

---

## 🚀 Getting Started for Researchers

1. **Review Actions:** Check [`research/robert/next-actions.md`](research/robert/next-actions.md) for current blockers.
2. **Submit Data:** If you have new $p_T$ tables, follow the [Data Onboarding Guide](research/robert/data-onboarding.md).
3. **Run Checks:** Use `physics/src/boson_paper_analysis.py` for local covariance and static-limit sanity checks.

---

*For technical deployment details, port mappings, and Docker logs, see the [Deployment Reference](docs/ops/deployment-reference.md).*
