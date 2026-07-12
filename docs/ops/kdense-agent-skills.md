# Multica Agent Integration & K-Dense Scientific Skills

> Historical record only — not active operational guidance.

**Date:** 2026-05-31  
**Status:** Research complete, skills installed, integration wrappers drafted  
**Related:** MULTICA_SETUP.md, AGENTS.md

## Overview

This document captures the integration architecture for connecting Multica task management with the AiSci agent ecosystem, plus the evaluation and installation of K-Dense scientific agent skills.

## 1. K-Dense Scientific Skills Installation

### Installed Skills (10 high-priority)

Successfully installed 10 HEP-relevant skills from [K-Dense-AI/scientific-agent-skills](https://github.com/k-dense-ai/scientific-agent-skills) (143 total skills, MIT licensed):

| Skill | Priority | Relevance | Location |
|-------|----------|-----------|----------|
| **sympy** | Critical | Symbolic math, already using sympy_validation_agent.py | `.agents/skills/sympy/` |
| **paper-lookup** | Critical | 10 academic DBs (arXiv, Semantic Scholar, OpenAlex) | `.agents/skills/paper-lookup/` |
| **scientific-visualization** | Critical | Publication-quality plots for pT spectra, chi²/ndf | `.agents/skills/scientific-visualization/` |
| **statistical-analysis** | Critical | AIC/BIC, chi²/ndf, covariance gates | `.agents/skills/statistical-analysis/` |
| **matplotlib** | High | Fit plots, residuals, multiplicity bins | `.agents/skills/matplotlib/` |
| **astropy** | High | HEP phenomenology overlaps with coordinate/stats tools | `.agents/skills/astropy/` |
| **database-lookup** | High | 78 databases including arXiv, CrossRef, Semantic Scholar | `.agents/skills/database-lookup/` |
| **literature-review** | High | Structured review against Khuntia/Rath baselines | `.agents/skills/literature-review/` |
| **scientific-writing** | Medium | Manuscript polish, referee response drafting | `.agents/skills/scientific-writing/` |
| **peer-review** | Medium | Structured critique before submission | `.agents/skills/peer-review/` |

### Installation Method

```bash
cd /home/ubuntu/aisci

# Install critical skills (batch 1)
npx skills add K-Dense-AI/scientific-agent-skills \
  --skill sympy \
  --skill paper-lookup \
  --skill scientific-visualization \
  --skill statistical-analysis

# Install high-priority skills (batch 2)
npx skills add K-Dense-AI/scientific-agent-skills \
  --skill matplotlib \
  --skill astropy \
  --skill database-lookup \
  --skill literature-review \
  --skill scientific-writing \
  --skill peer-review
```

Skills are installed to `.agents/skills/` and symlinked to Claude Code's skill directory. Each skill includes:
- `SKILL.md` - comprehensive documentation with examples
- Dependencies managed via `uv` package manager
- Security scanned (Cisco AI Defense Skill Scanner)

### Skills NOT Installed

~60% of the 142 K-Dense skills are bio/genomics/clinical/pharma focused and not relevant to HEP phenomenology:
- Bioinformatics (23 skills): BioPython, Scanpy, scRNA-seq pipelines
- Cheminformatics (10 skills): RDKit, drug discovery tools
- Clinical research (8 skills): EHR modeling, clinical decision support
- Medical imaging (3 skills): DICOM, pathology
- Lab automation (6 skills): Opentrons, PyLabRobot

### Security Notes

Per AGENTS.md: "prefer improving shared skills over adding model-specific instruction files"
- K-Dense skills follow same SKILL.md standard as existing `agent-skills/`
- Drop in cleanly with zero friction
- ⚠️ Scan community-contributed skills before using (K-Dense core ones are vetted)
- Security risk assessments: Most skills are "Safe" or "Low Risk", a few "Med Risk" (acceptable for research use)

