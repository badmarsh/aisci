# Literature Cross-Check: Is the dy/dη Jacobian correct in our Tsallis fix?

## The single question to answer

> **"When the Cleymans & Worku Tsallis formula (arXiv:1110.5526 eq.1, defined in rapidity y)
> is integrated over a detector pseudorapidity acceptance η ∈ [−η_max, η_max],
> is the dy/dη Jacobian correction required, and if so, at what pT scale does it matter?"**

This is what AIS-60 fixed in `libs/physics-core/src/fitting_pipeline.py`. Use 5 APIs to
cross-check whether the fix was correct. Write the verdict and one evidence-ledger row.

---

## API reference (all proxied through nginx, see `docs/ops/`)

| API | Proxy (host) | Auth | Rate limit | What it's good for |
|---|---|---|---|---|
| **arXiv** | Direct: `https://export.arxiv.org/api/query` | None | ~3s between | Full PDF of primary source |
| **Semantic Scholar** | `http://127.0.0.1:8095/semanticscholar/graph/v1` | `x-api-key: $SEMANTICSCHOLAR_API_KEY` | 1 req/s | Citation count, who cites this paper |
| **Asta** | `http://127.0.0.1:8095/asta/` | `x-api-key: $ASTA_API_KEY` | 1 req/s | Full-text snippet search inside paper bodies |
| **Scite** | `http://127.0.0.1:8095/scite/` | OAuth Bearer (MCP flow) | — | Smart citations: supporting / contrasting / mentioning |
| **Consensus** | `http://127.0.0.1:8095/consensus/` | OAuth Bearer (MCP flow) | — | AI synthesis of research consensus on a question |

---

## Step 1 — arXiv: get the actual formula (2 min)

Use the arXiv skill at `C:\Users\marek\.gemini\config\plugins\science\skills\literature_search_arxiv\SKILL.md`.

```bash
cd /mnt/c/Users/marek/.gemini/config/plugins/agent-skills/literature_search_arxiv
uv run scripts/download_paper.py --id 1110.5526 --format pdf --output /tmp/cleymans.pdf
pdftotext /tmp/cleymans.pdf - | grep -A 5 "eq.*1\|equation.*1\|dN.*dpT\|dN.*dy" | head -40
```

**Record:**
- [ ] Is eq.(1) in rapidity `y` or pseudorapidity `η`? (Expected: `y`)
- [ ] Does the paper mention integrating over a pseudorapidity acceptance? (Expected: no — it works in y-space)

---

## Step 2 — Semantic Scholar: who cites it and what do they say (3 min)

```python
import requests, time, os

HEADERS = {"x-api-key": os.environ["SEMANTICSCHOLAR_API_KEY"]}
BASE = "http://127.0.0.1:8095/semanticscholar/graph/v1"  # via proxy
# OR direct: BASE = "https://api.semanticscholar.org/graph/v1"

# Get paper metadata
r = requests.get(f"{BASE}/paper/ARXIV:1110.5526",
    params={"fields": "paperId,citationCount,tldr,year"}, headers=HEADERS)
meta = r.json()
print(f"Citations: {meta['citationCount']}, TLDR: {meta.get('tldr',{}).get('text','')}")
time.sleep(1)

# Get papers that cite Cleymans — check which mention pseudorapidity/Jacobian
r = requests.get(f"{BASE}/paper/{meta['paperId']}/citations",
    params={"fields": "title,year,abstract,citationCount,externalIds", "limit": 50},
    headers=HEADERS)
cites = r.json()["data"]
time.sleep(1)

hits = [c["citingPaper"] for c in cites
        if any(kw in (c["citingPaper"].get("abstract") or "").lower()
               for kw in ["pseudorapidity", "jacobian", "dy/d", "eta_max", "rapidity acceptance"])]
for h in hits[:5]:
    print(h["year"], h["title"], h.get("externalIds", {}))
```

**Record:**
- [ ] Total citations
- [ ] How many mentioning pseudorapidity/Jacobian
- [ ] Titles of relevant papers (to follow up with Asta)

---

## Step 3 — Asta: full-text snippet search (2 min)

Asta searches *inside* paper bodies — abstracts miss a lot of method detail.

```python
ASTA_HEADERS = {"x-api-key": os.environ["ASTA_API_KEY"], "Content-Type": "application/json"}
ASTA_URL = "http://127.0.0.1:8095/asta/"  # via proxy
# OR direct: "https://asta-tools.allen.ai/mcp/v1"

r = requests.post(ASTA_URL, headers=ASTA_HEADERS, json={
    "tool": "search_snippets",
    "params": {
        "query": "Tsallis pseudorapidity rapidity Jacobian dy deta correction pion ALICE",
        "limit": 5
    }
})
snippets = r.json()
time.sleep(1)

for s in snippets.get("snippets", []):
    print("---")
    print(s.get("title"), s.get("year"), s.get("arxivId") or s.get("doi"))
    print(s.get("text", "")[:300])
```

**Record for each snippet:**
- [ ] Paper title and year
- [ ] Does the passage apply the Jacobian? Does it argue against it?

---

## Step 4 — Scite: supporting vs contrasting citations (2 min)

Scite classifies each citation as **supporting**, **contrasting**, or **mentioning**.
This tells us if anyone has disputed the Cleymans formula.

Connect via the MCP client to: `http://127.0.0.1:8095/scite/`
(Requires OAuth Bearer token from the Scite browser flow.)

Ask the Scite MCP tool:
```
Search for smart citations to: arXiv:1110.5526
Focus on: contrasting citations (papers that dispute or modify the formula)
```

**Record:**
- [ ] Any contrasting citations found?
- [ ] If yes, what do they dispute?

---

## Step 5 — Consensus: synthesized answer (1 min)

Connect via the MCP client to: `http://127.0.0.1:8095/consensus/`
(Requires OAuth Bearer token from the Consensus browser flow.)

Ask:
```
In heavy-ion physics, when fitting Tsallis distributions to ALICE pion spectra,
is the dy/dη Jacobian correction needed when integrating over pseudorapidity acceptance?
At what transverse momentum pT does the correction become negligible?
```

**Record:**
- [ ] What does Consensus return?
- [ ] Does it cite specific papers?

---

## Step 6 — Write verdict + update evidence ledger (5 min)

Fill in this template and add it as one line to `research/robert/evidence-ledger.md`:

```
VERDICT (AIS-60 validation — 2026-06-03):
Cleymans & Worku (arXiv:1110.5526) eq.(1) is in rapidity y [confirmed: arXiv PDF].
[N] papers cite it; [M] mention pseudorapidity integration; [K] apply explicit Jacobian.
Asta snippets: [summary]. Scite: [N contrasting / N supporting]. Consensus: [one sentence].
CONCLUSION: AIS-60 Jacobian fix is [confirmed/disputed]. y≈η breaks down below pT~[X] GeV.
```

Do NOT create a new markdown file. One row in the ledger is sufficient.

```bash
git add research/robert/evidence-ledger.md
git commit -m "evidence: AIS-60 Jacobian validated via arXiv + S2 + Asta + Scite + Consensus"
```

---

## Constraints

- 1 req/s on Semantic Scholar and Asta — always `time.sleep(1)` between calls
- Scite and Consensus need OAuth Bearer from their browser MCP flow
- Semantic Scholar: `/graph/v1/` only (Academic Graph) — not Recommendations or Datasets
- If any source disputes the Jacobian, record as counterevidence — do not ignore
- Do NOT create new markdown reports; update `evidence-ledger.md` with one row only
