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

### Physics Validation Mode
- Active primary Onyx persona for Robert's HEP validation workflow.
- Current status is tracked in `docs/ops/onyx-rag-optimization-2026-04-27.md`.
- Attached document sets: `Physics`, `Robert Boson Draft`, and `HEP Phenomenology References`.
- Attached tools: internal search, file reader, code interpreter/Python, URL opening, Scite, Consensus, arXiv (`hep_arxiv`), INSPIRE-HEP (`hep_inspire`), and HEPData (`hepdata`).
- Prompt guardrails require evidence-ledger claim status, explicit Bose-Einstein versus Boltzmann/Juttner wording, no causal/root-cause inference from suggestive fits, and fit-quality/baseline gates before physical interpretation.

## 4. GPU Acceleration

### Configuration (`deployment/onyx/docker-compose.yml`)
- Host GPU: NVIDIA RTX 3090
- GPU device access is configured for `ollama`, `inference_model_server`, and `indexing_model_server` via Docker Compose device reservations.
- Both model servers are now configured for `DOCUMENT_ENCODER_MODEL=nomic-ai/nomic-embed-text-v1` with `EMBEDDING_DIM=768`, matching the active Nomic/768 retrieval configuration.
- Any future recreate should still verify `/api/gpu-status` and a 768-dimensional embedding response before reindex or retrieval cutover.

## 5. Directory Structure
- `physics/src/` — Validation and fitting scripts
- `research/robert/` — Science canon, evidence, runs
- `docs/ops/` — Platform and deployment documentation
- `docs/decisions/` — Architecture decision records
- `deployment/onyx/` — Onyx Docker stack and config
- `deployment/deer-flow/` — DeerFlow Docker stack and config
