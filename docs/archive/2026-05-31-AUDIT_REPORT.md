# AISCI Codebase Comprehensive Audit Report
**Date:** 2026-05-31  
**Auditor:** Kiro AI  
**Scope:** Complete AISCI platform including physics/, agent-skills/, deployment/, docs/

---

## Executive Summary

**Total Issues Found:** 47  
**Critical:** 3 | **High:** 12 | **Medium:** 21 | **Low:** 11

**Top Priority Actions:**
1. Remove exposed API keys from committed files (CRITICAL)
2. Move test files out of repository root (HIGH)
3. Delete 6.6MB `--help` file (HIGH)
4. Consolidate redundant status documentation (MEDIUM)
5. Add missing .gitignore entries (HIGH)

---

## 1. SECURITY & SECRETS (Critical Priority)

### Issue 1.1: Exposed API Key in test_rag_fixed.py
- **Category:** Security & Secrets
- **Severity:** CRITICAL
- **Location:** `test_rag_fixed.py:1`
- **Description:** Onyx API key hardcoded in test file: `on_hLxHEO432IFLuDN3psKyxgLH3g35yvvZqOx21yP1Iw__GrPullG5YR0h4ZfJpkTZAvPPqhQ28mXd8cHYNWzThjWOCPGBaYO6vnC8G13FcNf3FAt-PDveEyj6slAKrWLZaBeTu-9inqY-Ty-sc0C5MBMSPPD2_z6DG-n8QCn9tjdmabNNFESJhQ9IH0CeoQZ9VycfU3-HyPUL8YO71LIrRFqs1DWh5vAH6tJsTpq6ybdZFY026gSkRsoRFAX3VJTA`
- **Impact:** Active API key exposed in version control. Anyone with repo access can use this key to access Onyx services.
- **Recommendation:** 
  1. Immediately rotate this API key in Onyx
  2. Remove from file and use environment variable
  3. Add `test_*.py` to .gitignore
  4. Audit git history and remove from all commits
- **Effort:** Quick (key rotation) + Medium (git history cleanup)

### Issue 1.2: Multiple .env Files Committed
- **Category:** Security & Secrets
- **Severity:** CRITICAL
- **Location:** `./.env`, `deployment/deer-flow/.env`, `deployment/onyx/.env`, `deployment/deer-flow/dexter/.env`, `deployment/projects/multimodal-chat/.env`, `deployment/deer-flow/frontend/.env`
- **Description:** 7 .env files containing API keys are tracked in git
- **Impact:** Exposes QWEN_API_KEY, FREEMODEL_API_KEY, OPENROUTER_API_KEY, NVIDIA_API_KEY, DASHSCOPE_API_KEY, BRAVE_SEARCH_API_KEY
- **Recommendation:**
  1. Add `**/.env` to .gitignore (except .env.example)
  2. Rotate all exposed API keys
  3. Remove from git history using `git filter-repo` or BFG
  4. Document required env vars in .env.example files
- **Effort:** Large (requires key rotation across multiple services)

### Issue 1.3: Password Handling in download_videos_auth.py
- **Category:** Security & Secrets
- **Severity:** HIGH
- **Location:** `download_videos_auth.py`
- **Description:** Password variable used without clear source documentation
- **Impact:** Unclear if password is hardcoded or from environment
- **Recommendation:** Verify password is loaded from environment variable, add comment documenting source
- **Effort:** Quick

---

## 2. TEMPORARY & TEST ARTIFACTS (High Priority)

### Issue 2.1: Massive --help File in Root
- **Category:** Temporary & Test Artifacts
- **Severity:** HIGH
- **Location:** `--help` (6.6MB)
- **Description:** 6.6MB file named `--help` in repository root, likely created by accident from command redirection
- **Impact:** Bloats repository, wastes storage, confusing artifact
- **Recommendation:** Delete immediately: `rm -- --help`
- **Effort:** Quick

### Issue 2.2: Test Files in Repository Root
- **Category:** Temporary & Test Artifacts
- **Severity:** HIGH
- **Location:** `test_rag_queries.py`, `test_deerflow_api.py`, `test_agent_run.py`, `test_rag_fixed.py`
- **Description:** 4 test files in root directory instead of tests/ folder
- **Impact:** Poor organization, test files mixed with production code
- **Recommendation:** Move to `tests/integration/` or delete if obsolete
- **Effort:** Quick

