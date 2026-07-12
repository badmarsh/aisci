# ⚛️ AiSci Research Workspace

> **Active Project:** Validation of Robert's "Boson probability function for the moving system" paper.
> **Current Focus:** $p_T$ spectrum analysis against ATLAS 13 TeV data.

---

## 🔍 Research Dashboard

### Science Status: [![Status](https://img.shields.io/badge/status-Unblocked_via_Synthetic_Data-green)](#)
Phase 1 sanity checks are complete. Baseline literature (Tsallis, Blast-Wave) is indexed.
The fitting pipeline is blocked until Robert provides per-bin $p_T$ source tables matching
the manuscript multiplicity bins.


- **Claim Tracker:** [`research/robert/evidence-ledger.md`](research/robert/evidence-ledger.md)
- **Active Task Queue:** [`research/robert/next-actions.md`](research/robert/next-actions.md)
- **Validation Plan:** [`research/robert/validation-plan.md`](research/robert/validation-plan.md)

### 🧪 Core Tools

- **[Evidence Ledger](research/robert/evidence-ledger.md):** The source of truth for all scientific claims and validation statuses.

---

## 📂 Workspace Navigation

- `research/robert/` — **The Primary Research Hub.** Contains workflow, evidence, next actions, and run reports.
- `libs/physics-core/src/` — Symbolic and numerical validation scripts (Python/SymPy).
- `deployment/aisci-dashboard/` — **AiSci Dashboard.** The active React (TanStack Start) frontend being developed as part of this repository.
- `ignition/` — **Ignition Engine.** Python FastAPI backend for the dashboard.
- `docs/decisions/` — Methodological and architectural decisions.
- `docs/ops/` — Infrastructure and deployment details.

---

## 🚀 Getting Started for Researchers

1. **Review Actions:** Check [`research/robert/next-actions.md`](research/robert/next-actions.md) for current blockers.
2. **Submit Data:** If you have new $p_T$ tables, follow the [Data Onboarding Guide](research/robert/data-onboarding.md).
3. **Run Checks:** Use `libs/physics-core/src/boson_paper_analysis.py` for local covariance and static-limit sanity checks.

---

*For technical deployment details, port mappings, and Docker logs, see the [Deployment Reference](docs/ops/deployment-reference.md).*
