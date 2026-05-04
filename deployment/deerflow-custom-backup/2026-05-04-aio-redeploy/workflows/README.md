# Open FANG Workflows

This directory contains JSON-based workflows compatible with the **Open FANG Agent Operating System**. These workflows are designed to support the project mission of monitoring and debunking high-profile malicious misinformation and demagoguery.

## Workflows

### 1. High-Impact Misinfo Monitor (`monitor_high_impact_misinfo.json`)
Monitors targeted high-profile sources to identify potential malicious lies and demagoguery.
- **Agents Used**: `collector`, `analyst`
- **Output**: A JSON list of high-priority claims.

### 2. Coordinated Debunk Engine (`debunk_malicious_demagoguery.json`)
Performs deep investigative research to debunk flagged claims using multi-source verification.
- **Agents Used**: `researcher`, `analyst`
- **Methodology**: CRAAP (Currency, Relevance, Authority, Accuracy, Purpose).
- **Output**: A cited debunking report in APA format.

### 3. Social Impact & Accountability (`social_impact_accountability.json`)
Drives real-world accountability by informing stakeholders (advertisers, regulators) of confirmed misinformation.
- **Agents Used**: `researcher`, `analyst`, `collector`
- **Output**: Drafted alerts and reports for third-party dissemination.

### 4. MSM Archive Audit (`msm_archive_audit.json`)
Compares historical mainstream media predictions/narratives with actual historical outcomes to identify systemic bias or failed foresight.
- **Agents Used**: `researcher`, `analyst`
- **Output**: An 'Accountability Audit' with accuracy scoring.

### 5. OSINT Dezinformacia Monitor (`osint_dezinformacia_monitor.json`)
Continuous OSINT loop that normalizes, detects, and enriches misinformation data for automated fact-checking.
- **Agents Used**: `collector`, `analyst`, `researcher`
- **Output**: Fact-checked correction drafts and alerts.

## Usage
These workflows can be imported into an Open FANG compatible runtime or executed via the Open FANG REST API.