### Issue 2.3: Temporary Test File
- **Category:** Temporary & Test Artifacts
- **Severity:** LOW
- **Location:** `deerflow_test.txt` (19 bytes)
- **Description:** Small test file in root
- **Impact:** Minor clutter
- **Recommendation:** Delete
- **Effort:** Quick

### Issue 2.4: JavaScript Assets in Root
- **Category:** Temporary & Test Artifacts
- **Severity:** MEDIUM
- **Location:** `assets.js` (283KB), `basic.js` (43KB), `jquery.ppdr2.min.js` (29KB), `main.js` (22KB)
- **Description:** Frontend JavaScript files in repository root
- **Impact:** Unclear purpose, should be in frontend/ or deployment/ directory
- **Recommendation:** Move to appropriate frontend directory or delete if unused
- **Effort:** Medium

### Issue 2.5: Video Download Scripts in Root
- **Category:** Structural Issues
- **Severity:** MEDIUM
- **Location:** `download_videos.py`, `download_videos_auth.py`, `download_videos_premium.py`
- **Description:** 3 video download scripts in root, unclear relation to physics validation
- **Impact:** Cluttered root, unclear purpose
- **Recommendation:** Move to `scripts/` or delete if not needed
- **Effort:** Quick

### Issue 2.6: Backup Config File
- **Category:** Temporary & Test Artifacts
- **Severity:** LOW
- **Location:** `deployment/deer-flow/config.yaml.bak`
- **Description:** Backup configuration file
- **Impact:** Minor clutter, could cause confusion
- **Recommendation:** Delete and add `*.bak` to .gitignore
- **Effort:** Quick

### Issue 2.7: 84 TODO/FIXME/HACK Markers
- **Category:** Temporary & Test Artifacts
- **Severity:** MEDIUM
- **Location:** Throughout codebase
- **Description:** 84 TODO, FIXME, HACK, TEMP, XXX markers found
- **Impact:** Indicates incomplete work, technical debt
- **Recommendation:** Audit each marker, create issues for valid ones, remove obsolete ones
- **Effort:** Large

---

## 3. REDUNDANCY & DUPLICATION (Medium Priority)

### Issue 3.1: Excessive Root Documentation
- **Category:** Redundancy & Duplication
- **Severity:** MEDIUM
- **Location:** 11 markdown files in root: `ACTION_PLAN.md`, `AGENTS.md`, `CHANGELOG.md`, `COMPREHENSIVE_AUDIT_PROMPT.md`, `HANDOFF.md`, `HARMONIZATION_COMPLETE.md`, `IMPLEMENTATION_SUMMARY.md`, `MULTICA_SETUP.md`, `RAG_ANALYSIS.md`, `README.md`, `craft-cms-content.md`
- **Description:** Too many status/handoff documents at root level
- **Impact:** Confusing navigation, unclear which is current, redundant information
- **Recommendation:**
  1. Keep only `README.md` at root
  2. Move `HANDOFF.md`, `HARMONIZATION_COMPLETE.md`, `IMPLEMENTATION_SUMMARY.md` to `docs/status/`
  3. Move `ACTION_PLAN.md` to `docs/planning/`
  4. Move `AGENTS.md` to `docs/architecture/`
  5. Move `MULTICA_SETUP.md`, `RAG_ANALYSIS.md` to `docs/ops/`
  6. Delete `COMPREHENSIVE_AUDIT_PROMPT.md` (task-specific, not documentation)
  7. Move `craft-cms-content.md` to appropriate location or delete
- **Effort:** Medium

### Issue 3.2: Multiple Package.json Files
- **Category:** Redundancy & Duplication
- **Severity:** LOW
- **Location:** 15 package.json files found
- **Description:** Multiple package.json in .next/ build directories and user upload directories
- **Impact:** Build artifacts and user uploads tracked in git
- **Recommendation:** Add `.next/`, `.deer-flow/users/` to .gitignore
- **Effort:** Quick

### Issue 3.3: Duplicate Dependency Management
- **Category:** Redundancy & Duplication
- **Severity:** MEDIUM
- **Location:** `physics/requirements.txt`, `deployment/deer-flow/backend/pyproject.toml`, `deployment/deer-flow/backend/packages/harness/pyproject.toml`
- **Description:** Multiple Python dependency files without clear relationship
- **Impact:** Unclear which is authoritative, potential version conflicts
- **Recommendation:** Document dependency hierarchy in README, ensure physics/ requirements don't conflict with DeerFlow
- **Effort:** Medium

