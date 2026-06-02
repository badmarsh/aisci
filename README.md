# ⚛️ AiSci Research Workspace

> **Active Project:** Validation of Robert's "Boson probability function for the moving system" paper.
> **Current Focus:** $p_T$ spectrum analysis against ATLAS 13 TeV data.

---

## 🔍 Research Dashboard

### Science Status: **Blocked on Data Input for Phase 2 Fitting**
Phase 1 sanity checks are complete. Baseline literature (Tsallis, Blast-Wave) is indexed.
The fitting pipeline is blocked until Robert provides per-bin $p_T$ source tables matching
the manuscript multiplicity bins.
⚠️ RAG Status: In Progress — The Onyx corpus has structural gaps: questions grounded
in docs/ content (Q3, Q5 of the evaluation set) return no hits because the docs/
connector is not indexed. Literature PDFs (Khuntia 2019, Rath 2020) were re-uploaded
2026-05-30. See docs/ops/rag-evaluation-set.md and
Multica Issues for active tasks; docs/ops/platform-status.md for system state.

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
