# Onyx Physics Validation - Critical Components Documentation

Status note: this file is an operational component map. Scientific conclusions must be taken from `research/robert/evidence-ledger.md`, where claims are marked as open, sanity checked, supported, refuted, or blocked.

## 1. Physics Validation Scripts

### Tsallis Physics Validation (`/src/tsallis_physics_validation.py`)
- Prototype Tsallis/Tsallis-like fitting helper for baseline exploration.
- Uses simplified assumptions and must be replaced or calibrated against literature-matched Tsallis/Tsallis-Pareto formulas before publication-grade comparison.
- Includes candidate kinematic boundary logic: `limit = min(sqrt(p² - pT_cut²), p * cos(θ_cut))`
- Provides a configurable safe-fit-range filter, currently using 600 MeV as a working threshold.
- Provides velocity parameterization validation

### SymPy Validation Agent (`/src/sympy_validation_agent.py`)
- Provides parsing and symbolic sanity-check scaffolding.
- Current dimensional-analysis logic is not full unit validation; it mainly simplifies expressions and checks for undefined terms.
- Contains placeholders for kinematic boundary checks.
- Validates velocity parameterizations (U vs v checks)
- Flags obvious unphysical velocity expressions where implemented.

## 2. MCP Services Configuration

### Consensus MCP (`/config/nginx_mcp_proxy.conf`)
- Endpoint: `http://localhost:8095/consensus/`
- Purpose: Formula extraction and search in high-energy physics literature
- Authentication: Required for full access

### Scite MCP (`/config/nginx_mcp_proxy.conf`)
- Endpoint: `http://localhost:8095/scite/`
- Purpose: Citation context validation
- Authentication: Required for full access

## 3. Onyx Persona Configuration

### Physics Validation Mode
- Active listed Onyx persona for Robert's HEP validation workflow.
- Current status is tracked in `docs/ops/onyx-rag-optimization-2026-04-27.md`.
- Attached document sets: `Physics`, `Robert Boson Draft`, and `HEP Phenomenology References`.
- Attached tools: internal search, file reader, code interpreter/Python, URL opening, Scite, and Consensus.
- Prompt guardrails require evidence-ledger claim status, explicit Bose-Einstein versus Boltzmann/Juttner wording, no causal/root-cause inference from suggestive fits, and fit-quality/baseline gates before physical interpretation.
- arXiv, INSPIRE-HEP, and HEPData tools remain missing and are tracked in `docs/ops/platform-backlog.md`.

## 4. GPU Acceleration

### Configuration (`/config/litellm_config.yaml`)
- Uses local embedding models for document processing
- Leverages RTX GPU for faster PDF parsing
- Maintains privacy with local processing

## 5. Directory Structure
- `/src/` - Core validation scripts
- `/docs/` - Project documentation
- `/config/` - System configuration files
- `/generated_files/` - Output from Onyx agents
