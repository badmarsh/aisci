# Onyx Physics Validation System

## Overview
This project implements a physics validation pipeline using Onyx to systematically validate high-energy physics papers before code implementation.

## Directory Structure

### `/physics/`
- Physics-related components:
  - `/src/` - Core physics validation scripts:
    - `tsallis_physics_validation.py` - Implements Tsallis Statistics (replaces flawed Boltzmann approximation)
    - `sympy_validation_agent.py` - Performs dimensional analysis and kinematic boundary checks
  - `/physics_env/` - Virtual environment for physics validation scripts

### `/deployment/`
- All deployment-related files:
  - `/onyx/` - Onyx-specific deployment files:
    - `docker-compose.yml` - Main deployment configuration
    - `nginx_mcp_proxy.conf` - MCP service proxy configuration
    - `.env`, `env.template` - Environment configuration
    - `nginx_configs/` - Nginx configuration files
    - Other Onyx deployment files
  - `/deer-flow/` - Deer-Flow-specific deployment files (planned)

### `/docs/`
- Documentation files:
  - `README.md` - Project overview
  - `CRTICAL_COMPONENTS.md` - Technical documentation for key components
  - `PROJECT_RULES.md` - Development and maintenance guidelines
  - `TROUBLESHOOTING.md` - Issue resolution guide
  - `FINAL_SUMMARY.md` - Project completion summary
  - `GPU_OPTIMIZATION_DOCS.md` - GPU acceleration setup

### `/backup_before_wipe/`
- Backup data for restoring Onyx settings

### `/generated_files/`
- Output from Onyx agents (preserved)

## Core Features

### Physics Validation Scripts
- Implements Tsallis Statistics fitting function (replaces flawed Boltzmann approximation)
- Includes proper kinematic boundary logic: `limit = min(sqrt(p² - pT_cut²), p * cos(θ_cut))`
- Enforces safe fit range (excludes data below 600 MeV)
- Provides velocity parameterization validation

### MCP Services
- Consensus MCP: Formula extraction and literature search
- Scite MCP: Citation context validation
- Both accessible via proxy at `http://localhost:8095/[consensus|scite]/`

### Physics Validation Mode
- Available in Onyx UI as "Physics Validation Mode" persona
- Automatically engages all validation tools and MCP services
- Specialized for high-energy physics paper analysis

### GPU Acceleration
- RTX GPU utilized for document processing
- Private, local processing for sensitive documents
- Optimized embedding models for faster analysis

## Deployment Status
⚠️ **Note:** The Onyx system was running but had to be stopped for reorganization. Due to issues with the docker-compose system in this environment, the services are currently not running. See `/deployment/DEPLOYMENT_STATUS.md` for details on how to restart the system.

## Usage
1. Once deployed, access Onyx UI at `http://localhost:3000`
2. Select "Physics Validation Mode" persona
3. Upload physics papers for automated validation
4. Check results and generated scripts in `/generated_files/`