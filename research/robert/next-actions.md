# Robert — Science Next Actions

This is the canonical task queue for Robert's physics workflow.
Platform-blocked items (waiting on Ollama, Scite key, etc.) are noted separately; their resolution is tracked in `docs/ops/platform-backlog.md`.

Science tasks become active only after acceptance by Robert. Do not add, remove, or reword items without Robert's approval.

Evidence states referenced here are defined in `docs/decisions/2026-04-26-science-evidence-standards.md`.

---

## 🔴 Blocked — Data Table Required

### [B-01] Supply per-multiplicity-bin pT spectrum table
**Blocking:** `fitting_pipeline.py`, `tsallis_physics_validation.py`, all chi2/ndf results
**What is needed:** Per-bin pT spectra matching multiplicity classes `21–30, 31–40, 41–50, 51–60, 61–70, 71–80, 81–90, 91–100, 101–125, 126–150`
**Why HEPData is insufficient:** Record `ins1419652` returns only inclusive spectra, not per-class bins
**Action:** Robert to provide the data table directly, or identify the correct HEPData record / paper table number
**Unblocks:** `data_loader.py` → `fit_input.csv` → full fitting pipeline

---

## 🟡 Open — Can Proceed Now (symbolic layer is unblocked)

### [O-01] Resolve χ²/ndf absence in manuscript
**Status in ledger:** Open concern — highest priority
**What is missing:** The manuscript does not report goodness-of-fit (χ²/ndf) for the fits shown in its figures
**Action:** Confirm whether χ²/ndf values exist in supplementary material or an earlier version; if absent, flag as a required addition in the referee report draft
**Script:** `boson_paper_analysis.py` §6 already flags this — no new code needed

### [O-02] Confirm U₂ ≈ 0.011 ± 0.847 is a known instability
**Status in ledger:** Flagged — numerics show U₂ unconstrained at high multiplicity
**What is needed:** Robert to confirm whether this is expected (a known fitting instability at high multiplicity in the original paper) or a new finding
**Action:** Robert reads `boson_paper_analysis.py` §7 output and provides a one-line confirmation or correction for the ledger

### [O-03] Verify Cooper-Frye static-limit recovery is cited in manuscript
**Status in ledger:** Sanity checked (§5 passes)
**What is needed:** Confirm the manuscript explicitly states the U→0 limit recovers the static Cooper-Frye form, or note that it is implicit
**Action:** Read manuscript §2 or §3; add a citation note to `evidence-ledger.md` claim C-05

### [O-04] Move manuscript PDF to canonical location
**Current path:** `literature/Boson probability function for the moving system.pdf`
**Recommended path:** `research/robert/manuscript/boson-probability-function-moving-system.pdf`
**Rationale:** Co-location with `evidence-ledger.md`, `fit-plan.md`, and `validation-plan.md` per the `research/robert/` boundary rule in `AGENTS.md`
**Action:** Robert confirms; agent performs `git mv` and updates any cross-references

---

## ✅ Completed

| Item | Completed | Notes |
|---|---|---|
| Symbolic validation of core distribution §1–§5 | 2026-04-26 | `boson_paper_analysis.py` all sections green |
| U parameterization verified | 2026-04-26 | `v < c`, `γv = U`, `Y = arcsinh(U)` confirmed |
| η integration proved | 2026-04-26 | `U^μp_μ = pT·cosh(η−Y)` via SymPy |
| Tsallis/Blast-Wave baseline scripts written | 2026-04-27 | `tsallis_physics_validation.py` ready; awaiting data |
| Fitting pipeline infrastructure built | 2026-04-27 | `fitting_pipeline.py` ready; awaiting `fit_input.csv` |
