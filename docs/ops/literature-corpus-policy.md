# Literature Corpus Curation Policy

> Historical record only — not active operational guidance.

How a paper enters the Onyx RAG corpus, how it gets refreshed, how duplicates
are handled, and what to do when a paper is no longer wanted. This is the
canonical procedure — every literature change should follow it. Drift from
this policy is what produced the Q1/Q2 baseline gap in May 2026.

## Scope

This policy covers the **HEP literature** corpus indexed under Onyx connector
`id=3`, CC pair `id=4`. It does NOT cover:

- The repo's `docs/ops/` and `docs/decisions/` markdown — those are managed
  via the Documentation connector (CC pair `id=6`, see `platform-status.md`).
- The pre-publication manuscript (`research/robert/manuscript/...`) — kept
  in the private `Robert Corpus` doc set, with its own indexing path.
- The pending arXiv API connector (`id=21`) — that follows a different
  intake mechanism (Atom API) and is documented separately.

## Where literature lives on disk

- **PDFs**: `research/literature/<First-author>_<Year>_<arXiv-id>.pdf`
  - Example: `research/literature/Khuntia_2019_1808.02383.pdf`
- **Notes** (optional but recommended): `research/robert/literature-notes/<arXiv-id>.md`
  - One short markdown file per paper: title, authors, citation, what claim
    in `evidence-ledger.md` it grounds.

`research/literature/*.pdf` is `.gitignored` — PDFs do not enter version control.
Notes do, so the repo records *what was added and why* even though the
binary content lives only on disk and inside Onyx.

## Naming convention

```
<FirstAuthor>_<PublishYear>_<arXiv-id>.pdf
```

- `FirstAuthor` is the surname only, no initials.
- `PublishYear` is the year on the arXiv listing or journal entry.
- `arXiv-id` is the full versionless identifier (e.g. `1808.02383`).
- For a paper without an arXiv id, substitute the journal DOI's last
  segment: `Smith_2024_PRD-110-014501.pdf`.

If the same paper would be added under two different filenames (e.g. v1 vs
v2 of an arXiv preprint), keep the latest version, delete the older file
on disk, and remove the older copy from the Onyx connector via the same
helper documented below.

## Adding a paper

Use the canonical helper. It reads `ONYX_API_KEY` from env or
`deployment/onyx/.env` (no hardcoded keys).

```bash
# 1. Place the PDF on disk under research/literature/ with the naming convention.
cp ~/Downloads/1908.04208v2.pdf research/literature/Rath_2020_1908.04208.pdf

# 2. Edit deployment/helper/upload_literature_pdfs.py and add the path to
#    the PDFS list, OR write a one-off script using the same endpoint.
#    The atomic upload endpoint is:
#      POST /api/manage/admin/connector/<id>/files/update
#    which adds files AND triggers re-indexing in a single call.

python3 deployment/helper/upload_literature_pdfs.py
```

The helper prints the indexing trigger response. Indexing typically takes
2–5 minutes for a single PDF. After it finishes, validate with the eval
runner:

```bash
python3 deployment/helper/run_rag_tests.py --persona-id 2 \
    --label post-literature-add
```

A successful add appears as a non-zero `top_documents` count in the
artifact's relevant question record. See
`docs/ops/rag-baselines/README.md` for how to interpret the artifact.

## Refresh cadence

- **No automatic refresh** — these are static research papers, not live
  documents. Connector refresh is unnecessary and would only waste embed
  budget.
- **Re-upload** when a published version replaces a preprint, or when a
  major errata revises a number we cite from the paper.
- **Periodic audit** (~quarterly): walk `research/literature/` and confirm every
  PDF is referenced by at least one note in
  `research/robert/literature-notes/`. Orphan PDFs are candidates for
  removal.

## Deduplication

Onyx does not enforce uniqueness on uploaded PDFs, so two uploads of the
same file produce two indexed copies and bias retrieval. To prevent that:

1. Filename match is the dedup key. Always upload via
   `upload_literature_pdfs.py` so the basename ends up in the connector
   verbatim.
2. Before adding a paper, grep `research/literature/` for the arXiv id:

   ```bash
   ls research/literature/ | grep 1808.02383
   ```

3. If the file is already there, do not re-upload. If you need to refresh
   it, *replace then update* — pass the existing file's `file_id` in
   `file_ids_to_remove` on the same `files/update` call so the old copy
   is dropped atomically.

## Removal

To drop a paper from the corpus:

1. Get its `file_id` from `/api/manage/admin/connector/3` (the
   `connector_specific_config.file_locations` array also lists the disk
   paths).
2. Call `POST /api/manage/admin/connector/3/files/update` with
   `file_ids_to_remove=[<id>]` and no new files. Re-index runs
   automatically.
3. Delete the local PDF: `rm research/literature/<file>.pdf`.
4. If the paper had a note in `research/robert/literature-notes/`, delete
   the note too (or move it to `research/robert/literature-notes/archive/`
   if you want to preserve the rationale for why it was once cited).

## When to write a note

Always, when:

- The paper is the source of a number, formula, or claim that ends up in
  `research/robert/evidence-ledger.md`.
- The paper was added because Robert asked for it specifically.

Optional, when:

- The paper is general background that informs prompts but isn't cited.
  Add a note anyway if you'd like a future reviewer to know *why* it's in
  the corpus.

A note doesn't have to be long — title, authors, short paragraph on what
it grounds, and which evidence-ledger row it supports.

## Anti-patterns to avoid

- ❌ Dragging PDFs into the Onyx admin UI by hand. Bypasses the script,
  loses the audit trail, breaks dedup.
- ❌ Hardcoding `ONYX_API_KEY` in helper scripts. Use the env-or-`.env`
  loader pattern from `upload_literature_pdfs.py`.
- ❌ Re-uploading a paper "to refresh" without using
  `file_ids_to_remove` — produces duplicates, contaminates retrieval.
- ❌ Keeping orphan PDFs in `research/literature/` that aren't in the connector.
  Either upload them or delete them.

## Related

- `docs/ops/rag-evaluation-set.md` — questions that depend on the literature
  corpus being correctly populated (Q1, Q2 in particular).
- `docs/ops/rag-baselines/` — JSON artifacts that should be re-run after
  every literature add/remove and labelled accordingly.
- `deployment/helper/upload_literature_pdfs.py` — the canonical intake
  helper.