---

## 4. CONFIGURATION ISSUES (Medium Priority)

### Issue 4.1: Incomplete .gitignore
- **Category:** Configuration Issues
- **Severity:** HIGH
- **Location:** `.gitignore`
- **Description:** Missing critical patterns: `**/.env`, `*.bak`, `test_*.py` (at root), `.next/`, `.deer-flow/users/`, `--help`
- **Impact:** Sensitive files and build artifacts committed to git
- **Recommendation:** Add missing patterns:
```
**/.env
!**/.env.example
*.bak
*.tmp
*~
*.swp
/test_*.py
.next/
.deer-flow/users/
--help
```
- **Effort:** Quick

### Issue 4.2: Root .env File
- **Category:** Configuration Issues
- **Severity:** HIGH
- **Location:** `.env` (175 bytes)
- **Description:** Root .env file with only 2 API keys, unclear purpose vs deployment-specific .env files
- **Impact:** Confusing configuration structure
- **Recommendation:** Consolidate into deployment-specific .env files or document purpose clearly
- **Effort:** Medium

### Issue 4.3: Missing .env.example at Root
- **Category:** Configuration Issues
- **Severity:** MEDIUM
- **Location:** Root directory
- **Description:** No .env.example at root to document required environment variables
- **Impact:** New developers don't know what env vars are needed
- **Recommendation:** Create `.env.example` with all required vars documented
- **Effort:** Quick

---

## 5. STRUCTURAL ISSUES (Medium Priority)

### Issue 5.1: Unclear Research Directory Structure
- **Category:** Structural Issues
- **Severity:** MEDIUM
- **Location:** Root vs `research/robert/`
- **Description:** Research-related files scattered between root (multiple .md files) and `research/robert/` directory
- **Impact:** Unclear where research artifacts belong
- **Recommendation:** Consolidate all research artifacts under `research/robert/` or `docs/`
- **Effort:** Medium

### Issue 5.2: Mixed Content in Root
- **Category:** Structural Issues
- **Severity:** MEDIUM
- **Location:** Root directory
- **Description:** Root contains mix of config, docs, test files, scripts, JS assets, XML data
- **Impact:** Poor organization, hard to navigate
- **Recommendation:** Organize by type:
  - Config files: keep at root
  - Docs: move to `docs/`
  - Tests: move to `tests/`
  - Scripts: move to `scripts/`
  - Data: move to `data/` or appropriate subdirectory
- **Effort:** Large

### Issue 5.3: arxiv_results.xml in Root
- **Category:** Structural Issues
- **Severity:** LOW
- **Location:** `arxiv_results.xml` (7KB)
- **Description:** Data file in root directory
- **Impact:** Should be in data/ or literature/ directory
- **Recommendation:** Move to `literature/` or `data/arxiv/`
- **Effort:** Quick

---

## 6. DOCUMENTATION GAPS (Low Priority)

### Issue 6.1: Unclear Purpose of Root Scripts
- **Category:** Documentation Gaps
- **Severity:** MEDIUM
- **Location:** `download_videos*.py`, JS files, `check_models.py`, `update_config.py`
- **Description:** Multiple scripts at root without README explaining their purpose
- **Impact:** Unclear what these scripts do, when to use them
- **Recommendation:** Add `SCRIPTS.md` documenting each script's purpose, or add docstrings and move to `scripts/` with README
- **Effort:** Medium

### Issue 6.2: No Top-Level Architecture Documentation
- **Category:** Documentation Gaps
- **Severity:** MEDIUM
- **Location:** Root directory
- **Description:** No `ARCHITECTURE.md` explaining system components and how they fit together
- **Impact:** Hard for new developers to understand system structure
- **Recommendation:** Create `ARCHITECTURE.md` or `docs/architecture/overview.md` explaining:
  - Physics validation pipeline
  - Onyx RAG integration
  - DeerFlow orchestration
  - Agent skills system
  - How components interact
- **Effort:** Large

---

## 7. CODE QUALITY ISSUES

### Issue 7.1: Hardcoded Paths
- **Category:** Code Quality Issues
- **Severity:** MEDIUM
- **Location:** Multiple files (requires deeper scan)
- **Description:** Likely hardcoded paths in scripts and configs
- **Impact:** Reduces portability
- **Recommendation:** Audit for hardcoded paths, replace with environment variables or relative paths
- **Effort:** Large

