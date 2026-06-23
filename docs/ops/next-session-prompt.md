# Next Session Prompt

_Last updated: 2026-05-17_

Two prompts are maintained here: one for **platform/ops** work, one for **science workflow** work. Use whichever matches your session goal.

---

## Prompt A — Platform / Ops (unchanged from 2026-05-06)

Use this prompt to continue the AiSci platform repair work in a fresh coding
agent session.

```text
You are continuing the AiSci Onyx/DeerFlow platform repair.
Repo: /home/ubuntu/aisci, GitHub: badmarsh/aisci.

Read first:
- AGENTS.md
- agent-skills/git-worktree-guard/SKILL.md
- agent-skills/aisci-ops-auditor/SKILL.md
- agent-skills/secret-config-auditor/SKILL.md if touching env/config
- docs/ops/platform-status.md
- docs/ops/onyx-configure.md
- docs/ops/mcp-endpoints.md
- docs/ops/deployment-reference.md

Current known-good state from 2026-05-06:
- Onyx health endpoint returned 200.
- Redis AOF was verified with `aof_enabled:1`.
- alembic head is `14162713706c`.
- `search_settings.multilingual_expansion` exists again as `varchar[] not null
  default '{}'` because the recreated `craft-latest` background image expects
  it during `check_for_indexing`.
- Active embedding is `Alibaba-NLP/gte-Qwen2-1.5B-instruct`, 1536 dims,
  search_settings id 10.
- `deployment/helper/sitecustomize.py` is required for Transformers 5 / Qwen2.
- `deployment/onyx/.env` is tracked and secret-free; `.env.local` is ignored.
- Craft should remain enabled: `ENABLE_CRAFT=true`, `IMAGE_TAG=craft-latest`.
- Onyx MCP host route is `http://127.0.0.1:8095/...`.
- DeerFlow container route is `http://onyx-mcp-proxy:80/...`.
- Onyx MCP submodule URL is `https://github.com/badmarsh/onyx-mcp-server.git`;
  do not point the parent repo at an unreachable local submodule commit.
- GitHub Issues are now the active work layer; canonical docs stay in repo.
  Start with issues #4 (key rotation), #5 (Onyx docs connector monitoring),
  and #6 (docs/backlog migration).
- Onyx Documentation connector is CC pair 11 / connector 15. Its
  `refresh_freq` was reduced to 86400 seconds on 2026-05-06.
- LiteLLM has RAG routes `qwen-rag-fast`, `qwen-rag-balanced`,
  `qwen-rag-vision`, and local fallback `qwen-rag-local`. Probe with
  `deployment/helper/litellm_quota_check.py --timeout 90`.

Hard constraints:
- Do not restart `onyx-db`.
- Do not print secrets or modify `.env.local` unless explicitly asked.
- Do not change embedding dimensions or switch active search_settings id 10.
- Keep platform details out of science files.
- Preserve unrelated user changes.

Next highest-value work:
1. Rotate provider/tool API keys listed in issue #4 and the 2026-05-06
   secret-history audits, then update only ignored private env/config. Do not
   commit key values.
2. Monitor the next Onyx Documentation connector run from issue #5. Confirm it
   does not retry every 30 minutes, does not hit heartbeat timeout, and does not
   produce repeated DashScope 429s.
3. Start issue #6 by migrating only active open backlog rows to GitHub Issues,
   then shrink `docs/ops/platform-status.md` instead of adding new reports.
4. Fix the `onyx-mcp-server` full Jest failures around `send-chat-message`
   nock expectations, then remove the need for `--no-verify` pushes.
5. Rebuild `onyx-python-webdeps:3.11` reproducibly once Docker buildx and PyPI
   DNS are healthy.
6. Verify real DeerFlow MCP tool calls after the `extensions_config.json` route
   update. The gateway was restarted on 2026-05-06 and basic connectivity to
   `onyx-mcp-proxy:80` passed, but an authenticated end-to-end tool call should
   still be exercised.
7. Add monitoring for `onyx-background` errors, Redis queue depth, and Alembic
   version drift.
8. Decide whether OpenSearch retrieval is worth the memory cost or whether a
   measured Vespa-only fallback should reclaim RAM.

Before closing:
- Run `git status -sb`.
- Run `docker compose config --quiet` from `deployment/onyx`.
- Check `curl -fsS http://127.0.0.1:3000/api/health`.
- Report what was changed, what was pushed, and any remaining test gaps.
```

---

## Prompt B — Science Workflow: Post-PhD-Fit Analysis & Decisions

Use this prompt to continue the AiSci physics research workflow in a fresh local agent session. The PhD-level fits have completed. This session pushes toward physical interpretation and manuscript decisions.

```text
You are continuing the AiSci physics research workflow as a PhD-level High Energy Physicist.
Repo: /home/ubuntu/aisci, GitHub: badmarsh/aisci.

