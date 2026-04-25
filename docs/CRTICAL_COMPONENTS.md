# Onyx Physics Validation - Critical Components Documentation

## 1. Physics Validation Scripts

### Tsallis Physics Validation (`/src/tsallis_physics_validation.py`)
- Implements Tsallis Statistics fitting function (replaces flawed 7-parameter Boltzmann approximation)
- Includes proper kinematic boundary logic: `limit = min(sqrt(p² - pT_cut²), p * cos(θ_cut))`
- Enforces safe fit range (excludes data below 600 MeV)
- Provides velocity parameterization validation

### SymPy Validation Agent (`/src/sympy_validation_agent.py`)
- Performs dimensional analysis on physics equations
- Checks kinematic boundary conditions
- Validates velocity parameterizations (U vs v checks)
- Flags unphysical equations or results

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
- Activated through Onyx UI
- Automatically engages Consensus and Scite MCPs
- Uses SymPy validator for equation analysis
- Specialized for high-energy physics peer-review

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