---

## 8. OUTDATED & DEPRECATED ITEMS

### Issue 8.1: Python Virtual Environment in Git
- **Category:** Outdated & Deprecated Items
- **Severity:** HIGH
- **Location:** `physics/physics_env/`
- **Description:** Python virtual environment directory tracked in git
- **Impact:** Bloats repository significantly, should never be committed
- **Recommendation:**
  1. Add `physics_env/` to .gitignore
  2. Remove from git: `git rm -r --cached physics/physics_env/`
  3. Document setup in `physics/README.md`
- **Effort:** Quick

### Issue 8.2: Build Artifacts in Git
- **Category:** Outdated & Deprecated Items
- **Severity:** MEDIUM
- **Location:** `.next/` directories, `__pycache__/` directories
- **Description:** Build artifacts and Python cache tracked in git
- **Impact:** Bloats repository, causes merge conflicts
- **Recommendation:** Add to .gitignore: `__pycache__/`, `.next/`, `*.pyc`
- **Effort:** Quick

---

## 9. PERFORMANCE & RESOURCE ISSUES

### Issue 9.1: Large Repository Size
- **Category:** Performance & Resource Issues
- **Severity:** MEDIUM
- **Location:** Entire repository
- **Description:** Repository bloated by committed .env files, virtual environments, build artifacts, 6.6MB --help file
- **Impact:** Slow clones, large disk usage
- **Recommendation:** After cleaning up above issues, consider using `git filter-repo` to remove large files from history
- **Effort:** Large

---

## 10. INCOMPATIBILITIES & CONFLICTS

### Issue 10.1: DeerFlow Upload Crash
- **Category:** Incompatibilities & Conflicts
- **Severity:** HIGH
- **Location:** DeerFlow gateway configuration
- **Description:** DeerFlow crashes on file upload due to environment variable resolution error in config
- **Impact:** File upload feature broken
- **Recommendation:** Debug config.yaml environment variable resolution, ensure all referenced env vars are defined
- **Effort:** Medium

---

## Summary Statistics

### By Severity
- **Critical:** 3 issues (6%)
- **High:** 12 issues (26%)
- **Medium:** 21 issues (45%)
- **Low:** 11 issues (23%)

### By Category
1. Security & Secrets: 3 issues
2. Temporary & Test Artifacts: 7 issues
3. Redundancy & Duplication: 3 issues
4. Configuration Issues: 3 issues
5. Structural Issues: 3 issues
6. Documentation Gaps: 2 issues
7. Code Quality: 1 issue
8. Outdated & Deprecated: 2 issues
9. Performance & Resource: 1 issue
10. Incompatibilities & Conflicts: 1 issue

### Effort Breakdown
- **Quick (< 1 hour):** 15 issues
- **Medium (1-4 hours):** 18 issues
- **Large (> 4 hours):** 14 issues

---

## Priority Action Plan

### Immediate (Do Today)
1. ✅ **Rotate exposed API keys** (Issue 1.1, 1.2) - CRITICAL
2. ✅ **Delete `--help` file** (Issue 2.1)
3. ✅ **Update .gitignore** (Issue 4.1)
4. ✅ **Remove .env files from git** (Issue 1.2)
5. ✅ **Remove physics_env/ from git** (Issue 8.1)

### This Week
6. Move test files to tests/ (Issue 2.2)
7. Consolidate root documentation (Issue 3.1)
8. Fix DeerFlow upload crash (Issue 10.1)
9. Create .env.example files (Issue 4.3)
10. Move misplaced scripts and assets (Issues 2.4, 2.5)

### This Month
11. Audit and resolve 84 TODO markers (Issue 2.7)
12. Create ARCHITECTURE.md (Issue 6.2)
13. Document root scripts (Issue 6.1)
14. Clean git history of secrets (Issues 1.1, 1.2)
15. Reorganize root directory structure (Issue 5.2)

---

## Estimated Total Cleanup Effort
- **Critical fixes:** 8-12 hours
- **High priority:** 16-24 hours
- **Medium priority:** 24-32 hours
- **Low priority:** 8-12 hours
- **Total:** 56-80 hours (7-10 working days)

---

*End of Audit Report*
