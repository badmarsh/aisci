# K-Dense Skills Quick Reference

**Location:** `/home/ubuntu/aisci/.agents/skills/`  
**Repository:** https://github.com/k-dense-ai/scientific-agent-skills  
**Installed:** 2026-05-31

## Installed Skills

### Critical (4)

1. **sympy** - Symbolic mathematics
   - Exact symbolic math, algebra, calculus, equation solving
   - Code generation via lambdify/LaTeX
   - Use when: Need exact results (not floating-point approximations)

2. **paper-lookup** - Academic paper search
   - 10 databases: PubMed, arXiv, bioRxiv, OpenAlex, Semantic Scholar, etc.
   - DOI/PMID lookups, abstracts, full text, citation graphs
   - Use when: Searching for papers, literature queries

3. **scientific-visualization** - Publication-quality figures
   - Multi-panel layouts, significance annotations, error bars
   - Colorblind-safe palettes, journal formatting (Nature, Science, Cell)
   - Use when: Creating journal submission figures

4. **statistical-analysis** - Guided statistical analysis
   - Test selection, assumption checking, power analysis
   - APA-formatted results, chi²/ndf, AIC/BIC
   - Use when: Need help choosing appropriate statistical tests

### High Priority (6)

5. **matplotlib** - Low-level plotting
   - Full customization control, novel plot types
   - Export to PNG/PDF/SVG
   - Use when: Need fine-grained control over plots

6. **astropy** - Astronomy/astrophysics toolkit
   - Units/quantities, coordinates, FITS I/O, cosmology
   - HEP phenomenology overlaps with coordinate/stats tools
   - Use when: Astronomical data analysis workflows

7. **database-lookup** - 78 scientific databases
   - Physics (NASA, NIST, SDSS), chemistry (PubChem, ChEMBL)
   - Biology (UniProt, PDB), economics (FRED, World Bank)
   - Use when: Looking up compounds, genes, proteins, economic indicators

8. **literature-review** - Systematic literature reviews
   - Multiple academic databases, meta-analyses
   - Professionally formatted markdown/PDF with verified citations
   - Use when: Conducting systematic reviews, research synthesis

9. **scientific-writing** - Scientific manuscript writing
   - IMRAD structure, citations (APA/AMA/Vancouver)
   - Reporting guidelines (CONSORT/STROBE/PRISMA)
   - Use when: Writing research papers, journal submissions

10. **peer-review** - Structured manuscript review
    - Checklist-based evaluation, methodology assessment
    - Statistical validity, reporting standards compliance
    - Use when: Writing formal peer reviews

## Usage

Skills are automatically discovered by Claude Code. To use a skill:

1. **Automatic:** Mention the task in natural language
   - "Search arXiv for papers on Tsallis distributions" → triggers paper-lookup
   - "Create a publication-quality plot of pT spectra" → triggers scientific-visualization
   - "Solve this equation symbolically" → triggers sympy

2. **Explicit:** Reference the skill by name
   - "Use the statistical-analysis skill to help me choose the right test"
   - "Use paper-lookup to find papers by Khuntia on Tsallis fits"

## Skill Structure

Each skill includes:
- `SKILL.md` - Comprehensive documentation with examples
- Dependencies managed via `uv` package manager
- Security scanned (Cisco AI Defense Skill Scanner)

## Installation Commands

```bash
# View installed skills
cd /home/ubuntu/aisci
npx skills list

# Install additional skills
npx skills add K-Dense-AI/scientific-agent-skills --skill <skill-name>

# List all available skills
npx skills add K-Dense-AI/scientific-agent-skills --list
```

## Integration with AiSci

These skills complement existing `agent-skills/`:
- K-Dense skills: Domain-specific scientific capabilities
- AiSci agent-skills: Project-specific workflows and processes

Both follow the same SKILL.md standard and work seamlessly together.

## Security

- All installed skills are from K-Dense core (vetted)
- Security risk: Most "Safe" or "Low Risk", some "Med Risk" (acceptable)
- Review `SKILL.md` before first use
- Skills run with full agent permissions

## Next Steps

1. Test critical skills with real AiSci tasks
2. Evaluate additional skills as needs arise (132 more available)
3. Consider contributing AiSci-specific skills back to K-Dense