Read first (in this order):
- AGENTS.md
- research/robert/next-actions.md       ← canonical science task queue
- research/robert/evidence-ledger.md    ← canonical claim-status file
- research/robert/science-questions.md  ← core physics questions
- physics/README.md

Current state (as of 2026-06-20):
- PhD-level fits COMPLETED. Run dir: research/robert/runs/2026-06-20-phd-level-fits/
- Data: ATLAS 13 TeV pp, HEPData ins1735345, 10 multiplicity bins, pT ∈ [0.15, 3.0] GeV
- Models run: manuscript_juttner, exact_bose_einstein, tsallis (1c, 2c), blast_wave (1c)
- Test suite: 305/307 pass (1 pre-existing antlr4 skip, 1 pre-existing antlr4 test failure)
- Virtual environment: physics/physics_env

Key findings requiring Robert's decisions before further analysis:
1. [O-04] T-β degeneracy: |ρ(T, β_s)| = 0.93–0.999 in ALL BGBW bins (4/9 degenerate, 5/9 borderline).
   No bin allows independent physical interpretation of T_kin and β_s.
2. [O-05] Jacobian missing: dy/dη = 0.782 at pT=0.175 GeV (22% correction). If ATLAS data is dN/dpT dη,
   this is a mandatory referee correction. HEPData ins1735345 header check required.
3. [O-06] Tsallis 2c wins AIC/BIC in 7/10 bins (chi²/ndf < 2). Physical interpretation needed.
4. [O-07] Manuscript uses Boltzmann exponential, not Bose-Einstein denominator. Title says "bosons"
   = particle species, not quantum statistics. Robert must confirm if this is intentional.

Chi²/ndf summary (from runs/2026-06-20-phd-level-fits/fit_quality.csv):
- Tsallis 2c: chi²/ndf ∈ [0.36, 2.05] — acceptable in 7/10 bins
- Tsallis 1c: chi²/ndf ∈ [0.59, 19.6] — acceptable in 1/10 bins (21-30 only)
- blast_wave 1c: chi²/ndf ∈ [5.3, 29.8] — 0/10 acceptable
- manuscript_juttner 1c: chi²/ndf ∈ [67, 218] — 0/10 acceptable
- exact_bose_einstein 1c: chi²/ndf ∈ [64, 194] — 0/10 acceptable

Your tasks this session:
1. [O-05 — can be done now] Check HEPData ins1735345 table headers/qualifiers to determine if the
   observable is dN/dpT dη or dN/dpT dy. Run:
   curl -s "https://www.hepdata.net/record/ins1735345?format=json" | python3 -c "import sys,json; d=json.load(sys.stdin); [print(t['name'], t.get('qualifiers',{})) for t in d.get('data_tables',[])]"
   If the qualifier key is "ETARAP" → pseudorapidity → Jacobian required. Create a Multica Issue.

2. [O-06 — do now] Extract Tsallis 2c parameters from fit_parameters.csv for all bins where
   tsallis 2c succeeded (7 bins). Check: (a) are T₁, T₂ physically stable across multiplicity?
   (b) are q₁, q₂ in expected range 1.0–1.2? (c) what is |ρ(T,q)| from parameter_correlations.csv?
   Compare with Cleymans-Worku 2012 (arXiv:1110.5526) which finds T ~ 0.09–0.10 GeV, q ~ 1.1.

3. [O-04 + O-07] Summarize the T-β degeneracy and the BE vs Boltzmann finding for Robert clearly,
   so Robert can make an informed decision. Do NOT make the decision yourself.

4. Update evidence-ledger.md and next-actions.md with your findings.
   Do NOT create a new markdown report — write only the minimum necessary evidence updates.

Hard constraints:
- Treat all numerical results critically. Chi²/ndf alone is not sufficient; check covariance.
- Be explicit about Bose-Einstein vs Boltzmann/Juttner wording.
- Never write physics conclusions in docs/ops/ (keep them in research/robert/).
- Do not add new Multica Issues for O-04 or O-07 until Robert has made the decision.
- Only add a Multica Issue for O-05 if the check confirms the data is dN/dpT dη.

Before closing:
- Run cd physics && pytest and ensure tests pass (expect 1 antlr4 test failure = pre-existing).
- Run git status -sb and commit only the changes you produced.
- Summarize the physics outcomes clearly to the user.
- Update this Prompt B with the new current state.
```
