# Comprehensive AISCI Codebase Audit & Cleanup

You are conducting a thorough audit of the entire AISCI platform including the main codebase, Onyx deployment, DeerFlow configuration, helper scripts, and all supporting infrastructure. Your goal is to identify and document issues across these categories:

## 1. Redundancy & Duplication
- Find duplicate code, functions, or logic across files
- Identify redundant configuration files or settings
- Locate multiple implementations of the same functionality
- Find duplicate documentation or conflicting instructions
- Check for redundant dependencies in requirements files

## 2. Outdated & Deprecated Items
- Identify outdated dependencies (Python packages, Docker images, etc.)
- Find deprecated API usage or library calls
- Locate old configuration formats that should be migrated
- Check for references to deprecated Onyx/Claude API endpoints
- Find outdated documentation referencing old versions or removed features
- Identify old TODO/FIXME comments that are no longer relevant

## 3. Temporary & Test Artifacts
- Find temporary files that shouldn't be committed (*.tmp, *.bak, test_*.py in wrong locations)
- Identify debug code, print statements, or commented-out blocks
- Locate test data or fixtures in production code paths
- Find hardcoded test credentials or API keys
- Check for temporary workarounds marked with "HACK" or "TEMP"

## 4. Incompatibilities & Conflicts
- Check for version conflicts between dependencies
- Identify incompatible settings between Onyx, DeerFlow, and AISCI components
- Find mismatched API versions or schemas
- Locate configuration conflicts (e.g., different ports, paths, or URLs)
- Check for Python 2 vs 3 compatibility issues
- Identify Docker compose version incompatibilities

## 5. Security & Secrets
- Find exposed secrets, API keys, or credentials in code
- Identify weak or default passwords in configs
- Check for insecure HTTP connections that should be HTTPS
- Locate overly permissive file permissions or access controls
- Find missing authentication or authorization checks

## 6. Code Quality Issues
- Identify unused imports, functions, classes, or files
- Find dead code paths or unreachable logic
- Locate overly complex functions that need refactoring
- Check for inconsistent naming conventions
- Find missing error handling or bare except clauses
- Identify hardcoded values that should be environment variables

## 7. Configuration Issues
- Find hardcoded paths that should be configurable
- Identify missing or incomplete .env.example files
- Check for inconsistent configuration between environments
- Locate configuration files with unclear or missing documentation
- Find settings that conflict with deployment documentation

## 8. Documentation Gaps
- Identify code without docstrings or comments
- Find outdated README files
- Locate missing setup or deployment instructions
- Check for undocumented environment variables
- Find API endpoints without documentation

## 9. Structural Issues
- Identify misplaced files (e.g., scripts in wrong directories)
- Find circular dependencies or tight coupling
- Locate monolithic files that should be split
- Check for inconsistent project structure
- Identify missing __init__.py files in Python packages

## 10. Performance & Resource Issues
- Find inefficient database queries or N+1 problems
- Identify memory leaks or resource exhaustion risks
- Locate blocking operations that should be async
- Check for missing indexes or caching
- Find large files or assets that should be optimized

## Audit Scope

### Core AISCI Codebase
- `/physics/` - Physics simulation and data processing
- `/agent-skills/` - Agent skill implementations
- `/docs/` - Documentation and operational guides
- Root configuration files

### Deployment Infrastructure
- `/deployment/onyx/` - Onyx RAG platform deployment
- `/deployment/deer-flow/` - DeerFlow agent configuration
- `/deployment/helper/` - Helper scripts and utilities
- Docker configurations and compose files

### Configuration Files
- `.env` files and environment configurations
- `docker-compose.yml` files
- `config.yaml` and extension configurations
- `requirements.txt` and dependency files
- Nginx and proxy configurations

## Output Format

For each issue found, provide:

1. **Category**: Which of the 10 categories above
2. **Severity**: Critical / High / Medium / Low
3. **Location**: Specific file path and line numbers
4. **Description**: Clear explanation of the issue
5. **Impact**: What problems this causes or could cause
6. **Recommendation**: Specific action to fix or improve
7. **Effort**: Estimated effort (Quick / Medium / Large)

## Priority Focus Areas

1. **Security issues** - Address immediately
2. **Breaking incompatibilities** - Fix before they cause outages
3. **Redundant/conflicting configs** - Consolidate to prevent confusion
4. **Outdated dependencies** - Update to maintain security and compatibility
5. **Documentation gaps** - Fill to improve maintainability
6. **Code quality** - Refactor to reduce technical debt

## Execution Instructions

1. Start with a systematic file-by-file review of the repository
2. Cross-reference configurations between components
3. Test for actual incompatibilities where possible
4. Prioritize findings by severity and impact
5. Group related issues together
6. Provide actionable recommendations, not just observations
7. Create a summary report with statistics and priority actions

## Success Criteria

- All critical security issues identified
- All redundant or conflicting configurations documented
- All outdated dependencies catalogued with upgrade paths
- All temporary/test artifacts flagged for removal
- Comprehensive improvement roadmap created
- Estimated effort for cleanup provided

Begin the audit systematically, starting with security and configuration issues, then moving to code quality and documentation. Be thorough but practical - focus on issues that actually impact functionality, security, or maintainability.
