# Next Session Kickoff: 2026-07-13

**Objective:** Run the full unblocked `cli.py` suite on the new `ins1735345` data.

**Context:** 
In the previous session, we unblocked the physics core by wiring `fitting_pipeline.py` and `cli.py` to use the correct data file. We also resolved the missing `bose_2c` implementation and provided a symbolic proof for the Jüttner 3-component singularity at $U \to 0$ (D-01).

**Instructions for the Next Agent:**
1. Read `AGENTS.md` and check `docs/ops/CURRENT_STATUS.md`.
2. Run the full physics suite using the CLI:
   `libs/physics-core/.venv/bin/python libs/physics-core/cli.py --run-dir research/robert/runs/2026-07-13-full-suite`
3. Review the outputs (`cli_summary.json` and any anomalies) generated in the run directory.
4. If there are anomalies detected, invoke the `science-hypothesis-generator` skill as directed.
5. Address any resulting next actions in `research/robert/next-actions.md`.
