# Onyx Physics Validation - Critical Components Documentation

Status note: this file is an operational component map. Scientific conclusions must be taken from `research/robert/evidence-ledger.md`, where claims are marked as open, sanity checked, supported, refuted, or blocked.

## 1. Physics Validation Scripts

### Tsallis Physics Validation (`physics/src/tsallis_physics_validation.py`)
- Prototype Tsallis/Tsallis-like fitting helper for baseline exploration.
- Uses simplified assumptions and must be replaced or calibrated against literature-matched Tsallis/Tsallis-Pareto formulas before publication-grade comparison.
- Includes candidate kinematic boundary logic: `limit = min(sqrt(p² - pT_cut²), p * cos(θ_cut))`
- Provides a configurable safe-fit-range filter, currently using 600 MeV as a working threshold.
- Provides velocity parameterization validation

### SymPy Validation Agent (`physics/src/sympy_validation_agent.py`)
- Provides parsing and symbolic sanity-check scaffolding.
- Current dimensional-analysis logic is not full unit validation; it mainly simplifies expressions and checks for undefined terms.
- Contains placeholders for kinematic boundary checks.
- Validates velocity parameterizations (U vs v checks)
- Flags obvious unphysical velocity expressions where implemented.

### Fitting Pipeline (`physics/src/fitting_pipeline.py`)
- iminuit-based Tsallis/Blast-Wave fitting pipeline.
- Blocked until Robert provides per-bin pT source table matching manuscript multiplicity bins.

### Data Loader (`physics/src/data_loader.py`)
- HEPData loader for boson paper spectra.
- Handles CSV and JSON table formats.

### Boson Paper Analysis (`physics/src/boson_paper_analysis.py`)
- Phase 1 sanity checks: Lorentz covariance, static limit, massless approximation.
- Re-run clean as of 2026-04-27.

## 2. MCP Services Configuration

### MCP Proxy (`deployment/onyx/nginx_configs/mcp_proxy.conf.template`)
- Endpoint: `http://localhost:8095`
- Routes: `/consensus/`, `/scite/`
- Authentication: Required for full access
- The compose-mounted template is `deployment/onyx/nginx_configs/mcp_proxy.conf.template`.
- `deployment/onyx/nginx_mcp_proxy.conf` is only a standalone reference copy and is not the live compose mount.

## 3. Onyx Persona Configuration

The HEP validation persona and its doc sets/tools are tracked in
`docs/ops/onyx-persona-ids.md` (current registry). Prompt guardrails require
evidence-ledger claim status, explicit Bose-Einstein vs Boltzmann/Jüttner
wording, no causal inference from suggestive fits, and fit-quality/baseline
gates before physical interpretation.

## 4. GPU Acceleration

Host GPU (RTX 3090), GPU device access per service, and the `nemotron_embed_vl`
NIM caveat are documented in `docs/ops/onyx-configure.md` (GPU Acceleration).

## 5. Directory Structure
- `physics/src/` — Validation and fitting scripts
- `research/robert/` — Science canon, evidence, runs
- `docs/ops/` — Platform and deployment documentation
- `docs/decisions/` — Architecture decision records
- `deployment/onyx/` — Onyx Docker stack and config
- `deployment/deer-flow/` — DeerFlow Docker stack and config
