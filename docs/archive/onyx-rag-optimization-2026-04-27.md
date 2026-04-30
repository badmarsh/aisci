# Onyx RAG Optimization Audit - 2026-04-27

Platform note for the local Onyx deployment in `deployment/onyx`. This is an operations/RAG configuration audit only. It does not promote or modify any science claims.

## Executive Findings

- The Onyx stack is running and non-destructive health checks pass for the API, OpenSearch, Postgres, Redis, MinIO, model servers, and Unstructured.
- OpenSearch indexing is enabled and contains the active Nomic 768-dimensional indexes, but the live tenant migration record currently has `enable_opensearch_retrieval=false`; the RAG-16 through RAG-18 retrieval run below used Vespa despite OpenSearch retrieval env flags being set.
- The Onyx API/background containers expect `nomic-ai/nomic-embed-text-v1` with 768 dimensions, but the running model-server processes still expose environment values for `sentence-transformers/all-MiniLM-L6-v2` and 384 dimensions. This mismatch must be fixed before any quality tuning.
- The model-server containers have no NVIDIA device access even though the host has an RTX 3090. Docker `deploy.resources.reservations.devices` is not providing GPU devices in this local Compose run.
- The LiteLLM proxy is up, but all configured endpoints are unhealthy: Ollama has no local models, OpenRouter calls returned authorization failures, the DashScope/Qwen endpoint reported exhausted free tier, and one Hugging Face embedding route is configured through Ollama incorrectly.
- The local Unstructured API works at both `localhost:9560` and internal Docker DNS `http://unstructured:8000`, but the running Onyx code path appears not to pass `UNSTRUCTURED_API_URL` into `UnstructuredClient`. It also gates the SDK call on a KV-stored Unstructured API key that is absent. As configured today, local Unstructured is likely present but not actually used by Onyx ingestion.
- `Physics Validation Mode` has since been aligned as the primary science persona with local physics document sets plus science/literature, HEP-native lookup, and analysis tools attached. `Science Deep-Dive Mode` now has matching local-plus-external source curation guardrails.

## Applied Persona Alignment

Applied on 2026-04-27 through non-destructive Postgres metadata updates. No containers were restarted, no connectors were reset, no reindex was started, and no credentials were read or changed.

- `Physics Validation Mode` prompt now encodes the AiSci evidence-ledger rules, Bose-Einstein versus Boltzmann/Juttner wording guard, no-causality-from-suggestive-fits guard, and fit-quality/baseline gates.
- `Physics Validation Mode` now has `Physics`, `Robert Boson Draft`, and `HEP Phenomenology References` document sets attached.
- `Physics Validation Mode` now has internal search, file reader, code interpreter/Python, URL opening, Scite, Consensus, arXiv, INSPIRE-HEP, and HEPData tools attached.
- `Science Deep-Dive Mode` prompt now treats the persona as source curation rather than final claim promotion, and its user-specific internal-search disable was removed.
- `Science Deep-Dive Mode` now has internal search, file reader, URL opening, Scite, Consensus, and the same local physics document sets attached.
- `Draft Review Mode`, `Validation Orchestrator Mode`, and `Literature Deep-Dive Mode` were unlisted because their descriptions did not match their empty tool/document-set attachments.
- `AiSci Wiki Agent` prompt now states that Outline is not the canonical project record and should not replace `research/robert/evidence-ledger.md`, `research/robert/next-actions.md`, `docs/ops/platform-backlog.md`, or `docs/decisions/`.
- Broad Outline/Wiki write tools were removed from the default `Assistant`; the dedicated `AiSci Wiki Agent` remains the write-capable wiki persona.

Remaining persona/source gaps:

- arXiv, INSPIRE-HEP, and HEPData read-only custom OpenAPI tools are present in live Onyx and attached to `Physics Validation Mode`; OpenAlex remains a fallback candidate, and Semantic Scholar remains disabled/best-effort until unauthenticated rate-limit behavior is solved.
- `HEP Phenomenology References` now includes the original `Tsallis_statistics` connector plus a small `HEP Native API Sources` ingestion seed for the ATLAS 13 TeV arXiv/INSPIRE/HEPData record. It still needs literature-matched Tsallis/Tsallis-Pareto and Blast-Wave sources before model-quality claims.
- A draft retrieval evaluation set now exists below. RAG-16 through RAG-18 have a recorded retrieval-only baseline; do not tune embeddings, rerank settings, contextual RAG, parsers, or production document-set coverage until the remaining set has a recorded baseline run or explicit approval.

## HEP-Native Read-Only Integration Plan

Scope: plan source-grounding integrations only. No credentials were added, no MCP servers were installed, no Onyx config was changed, and no containers were restarted. The immediate goal is to support RAG-16 through RAG-19 with HEP-native identifiers, data-table metadata, and citation context while keeping Onyx as the curated evidence layer.

### Recommended tool split

| Tool/source | Primary use | Placement | Auth posture | Minimal returned fields |
| --- | --- | --- | --- | --- |
| arXiv API | Resolve arXiv IDs, titles, abstracts, PDF links, categories, DOI hints | Shared local MCP/API proxy; attach read-only action to `Physics Validation Mode` after testing | No key for normal use; respect arXiv rate limits | arXiv ID/version, title, authors/collaboration, abstract, categories, DOI, journal reference, PDF URL |
| INSPIRE-HEP REST API | HEP canonical record lookup, DOI/arXiv/CDS/HEPData cross-links, collaboration metadata | Shared proxy first; optionally direct coding-agent tool for reproducible source curation | No key for public literature lookup | control number, titles, DOI, arXiv eprints, collaboration/experiment, external system identifiers, publication info, citation counts if available |
| HEPData | Dataset/table discovery for spectra, binning, uncertainties, machine-readable table downloads | Shared proxy plus Onyx ingestion workflow for selected records/tables | No key for public records | HEPData DOI/record, INSPIRE ID, table names, descriptions, observables, reaction/energy keywords, JSON/YAML/CSV table URLs |
| OpenAlex | Broad citation and open-access metadata fallback when HEP-native records are incomplete | Direct agent/API fallback; attach to Onyx only after relevance testing | No key required, but identify politely if used heavily | DOI, title, year, source, cited-by count, OA landing/PDF links |
| Semantic Scholar Graph API | Citation/reference counts and external IDs when available | Optional fallback only; not a blocker for HEP workflow | Public endpoint may rate-limit without a key | paper ID, external IDs, title, year, citation/reference counts, URL |

### Endpoint probes from 2026-04-27

These were host-side, read-only probes. They validate endpoint shape, not scientific suitability of a particular source.

- arXiv Atom API worked for `id_list=1602.01633` and returned `Charged-particle distributions in sqrt(s)=13 TeV pp interactions measured with the ATLAS detector at the LHC`, DOI `10.1016/j.physletb.2016.04.050`, and a PDF link.
- INSPIRE-HEP worked for `q=arxiv:1602.01633` and returned control number `1419652`, DOI `10.1016/j.physletb.2016.04.050`, arXiv eprint `1602.01633`, ATLAS experiment metadata, and a HEPData external identifier `ins1419652`.
- HEPData worked for `record/ins1419652?format=json` and returned record `72491`, status `finished`, HEPData DOI `10.17182/hepdata.72491.v1`, and `18` `data_tables` with machine-readable table download URLs.
- OpenAlex worked for a broad ATLAS 13 TeV charged-particle query and returned DOI, title, source, open-access location, and cited-by count fields.
- Semantic Scholar Graph returned HTTP `429` for unauthenticated `paper/search` probes, even with a polite user agent. Treat it as optional unless a key, backoff, and caching policy are approved.

### Implementation shape

1. Add thin read-only clients or MCP tools for arXiv, INSPIRE-HEP, and HEPData first. Keep them stateless and allow query by DOI, arXiv ID, INSPIRE control number, HEPData record, and free text.
2. Normalize each result into a small evidence envelope with `source`, stable identifier, title, URL, retrieved timestamp, and compact metadata. Do not summarize scientific implications inside the tool.
3. Route selected PDFs and HEPData JSON/YAML tables into Onyx only after source curation decides they belong in `HEP Phenomenology References` or a dataset-specific document set.
4. Keep OpenAlex as a fallback for DOI/OA/citation metadata. Do not prefer it over INSPIRE-HEP for HEP canonical records.
5. Leave Semantic Scholar disabled or best-effort until rate-limit behavior is solved without committing keys.
6. After tools exist, run RAG-16 through RAG-19 and record observed citations, misses, latency, and failure modes in the retrieval run sheet before any RAG tuning.

### Approval gates

- Approval required before adding real API keys, installing MCP servers globally, exposing a proxy beyond localhost, changing Onyx persona tool attachments, ingesting new documents into live Onyx, or restarting/reindexing any Onyx service.
- No approval needed for local client code, read-only endpoint probes, unit tests with recorded public fixtures, or docs updates that do not alter live configuration.

## Applied HEP-Native Tool And Source Grounding

Applied on 2026-04-27 after explicit user approval for the three pending Onyx tasks. No containers were restarted, no connectors were reset, no reindex was started, no embeddings were changed, no real keys were added, and no services were exposed beyond localhost.

Implementation artifact:

- Added `deployment/onyx/hep_readonly_tools.py`, a reproducible installer/ingester intended to run inside `onyx-api_server-1`.
- The script validates OpenAPI schemas, verifies public endpoints with a non-secret user agent, installs or updates no-credential read-only tools, attaches them to `Physics Validation Mode`, creates a dedicated ingestion connector, and seeds selected source-grounding documents.

Live Onyx changes:

| Item | Result |
| --- | --- |
| Persona | `Physics Validation Mode` id `7` |
| Tools | `hep_arxiv` id `28`, `hep_inspire` id `29`, `hepdata` id `30`; all enabled, non-MCP custom OpenAPI tools, `passthrough_auth=false` |
| Tool endpoints | `https://export.arxiv.org/api/query`, `https://inspirehep.net/api/literature`, `https://www.hepdata.net/search/`, `https://www.hepdata.net/record/{record_id}?format=json`, `https://www.hepdata.net/download/table/{inspire_id}/{table_name}/json` |
| Connector | `HEP Native API Sources` connector id `11`, source `INGESTION_API`, input type `LOAD_STATE` |
| Connector credential pair | `HEP Native API Sources` cc-pair id `7`, status `ACTIVE`, access type `PUBLIC` |
| Document set attachment | `HEP Phenomenology References` id `6` now includes cc-pairs `3` and `7` |

Seeded documents in cc-pair `7`:

| Document id | Purpose | Indexed chunks |
| --- | --- | --- |
| `hep-native-arxiv-1602-01633-inspire` | arXiv/INSPIRE metadata for the ATLAS 13 TeV charged-particle source | `3` |
| `hepdata-ins1419652-table-index` | HEPData `ins1419652` table index and record metadata | `5` |
| `hepdata-ins1419652-selected-pt-multiplicity-tables` | Selected pT, multiplicity, and average-pT source-grounding text for tables 4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17, and 18 | `120` |

Verification:

- `python -m py_compile deployment/onyx/hep_readonly_tools.py` passed.
- Postgres metadata confirms all three tools are enabled and attached to `Physics Validation Mode`.
- Postgres metadata confirms connector id `11`/cc-pair id `7` is attached to `HEP Phenomenology References`.
- Postgres metadata confirms the three seeded documents are `from_ingestion_api=true`, `hidden=false`, and `has_been_indexed=true`.
- Retrieval probe query `"Uncertainty labels present in rows"` returned selected-table chunks such as Table 6 chunk `22` and Table 14 chunk `71`, confirming that the active index exposes row-level HEPData binning and stat/sys text rather than only raw JSON-shaped content.

Observed failure/noise mode:

- During ingestion, OpenSearch alt-index writes emitted non-fatal `version_conflict_engine_exception`/`BulkIndexError` logs and then retried individual docs. The script completed successfully and DB metadata shows indexed documents, but this should be treated as indexing noise to monitor during the RAG-16 through RAG-18 evaluation run.

Remaining approval-gated work:

- Run the remaining retrieval evaluation questions, especially RAG-01 through RAG-15 and RAG-19 through RAG-25, before any RAG tuning.
- Ingest literature-matched Tsallis/Tsallis-Pareto and Blast-Wave baseline sources into `HEP Phenomenology References` only after source curation.
- Add Robert's fitting table or an explicitly matched HEPData selection if the workflow needs proof that every manuscript fitting multiplicity bin maps to a source-grounded pT table.

## RAG-16 Through RAG-18 Retrieval Evaluation - 2026-04-27

Run scope:

- Executed RAG-16 through RAG-18 from inside `onyx-api_server-1` through Onyx's EE `stream_search_query` path, scoped to the three document sets attached to `Physics Validation Mode`: `Physics`, `Robert Boson Draft`, and `HEP Phenomenology References`.
- Used `anonymous@onyx.app`, `num_hits=8`, `include_content=true`, `run_query_expansion=false`, and no LLM document selection. This avoided the unhealthy chat/LLM layer and kept the run retrieval-only.
- No containers were restarted, no connector was reset, no reindex was run, no embeddings were changed, no credentials were added or printed, and no services were exposed beyond localhost.
- Unauthenticated host API probing of `POST /api/search/send-search-message` returned `403`, so this is an in-container retrieval baseline rather than a browser/session chat transcript.
- `ENABLE_OPENSEARCH_RETRIEVAL_FOR_ONYX=true` is set in the API container, but `opensearch_tenant_migration_record.enable_opensearch_retrieval=false`; the run logs selected Vespa profile `hybrid_search_keyword_base_768`. No state was changed.

Run sheet:

| ID | Persona/document set | Observed cited source | Observed chunk/page | Answer status | Latency | Failure mode | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RAG-16 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | `hep-native-arxiv-1602-01633-inspire`; `hepdata-ins1419652-table-index` | arXiv/INSPIRE chunk `0`; HEPData table-index chunk `0` | Pass for identifier/source lookup from seeded records | `1.252s` | None for retrieval | Top result cites arXiv `1602.01633v2`, DOI `10.1016/j.physletb.2016.04.050`, `ATLAS Collaboration`, INSPIRE control number `1419652`, HEPData external id `ins1419652`, and Phys. Lett. B publication metadata. |
| RAG-17 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | `hepdata-ins1419652-selected-pt-multiplicity-tables`; `hepdata-ins1419652-table-index`; `hep-native-arxiv-1602-01633-inspire` | selected-tables chunk `0`; table-index chunk `0`; arXiv/INSPIRE chunk `0` | Partial | `0.144s` | HEPData JSON row rendering is weak | Retrieval locates record `ins1419652`, HEPData DOI `10.17182/hepdata.72491.v1`, table count `18`, and table descriptions/JSON URLs. It identifies pT spectra tables such as Table 4 and Table 12 from the index, but the JSON-backed selected-table chunk does not expose usable row-level binning or uncertainty text. |
| RAG-18 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | `hepdata-ins1419652-selected-pt-multiplicity-tables`; Robert boson draft PDF; `hep-native-arxiv-1602-01633-inspire` | selected-tables chunks `0` and `7`; manuscript PDF chunk `5`; arXiv/INSPIRE chunk `0` | Partial/coverage gap | `0.122s` | The indexed HEPData table content cannot substantiate full pT uncertainties for every fitting multiplicity bin | Retrieval supports the conservative answer that indexed sources do not yet demonstrate a full source-to-pipeline table mapping. Direct read-only HEPData checks show tables such as 4, 8, 12, and 16 have `values` rows with `stat` and `sys` errors, but the current Onyx `TabularSection` rendering reports selected JSON chunks as `0 rows and 425 columns`. |

Source-grounding assessment:

- The arXiv/INSPIRE seed materially improved RAG-16. The top retrieved Onyx chunk now contains enough canonical identifier metadata to answer without relying on manuscript references alone.
- The HEPData seed materially improved dataset discovery for RAG-17 by surfacing `ins1419652`, table descriptions, DOIs, and JSON URLs inside `HEP Phenomenology References`.
- The HEPData JSON-backed chunks do not yet materially improve row-level table answers. They rank highly, but Onyx does not render HEPData's `values` arrays into readable bins and uncertainties. For RAG-18 this prevents a clean cited answer about full pT uncertainty coverage for every fitting bin.
- This run did not measure agentic custom-tool invocation by `Physics Validation Mode`; it measured Onyx retrieval over the source-grounding documents seeded by the HEP-native tooling. A persona chat/tool run should wait until the local chat model/session path is healthy enough to avoid confounding retrieval quality with LLM endpoint failures.

## HEPData Text-Section Follow-up - 2026-04-27

Change applied:

- `deployment/onyx/hep_readonly_tools.py` now renders the selected HEPData tables as source-grounding `TextSection` content instead of raw JSON-shaped table dumps. Each table chunk includes kind, DOI, description, headers, qualifiers, row count, first/last bins, uncertainty labels, and explicit row-level values/errors.
- The existing seeded HEP native documents were refreshed in place through the read-only installer path inside `onyx-api_server-1` with `--verify-tools --ingest`. No containers were restarted, no connector was reset, no reindex was run, no embeddings were changed, and no services were exposed beyond localhost.
- Retrieval remained on Vespa because `opensearch_tenant_migration_record.enable_opensearch_retrieval=false`; the follow-up again logged `hybrid_search_keyword_base_768`.

Follow-up run sheet:

| ID | Persona/document set | Observed cited source | Observed chunk/page | Answer status | Latency | Failure mode | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RAG-17 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | `hepdata-ins1419652-selected-pt-multiplicity-tables`; `hep-native-arxiv-1602-01633-inspire` | selected-tables chunks `3`, `0`, `31`, and `58`; arXiv/INSPIRE chunk `0` | Pass | `0.710s` | None for retrieval | Top chunks now identify HEPData record `ins1419652` and pT-spectrum tables `4`, `8`, `12`, and `16`, with qualifiers, observable/header names, first/last pT bins, and explicit `stat`/`sys` uncertainty labels. The mapping chunk still states that a source-to-pipeline match for every manuscript multiplicity bin is not established by these selected tables alone. |
| RAG-18 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | `hepdata-ins1419652-selected-pt-multiplicity-tables` | selected-tables chunks `3`, `0`, and `83` | Pass for conservative availability answer | `0.111s` | None for retrieval | The top chunk now directly supports the conservative answer: the selected HEPData pT tables provide inclusive spectra with row-level `stat`/`sys` uncertainties, but the indexed sources still do not establish a pT-spectrum split for every manuscript fitting multiplicity bin. |

Follow-up assessment:

- The HEPData rendering change removed the earlier `TabularSection` failure mode. Retrieval now surfaces citeable row-level bins and uncertainties from the seeded HEPData tables.
- RAG-17 now passes as a dataset-lookup question because the retrieved chunks expose table name, record identifier, observable, binning, and uncertainty labels in the indexed content.
- RAG-18 now passes as a conservative data-availability question because the retrieved mapping chunk states both what the selected HEPData tables do provide and the remaining source-to-pipeline gap.
- Remaining gap: Robert's fitting table or an explicitly matched HEPData selection is still required to prove a full manuscript-bin mapping for the fitting pipeline.

## RAG-01 Through RAG-15 And RAG-19 Through RAG-25 Retrieval Evaluation - 2026-04-27

Run scope:

- Executed the remaining retrieval questions from inside `onyx-api_server-1` through the same EE `stream_search_query` path used above, again scoped to `Physics`, `Robert Boson Draft`, and `HEP Phenomenology References`.
- Used `anonymous@onyx.app`, `num_hits=8`, `include_content=true`, `run_query_expansion=false`, and no LLM document selection. This kept the run retrieval-only and comparable to the RAG-16 through RAG-18 baseline.
- No containers were restarted, no connector was reset, no reindex was run, no embeddings were changed, no credentials were added or printed, and no services were exposed beyond localhost.
- Retrieval again logged Vespa profile `hybrid_search_keyword_base_768` because `opensearch_tenant_migration_record.enable_opensearch_retrieval=false`.

Run sheet:

| ID | Persona/document set | Observed cited source | Observed chunk/page | Answer status | Latency | Failure mode | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RAG-01 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | `hepdata-ins1419652-selected-pt-multiplicity-tables`; `Tsallis statistics - Wikipedia` | selected-tables chunks `3` and `0`; Wikipedia chunk `1` | Fail | `0.469s` | Manuscript formula was not retrieved from the scoped sets | Results drifted to HEPData pT tables and a generic Tsallis page; no Robert manuscript chunk surfaced in the top retrieved set. |
| RAG-02 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | Robert boson draft PDF; `Tsallis statistics - Wikipedia` | manuscript PDF chunk `1`; Wikipedia chunk `0` | Partial | `0.105s` | Relevant manuscript chunk ranked below generic Tsallis noise | The manuscript chunk does ground the definition `U^μ = γ(1, \vec{U})` and `\vec{U} = \vec{P}/E`, but it was not the top-ranked hit. |
| RAG-03 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | Robert boson draft PDF; `hepdata-ins1419652-selected-pt-multiplicity-tables` | manuscript PDF chunks `5` and `11`; selected-tables chunk `3` | Partial | `0.125s` | Acceptance cuts and fit setup were not isolated into one clean manuscript chunk | The retrieval set mixes the manuscript cut-study figures with HEPData qualifiers (`PT(P=3) > 500 MeV`, `|eta| < 2.5` and `< 0.8`) and the manuscript fit-range excerpt. |
| RAG-04 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | Robert boson draft PDF | manuscript PDF chunk `11` (Table 1 / p. 10 excerpt); chunk `9` (Figure 7 / p. 7 excerpt) | Pass | `0.131s` | None for retrieval | The retrieved manuscript chunks expose the fitted multiplicity bins and the reported fit parameters (`U1`, `kT1`, `U2`, `kT2`, `kT3`; figure panels also show `A1`-`A3` and `chi2/ndf`). |
| RAG-05 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | Robert boson draft PDF; `hepdata-ins1419652-selected-pt-multiplicity-tables` | manuscript PDF chunks `9` and `11`; selected-tables chunk `3` | Partial | `0.118s` | Retrieval shows `chi2/ndf` examples but not a complete fit-quality audit, and the evidence-ledger fallback is out of scope | Figure chunks expose `chi2/ndf` such as `5555 / 480`, but no retrieved chunk establishes covariance matrices, parameter correlations, residuals, or fit-range sensitivity for every bin. |
| RAG-06 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | Robert boson draft PDF | manuscript PDF chunk `11` (Table 1 / p. 10 excerpt); chunk `9` (Figure 7 / p. 7 excerpt) | Partial | `0.108s` | The retrieval set is only suggestive for "poorly constrained" | The manuscript chunks show very large parameter uncertainties and note that high-multiplicity values differ, but they do not cleanly ground that phrasing as an explicit manuscript claim. |
| RAG-07 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | `hepdata-ins1419652-selected-pt-multiplicity-tables`; `hepdata-ins1419652-table-index` | selected-tables chunks `3` and `0`; table-index chunk `0` | Fail | `0.101s` | `research/robert/evidence-ledger.md` is not reachable through the scoped document sets | Retrieval returned unrelated HEPData chunks instead of the Bose-Einstein versus Boltzmann/Juttner claim-status record. |
| RAG-08 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | Robert boson draft PDF; `hepdata-ins1419652-selected-pt-multiplicity-tables` | manuscript PDF chunk `3`; selected-tables chunks `1` and `3` | Fail | `0.095s` | `research/robert/validation-plan.md`, `fit-plan.md`, and `next-actions.md` are not in the scoped retrieval path | The run returned theory/manuscript and HEPData chunks instead of the validation-gate checklist. |
| RAG-09 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | `Tsallis statistics - Wikipedia`; Robert boson draft PDF | Wikipedia chunk `2`; manuscript PDF chunk `1` | Fail | `0.101s` | `physics/src/boson_paper_analysis.py` was not retrieved from the scoped sets | Retrieval drifted to a generic Tsallis page and the manuscript PDF instead of the local sanity-check script provenance. |
| RAG-10 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | `hepdata-ins1419652-selected-pt-multiplicity-tables` | selected-tables chunks `0`, `3`, and `90` | Fail | `0.111s` | `physics/src/tsallis_physics_validation.py` and `docs/ops/critical-components.md` are out of scope for this run | The retrieval set never surfaced the local simplified-helper warning or a literature-matched baseline note. |
| RAG-11 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | Robert boson draft PDF; `hepdata-ins1419652-selected-pt-multiplicity-tables` | manuscript PDF chunks `11`, `7`, and `5`; selected-tables chunk `3` | Fail | `0.098s` | `research/robert/runs/2026-04-26-baseline-fit/README.md` is not in the scoped document sets | Retrieval did not ground the missing full `pT` data-table blocker for the blocked baseline-fit run. |
| RAG-12 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | `Tsallis statistics - Wikipedia`; `hep-native-arxiv-1602-01633-inspire`; `hepdata-ins1419652-selected-pt-multiplicity-tables` | Wikipedia chunk `3`; arXiv/INSPIRE chunk `0`; selected-tables chunk `3` | Fail | `0.118s` | No literature-matched Tsallis/Tsallis-Pareto source is attached yet | The best retrieval result is still a generic Wikipedia page, not a paper suitable for parameter-level baseline comparison. |
| RAG-13 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | Robert boson draft PDF; `Tsallis statistics - Wikipedia` | manuscript PDF chunks `11` and `9`; Wikipedia chunk `1` | Fail | `0.098s` | No Blast-Wave baseline source is attached yet | Retrieval substitutes Robert's manuscript fit outputs and generic Tsallis background for the missing Blast-Wave literature. |
| RAG-14 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | `hepdata-ins1419652-selected-pt-multiplicity-tables`; Robert boson draft PDF | selected-tables chunks `3` and `0`; manuscript PDF chunk `11` | Fail | `0.117s` | No comparison paper with literature-matched Tsallis/Tsallis-Pareto fit-quality tables is attached yet | Retrieval returns HEPData source-grounding chunks and Robert's manuscript rather than an external comparison paper reporting `chi2/ndf`. |
| RAG-15 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | Robert boson draft PDF; `hepdata-ins1419652-selected-pt-multiplicity-tables` | manuscript PDF chunks `11` and `8`; selected-tables chunk `3` | Fail | `0.148s` | No baseline small-system radial-flow-like literature is attached yet | The run surfaced Robert's own fit plots, not external context that could be cited with the required no-causality guard. |
| RAG-19 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | `Tsallis statistics - Wikipedia`; `hep-native-arxiv-1602-01633-inspire` | Wikipedia chunk `3`; arXiv/INSPIRE chunk `0` | Fail | `0.097s` | Retrieval-only search does not invoke Scite/Consensus, and the attached sets lack citation-context sources for Tsallis or Blast-Wave standardness | The result set never grounded whether Robert's cited comparison references are standard in the literature. |
| RAG-20 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | `Tsallis statistics - Wikipedia`; `hep-native-arxiv-1602-01633-inspire` | Wikipedia chunks `3` and `0`; arXiv/INSPIRE chunk `0` | Fail | `0.091s` | The platform audit describing persona attachments is not in the scoped document sets | Retrieval did not surface the document-set/tool attachment state for `Physics Validation Mode`. |
| RAG-21 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | `hepdata-ins1419652-selected-pt-multiplicity-tables`; `Tsallis statistics - Wikipedia`; Robert boson draft PDF | selected-tables chunk `0`; Wikipedia chunk `0`; manuscript PDF chunk `0` | Fail | `0.092s` | The embedding-model/dimension audit note is not in the scoped document sets | No retrieved chunk grounded the active Nomic 768 setting or the reindex requirement for embedding swaps. |
| RAG-22 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | `hepdata-ins1419652-selected-pt-multiplicity-tables`; `hep-native-arxiv-1602-01633-inspire`; Robert boson draft PDF | selected-tables chunk `0`; arXiv/INSPIRE chunk `0`; manuscript PDF chunk `5` | Fail | `0.091s` | The Unstructured integration caveat lives only in the ops audit, not in the scoped document sets | Retrieval returned source-grounding and manuscript chunks instead of the `UNSTRUCTURED_API_URL` caveat. |
| RAG-23 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | Robert boson draft PDF | manuscript PDF chunk `5` (Figures 3-5 / pp. 3-4 excerpt); chunks `11` and `9` | Pass | `0.095s` | None for retrieval | The manuscript chunk directly grounds the `pT`/eta-cut discussion and states that `pT > 200 MeV` and `pT > 300 MeV` change the distribution shape up to about `1.2 GeV` and `1.8 GeV`. |
| RAG-24 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | Robert boson draft PDF; `hepdata-ins1419652-selected-pt-multiplicity-tables`; `Tsallis statistics - Wikipedia` | manuscript PDF chunk `1`; selected-tables chunks `3` and `0`; Wikipedia chunk `2` | Fail | `0.104s` | The local sanity-check script was not retrieved under this scoped path | The manuscript derivation was retrieved, but the run could not separate manuscript evidence from the local `U -> 0` sanity check because the script provenance chunk never surfaced. |
| RAG-25 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | `hepdata-ins1419652-selected-pt-multiplicity-tables`; `hep-native-arxiv-1602-01633-inspire`; `hepdata-ins1419652-table-index` | selected-tables chunks `0` and `3`; arXiv/INSPIRE chunk `1`; table-index chunk `1` | Fail | `0.102s` | `research/robert/evidence-ledger.md`, `validation-plan.md`, and `referee-report-draft.md` are not in the scoped document sets | Retrieval returned general source-grounding records instead of the report-readiness evidence gates. |

Assessment:

- Passes from the scoped retrieval path are currently limited to manuscript table/figure lookup (`RAG-04`, `RAG-23`) plus the already-recorded HEP-native identifier/dataset questions (`RAG-16` through `RAG-18`).
- `RAG-02`, `RAG-03`, `RAG-05`, and `RAG-06` have partial coverage: the relevant Robert manuscript chunks are in the retrieved set, but ranking noise or missing canonical fallback files prevents a clean answer.
- `RAG-12`, `RAG-13`, `RAG-14`, `RAG-15`, and `RAG-19` remain blocked by missing baseline literature coverage in `HEP Phenomenology References`. This is the next issue in the queue.
- `RAG-07` through `RAG-11` and `RAG-20` through `RAG-25` largely fail for structural scoping reasons: the needed `research/robert/`, `physics/src/`, and `docs/ops/` canonical files are not reachable through the three attached document sets used for this retrieval-only baseline.

## Baseline Literature Coverage Follow-up - 2026-04-27

Change applied:

- `deployment/onyx/hep_readonly_tools.py` now seeds two additional `INGESTION_API` documents into `HEP Phenomenology References`: `hep-baseline-tsallis-large-pt` and `hep-baseline-blast-wave-ssh-1993`.
- The Tsallis baseline document is grounded in arXiv `1501.07127` / DOI `10.1140/epjc/s10052-015-3629-9` and includes the charged-particle mid-rapidity formula, fitted parameter set `(q, T, R or V)`, explicit Table 1 `chi2/NDF` values, and an explicit contrast against the local simplified helper in `physics/src/tsallis_physics_validation.py`.
- The Blast-Wave baseline document is grounded in arXiv `nucl-th/9307020` / DOI `10.1103/PhysRevC.48.2462` and includes the canonical Schnedermann-Sollfrank-Heinz transverse-flow formula, the `beta_s`, `n`, `rho`, and `T` parameterization, and an explicit pp-versus-heavy-ion applicability warning.
- No containers were restarted, no connector was reset, no broad reindex was run, no embeddings were changed, and no services were exposed beyond localhost. Retrieval remained on Vespa because `opensearch_tenant_migration_record.enable_opensearch_retrieval=false`.

Verification:

- `python -m py_compile deployment/onyx/hep_readonly_tools.py` passed on the host before ingestion.
- The final ingest used the existing in-container `upsert_ingestion_doc` path, scoped only to the two new baseline documents, after a broader refresh attempt stayed quiet before commit. This kept the change narrow and avoided touching unrelated seeded coverage.
- Postgres metadata confirms both new documents are present, public, `from_ingestion_api=true`, and indexed on connector id `11` / credential id `0`:
  - `hep-baseline-tsallis-large-pt` with `chunk_count=4`
  - `hep-baseline-blast-wave-ssh-1993` with `chunk_count=3`
- As with the earlier HEP-native seed, OpenSearch alt-index writes emitted non-fatal `version_conflict_engine_exception` / `BulkIndexError` noise for already-existing chunk ids and then completed. The document metadata still shows the new docs as indexed.

Follow-up run scope:

- Re-ran `RAG-12`, `RAG-13`, and `RAG-14` from inside `onyx-api_server-1` through the same EE `stream_search_query` path used for the baseline retrieval audit.
- Used `anonymous@onyx.app`, `num_hits=8`, `include_content=true`, `run_query_expansion=false`, and no LLM document selection, scoped again to `Physics`, `Robert Boson Draft`, and `HEP Phenomenology References`.

Follow-up run sheet:

| ID | Persona/document set | Observed cited source | Observed chunk/page | Answer status | Latency | Failure mode | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RAG-12 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | `hep-baseline-tsallis-large-pt` | Tsallis baseline chunk `1` | Pass | `0.944s` | None for retrieval | The top retrieved chunk now carries both the literature-matched charged-particle Tsallis formula and an explicit contrast against `physics/src/tsallis_physics_validation.py`, including the local `(T, beta_T, q)` parameterization, the extra flow term, and the massless `E ~= pT` approximation. |
| RAG-13 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | `hep-baseline-blast-wave-ssh-1993` | Blast-Wave baseline chunk `1` | Pass | `0.161s` | None for retrieval | The top retrieved chunk now grounds the canonical Blast-Wave comparison source, its thermal-plus-radial-flow parameter set, and the required warning that the seeded paper is an S+S heavy-ion source rather than a pp charged-particle fit paper. |
| RAG-14 | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References | `hep-baseline-tsallis-large-pt` | Tsallis baseline chunk `0` | Pass | `0.170s` | None for retrieval | The top retrieved chunk now cites a literature-matched charged-particle Tsallis paper with explicit Table 1 `chi2/NDF` values for ATLAS and CMS `pp` spectra, which is sufficient for the requested fit-quality comparison lookup. |

Follow-up assessment:

- The smallest credible baseline-literature set for this retrieval lane is now attached to `HEP Phenomenology References`.
- `RAG-12`, `RAG-13`, and `RAG-14` now pass under the same retrieval-only baseline method used for the rest of the audit.
- The remaining literature-side gap in this queue is `RAG-15`, which still needs a source-grounded small-system radial-flow comparison rather than only formula provenance.
- `RAG-19` remains blocked in retrieval-only mode because the attached document sets still do not provide citation-context evidence for whether Robert's comparison references are standard in the literature; that likely needs either additional citation-context sources or a tool-invocation path rather than plain document retrieval.

## Manuscript-To-Source Table Mapping Bound - 2026-04-27

Question:

- Can the manuscript's fitted multiplicity bins be mapped to the currently indexed HEPData tables or to any Robert-provided fitting/source table already present in the repo?

Verified manuscript-side binning:

- The local manuscript file `boson probability function for the moving system.pdf` contains a Table 1 with fitted all-eta multiplicity intervals `21-30`, `31-40`, `41-50`, `51-60`, `61-70`, `71-80`, `81-90`, `91-100`, `101-125`, and `126-150`, together with fitted `U1`, `kT1`, `U2`, `kT2`, and `kT3`.
- The local `physics/src/boson_paper_analysis.py` notes and the current `research/robert/next-actions.md` queue are consistent with that state: the fit review has parameter summaries from retrieved chunks, but the full per-bin source `pT` table is still missing.

Verified indexed-source-side coverage:

- The indexed HEPData mapping chunk for `hepdata-ins1419652-selected-pt-multiplicity-tables` groups the seeded source-grounding tables into:
  - inclusive `pT` spectra: Tables `4`, `8`, `12`, and `16`, each with qualifiers such as `N(P=3) >= 1`
  - multiplicity distributions: Tables `5`, `9`, `13`, and `17`
  - average `pT` versus multiplicity: Tables `6`, `10`, `14`, and `18`
- The retrieved HEPData mapping text explicitly states that these selected tables provide inclusive spectra plus multiplicity-level distributions, but do not establish a source-to-pipeline mapping for `pT` spectra split by every manuscript fitting multiplicity bin.

Repo-artifact check:

- `research/robert/` currently contains plans, validation notes, and run readmes, but no Robert-provided machine-readable `pT` source table or per-bin fitting table that can be linked to the manuscript intervals above.
- Because `research/robert/next-actions.md` already has the canonical science task `Get Robert's full pT data table for all multiplicity bins`, no additional science-file edit was needed for this issue.

Bounded conclusion:

- The mapping gap is not row rendering anymore; it is a real source-coverage gap.
- With the current indexed set, I can ground that ATLAS 13 TeV HEPData provides inclusive charged-particle `pT` spectra with row-level `stat`/`sys` uncertainties and separate multiplicity/mean-`pT` tables.
- I cannot defensibly map the manuscript fit bins `21-30` through `126-150` to indexed `pT` source tables, and I did not infer such a mapping from suggestive similarity.
- To close the gap, the workflow needs either Robert's per-bin `pT` source table or an explicitly matched HEPData selection that exposes `pT` spectra for those multiplicity intervals.

## OpenSearch Retrieval Cutover Readiness - 2026-04-27

Scope:

- Read-only verification of whether the current tenant can safely switch retrieval from Vespa to OpenSearch.
- No tenant flag was changed, no reindex was started, no connector was reset, and no containers were restarted.

Verified state:

- The live tenant record in `opensearch_tenant_migration_record` still has `enable_opensearch_retrieval=false`.
- The same singleton record is not in a migrated state: `document_migration_record_table_population_status='PENDING'`, `overall_document_migration_status='PENDING'`, `total_chunks_migrated=0`, `total_chunks_errored=0`, `total_chunks_in_vespa=0`, and `approx_chunk_count_in_vespa=0`.
- The per-document migration table is empty: `opensearch_document_migration_record` currently has zero rows.
- The live OpenSearch cluster is reachable and the active Nomic indexes exist:
  - `danswer_chunk_nomic_ai_nomic_embed_text_v1` with `docs.count=29`
  - `danswer_chunk_nomic_ai_nomic_embed_text_v1__danswer_alt_index` with `docs.count=178`
- Postgres currently marks `19` documents as indexed with a summed `chunk_count=224`.

Coverage/parity check:

- Every currently indexed DB document appears somewhere in the OpenSearch indices, but the active contextual alt index is not chunk-complete for several documents that matter to the current physics workflow.
- Examples from the direct DB-versus-OpenSearch comparison:
  - `hepdata-ins1419652-selected-pt-multiplicity-tables`: DB `120` chunks versus OpenSearch alt index `96`
  - `hepdata-ins1419652-table-index`: DB `5` versus alt `4`
  - `hep-native-arxiv-1602-01633-inspire`: DB `3` versus alt `2`
  - `hep-baseline-tsallis-large-pt`: DB `4` versus alt `3`
  - `hep-baseline-blast-wave-ssh-1993`: DB `3` versus alt `2`
- The primary OpenSearch index also contains stale extra document ids not present in the current indexed DB set, which is additional evidence that the cutover state is not cleanly reconciled.

Recommendation:

- Do not enable OpenSearch retrieval for this tenant yet.
- The blocking prerequisites are:
  1. populate or repair the OpenSearch migration bookkeeping so the tenant record and per-document migration table reflect reality instead of a permanently pending/zeroed state
  2. reconcile chunk parity for the active contextual index, especially for the HEPData and newly seeded baseline-literature documents now used in the retrieval evaluation set
  3. clear or account for stale primary-index documents before treating the OpenSearch copy as the canonical retrieval surface
- The model-server alignment mismatch remains an operational risk for any future reindex or rebuild, but the immediate cutover blocker is the inconsistent migration and chunk-parity state above.

## Local Unstructured Integration Bound - 2026-04-27

Scope:

- Read-only inspection of the current Onyx code path and runtime configuration for local Unstructured usage.
- No API/background containers were restarted and no container-local code was modified in place.

Verified runtime/config state:

- `deployment/onyx/docker-compose.yml` already sets `UNSTRUCTURED_API_URL=http://unstructured:8000` for both `api_server` and `background`.
- The local Unstructured API itself is healthy and reachable on the Docker network at `http://unstructured:8000`.
- The tenant key-value store currently has no `unstructured_api_key` entry.

Verified code-path blockers:

- `/app/onyx/file_processing/extract_file_text.py` only attempts Unstructured when `get_unstructured_api_key()` is truthy. Without a stored key, both the legacy text-only path and the structured extraction path skip Unstructured entirely and fall back to built-in parsers.
- `/app/onyx/file_processing/unstructured.py` constructs `UnstructuredClient(api_key_auth=get_unstructured_api_key())` and does not pass `server_url`.
- A direct SDK inspection inside `onyx-api_server-1` shows that `UnstructuredClient(api_key_auth='dummy')` defaults to `sdk_configuration.server_url='https://platform.unstructuredapp.io'`, while `UnstructuredClient(..., server_url='http://unstructured:8000')` correctly targets the local container. This confirms there is no config-only fix through the current Onyx code path.

Smallest safe step:

- The smallest safe functional change is an Onyx backend patch, not another Compose or admin-config tweak.
- The patch needs both of the following:
  1. pass `server_url=os.environ.get("UNSTRUCTURED_API_URL", "http://unstructured:8000")` into `UnstructuredClient`
  2. relax the extraction gate so local Unstructured can be used when a local `UNSTRUCTURED_API_URL` is configured, even if no cloud-style `unstructured_api_key` is stored

Why I did not patch it here:

- The affected code lives in the running Onyx application under `/app/onyx/file_processing/*.py`, not in a vendored source tree under `/home/ubuntu/aisci`.
- A durable fix therefore needs either an upstream/local image-source patch or a deliberate local overlay/build workflow. Applying an ad hoc container-local edit here would not be durable and would still require the restart that we have not justified or approved for this issue.

Patch plan:

```python
UnstructuredClient(
    api_key_auth=get_unstructured_api_key() or "local",
    server_url=os.environ.get("UNSTRUCTURED_API_URL", "http://unstructured:8000"),
)
```

- Companion gate change: in `extract_file_text.py`, replace the current `if get_unstructured_api_key():` guard with a predicate that also allows the local path when `UNSTRUCTURED_API_URL` is set.
- After that code exists in a durable source location, the smallest justified rollout would be to recreate only `api_server` and `background`, then test a representative PDF through the local path.

## Remaining Platform Blockers Sweep - 2026-04-27

Scope:

- Read-only verification of the remaining model-stack and indexing-noise blockers after Issues 1 through 5.
- No containers were restarted, no models were pulled, no connector was reset, and no reindex was started.

Verified state:

- Model-server alignment is still wrong at runtime:
  - `onyx-inference_model_server-1` exports `DOCUMENT_ENCODER_MODEL=sentence-transformers/all-MiniLM-L6-v2`, `EMBEDDING_DIM=384`, and `DEFAULT_CROSS_ENCODER_MODEL_NAME=BAAI/bge-reranker-v2-m3`
  - `onyx-indexing_model_server-1` exports the same MiniLM/384 values with `INDEXING_ONLY=True`
  - Postgres search settings still mark `nomic-ai/nomic-embed-text-v1` at `768` dimensions as the active present index configuration
- GPU availability is still absent inside the relevant containers even though the host has an `NVIDIA GeForce RTX 3090`:
  - both model servers report `{'gpu_available': False, 'type': 'none'}`
  - `onyx-ollama-1` has no `nvidia-smi` binary/device path available
- LiteLLM is still unhealthy as a whole:
  - `GET /v1/models` lists the configured aliases
  - `GET /health` reports `healthy_count=0` and `unhealthy_count=7`
  - the unhealthy reasons now separate into concrete buckets: missing Ollama models (`gemma2:27b`, `nomic-embed-text:latest`), a misrouted embedding alias that asks Ollama for `sentence-transformers/all-MiniLM-L6-v2`, OpenRouter `401 Unauthorized`, and DashScope free-tier exhaustion
- Ollama itself still has no local models installed: `ollama list` returned an empty table.
- The stale Tsallis/OpenSearch noise is still active but is now tightly characterized:
  - connector `3` (`Tsallis_statistics`) continues to finish with `SUCCESS`
  - the web fetch path still takes a `403 Forbidden` first hit and then succeeds via browser automation
  - Vespa reports `Updated 7 chunks for document https://en.wikipedia.org/wiki/Tsallis_statistics`
  - OpenSearch then emits repeated no-op updates for chunks `0` through `3` and a `404 document_missing_exception` for chunk `4`, followed by `Skipping update for now...`
  - this lines up with the chunk-parity gap already recorded in the OpenSearch cutover section rather than a connector-run failure
- The background monitor false positives are also still present but bounded:
  - `monitor_process_memory` logs a duplicate `beat` process type and a large missing-process set
  - the immediately following memory lines still show `beat`, `heavy`, `light`, `monitoring`, `primary`, and `slack` PIDs with resident memory
  - queue-length logs remain at zero across the monitored queues, so the current evidence points to monitor classification/noise rather than worker outage

Exact next actions:

- Keep Vespa as the active retrieval backend until the OpenSearch parity and migration-record issues are fixed.
- Fix model-server runtime alignment and GPU passthrough before any reindex or embedding-model change:
  1. expose GPUs to `inference_model_server`, `indexing_model_server`, and `ollama`
  2. make the runtime model-server env match the active Nomic `768`-dim search settings
- Restore the local LLM stack in the dependency order that actually matters:
  1. pull the intended Ollama models
  2. fix LiteLLM aliases that currently point missing or wrong backends
  3. repair OpenRouter/DashScope credentials or disable those dead aliases so `/health` becomes meaningful
- Treat the Tsallis OpenSearch warnings as an index-consistency task, not as a connector-reset task. The connector is succeeding; the noisy part is the stale/incomplete OpenSearch copy.
- Treat the background monitor issue as log/monitor hygiene until the process-classification rule is fixed. The current logs do not show an actual queue or worker outage.

## Current Processing Map

| Endpoint / role | Container | Ports | Main non-secret config | Processing role | Current use |
| --- | --- | --- | --- | --- | --- |
| Onyx API server | `onyx-api_server-1` | Internal `8080`; reached through `onyx-nginx-1` on host `80` and `3000` | `MODEL_SERVER_HOST=inference_model_server`, `POSTGRES_HOST=relational_db`, `VESPA_HOST=index`, `OPENSEARCH_HOST=opensearch`, OpenSearch indexing env enabled, OpenSearch retrieval env enabled but DB retrieval flag currently false, `UNSTRUCTURED_API_URL=http://unstructured:8000`, S3/MinIO file store | Web/API backend, chat orchestration, retrieval orchestration, persona/tool config, calls model server for local embeddings/rerank where configured | Yes. `/api/health` returned OK |
| Onyx background workers | `onyx-background-1` | No host port | `MODEL_SERVER_HOST=inference_model_server`, `INDEXING_MODEL_SERVER_HOST=indexing_model_server`, same DB/index/cache/file-store config as API | Connector sync, parsing/indexing pipeline, contextual RAG chunk generation, embedding calls, index writes, migration queues | Yes. Recent index attempts are successful and queues were idle |
| Inference model server | `onyx-inference_model_server-1` | Internal `9000`; no host port | Intended by API as query-time model server. Runtime env showed `DOCUMENT_ENCODER_MODEL=sentence-transformers/all-MiniLM-L6-v2`, `EMBEDDING_DIM=384`, `NORMALIZE_EMBEDDINGS=True`; no GPU devices | Local query-time bi-encoder embeddings. API code expects local reranker endpoint `/encoder/cross-encoder-scores`, but this server exposes only `/encoder/bi-encoder-embed` | Used for local embeddings if `provider_type` is blank. Misaligned with active Nomic 768 index |
| Indexing model server | `onyx-indexing_model_server-1` | Internal `9000`; no host port | `INDEXING_ONLY=True`; runtime env also showed MiniLM/384; no GPU devices | Local indexing embeddings | Used by background workers. Misaligned with active Nomic 768 index |
| LiteLLM proxy | `onyx-litellm-1` | Host/internal `4000` | `litellm_config.yaml` exposes `gemma2`, `qwen-coder`, OpenRouter/DashScope models, and two embedding aliases. Secrets redacted | Chat gateway, possible OpenAI-compatible route for cloud/local models. LiteLLM can also expose `/embeddings` and `/rerank` if correctly configured | Present but unhealthy. Onyx default LLM provider points at `http://litellm:4000`, but configured models are not currently usable |
| Ollama | `onyx-ollama-1` | Internal `11434`; no host port | `OLLAMA_API_BASE=http://ollama:11434`; intended models in env include chat, coder, and Nomic embedding names | Local chat generation, local vision chat, possible local embeddings through Ollama/LiteLLM | Present but unusable now: `ollama list` returned no models and container has no GPU device access |
| Unstructured API | `onyx-unstructured-1` | Internal `8000`; host `9560` | `UNSTRUCTURED_API_URL=http://unstructured:8000`; host mapping `localhost:9560`; endpoint docs at `/general/docs`; OpenAPI at `/general/openapi.json`; partition endpoint `/general/v0/general` | Document parsing/partitioning for PDFs, text, HTML, etc. Can return element text and metadata | API itself works. Onyx ingestion likely not using it until the SDK server URL/key path is fixed |
| Vespa | `onyx-index-1` | Internal Vespa ports; no host port | `VESPA_HOST=index`; `VESPA_SKIP_UPGRADE_CHECK=true` | Legacy vector/keyword document index and migration source/fallback | Present and used by the RAG-16 through RAG-18 retrieval run because the DB OpenSearch retrieval flag is false |
| OpenSearch | `onyx-opensearch-1` | Internal `9200`, `9300`, `9600`, `9650`; no host port | OpenSearch indexing/retrieval env enabled; auth via env; single-node | Active indexed copy and migration target; retrieval only if DB migration flag allows it | Yes. Yellow cluster from unassigned replicas on single node; active Nomic indexes present, but tenant retrieval flag is currently false |
| Postgres | `onyx-relational_db-1` | Internal `5432`; no host port | Onyx DB metadata and app state | Users, personas, connectors, credentials, search settings, LLM providers, index attempt metadata | Yes |
| Redis | `onyx-cache-1` | Internal `6379`; no host port | `REDIS_HOST=cache` | Celery/worker queues, cache, locks | Yes |
| MinIO | `onyx-minio-1` | Internal `9000`, console `9001`; no host port | S3-compatible file store; credentials via env | Uploaded files and extracted artifacts | Yes when `FILE_STORE_BACKEND=s3` |
| Code interpreter | `onyx-code-interpreter-1` | Internal `8000`; no host port | `CODE_INTERPRETER_BASE_URL=http://code-interpreter:8000` | Tool execution for enabled assistants | Present and available to personas/tools that enable it |
| Nginx/web | `onyx-nginx-1`, `onyx-web_server-1` | Host `80`, `3000`; internal web/API routing | `INTERNAL_URL=http://api_server:8080` | UI and reverse proxy | Yes |

## Live Verification Results

Non-destructive checks run:

- `docker ps`: all Onyx containers were up; API and Unstructured were healthy.
- `docker compose ps` from `deployment/onyx`: Compose labels now point at `/home/ubuntu/aisci/deployment/onyx/docker-compose.yml`.
- Onyx health: `GET http://localhost:3000/api/health` returned success.
- LiteLLM: `/v1/models` listed the configured aliases, but `/health` reported zero healthy endpoints.
- Ollama: `ollama list` returned no local models.
- Model servers: `/api/health` returned OK; `/api/gpu-status` returned no GPU; `/openapi.json` exposed `['/api/gpu-status', '/api/health', '/encoder/bi-encoder-embed', '/metrics']`.
- OpenSearch: cluster was yellow due to single-node unassigned replicas. Active content indexes:
  - `danswer_chunk_nomic_ai_nomic_embed_text_v1`: 29 docs
  - `danswer_chunk_nomic_ai_nomic_embed_text_v1__danswer_alt_index`: 71 docs
- OpenSearch env flags are enabled, but `opensearch_tenant_migration_record.enable_opensearch_retrieval=false`; the RAG-16 through RAG-18 run logged Vespa retrieval profile `hybrid_search_keyword_base_768`.
- Search settings in Postgres:
  - Active primary: `nomic-ai/nomic-embed-text-v1`, 768 dimensions.
  - Active alternate/contextual index: `nomic-ai/nomic-embed-text-v1`, 768 dimensions, multipass enabled, contextual RAG enabled.
- Recent index attempts for active search settings id `4` were successful.

## Retrieval Evaluation Set

Purpose: run these questions before changing embeddings, rerank settings, contextual RAG, parser settings, document-set coverage, or production persona prompts. Record observed cited source, cited chunk or page, answer status, latency, and notes for each query. Questions whose expected source is marked as missing coverage are intended to fail until that source/tool is ingested; treat those failures as coverage gaps, not as model-quality failures.

| ID | Question | Expected source | Required answer type | Pass/fail criteria | Coverage notes |
| --- | --- | --- | --- | --- | --- |
| RAG-01 | What exact manuscript formula defines the particle probability or spectrum, and is it a full Bose-Einstein denominator or a Boltzmann/Juttner-style exponential approximation? | `Robert Boson Draft` / `boson probability function for the moving system.pdf` | Equation classification | Pass if the answer cites the manuscript equation or page and explicitly separates full Bose-Einstein wording from Boltzmann/Juttner approximation wording. Fail if it infers the form from local scripts alone. | Core science gate. |
| RAG-02 | Where does the manuscript define the moving-system parameter `U` and its relation to rapidity or velocity? | `Robert Boson Draft` | Definition lookup | Pass if the cited source identifies the manuscript definition and units/conventions, or states that the definition is not recoverable from the indexed text. | Checks notation retrieval. |
| RAG-03 | Which ATLAS 13 TeV acceptance cuts, including `pT` and pseudorapidity or eta cuts, are used in the manuscript fit setup? | `Robert Boson Draft` | Data/method extraction | Pass if the answer cites the acceptance statement and does not substitute assumptions from scripts unless clearly labeled. | Needs exact manuscript wording. |
| RAG-04 | Which multiplicity bins are fitted, and what fitted parameters are reported for each bin? | `Robert Boson Draft` | Table/figure extraction | Pass if the answer cites the relevant table or figure and lists bins/parameters without adding physical interpretation. | Useful for table parsing quality. |
| RAG-05 | Does the manuscript report chi2/ndf, covariance matrices, parameter correlations, residuals, or fit-range sensitivity for every multiplicity bin? | `Robert Boson Draft`; `research/robert/evidence-ledger.md` as local status fallback | Evidence status answer | Pass if it cites manuscript evidence for presence/absence and, if absent, cites the evidence ledger status without upgrading the claim. | Fit-quality gate. |
| RAG-06 | Which manuscript figure or table supports the statement that high-multiplicity fit parameters are poorly constrained? | `Robert Boson Draft`; `research/robert/evidence-ledger.md` | Evidence lookup | Pass if it cites the manuscript values or uncertainty table and labels any interpretation as `Suggestive` unless full covariance/refits exist. | Avoid causal/root-cause inference. |
| RAG-07 | What is the current evidence-ledger status for the claim that the manuscript uses full Bose-Einstein rather than Boltzmann/Juttner? | `research/robert/evidence-ledger.md` | Ledger-status lookup | Pass if the answer returns the exact claim status and required next evidence. Fail if it answers from memory or promotes the claim. | Requires local repo file access if not indexed. |
| RAG-08 | What validation gates must pass before plotting or interpreting `U` and temperature trends versus multiplicity? | `research/robert/validation-plan.md`; `research/robert/fit-plan.md`; `research/robert/next-actions.md` | Checklist | Pass if it cites fit quality, covariance, correlations, residuals, fit-range sensitivity, and baseline comparisons. | Science guardrail retrieval. |
| RAG-09 | What assumptions limit the local `boson_paper_analysis.py` sanity checks? | `physics/src/boson_paper_analysis.py`; `research/robert/evidence-ledger.md` | Code/provenance summary | Pass if it cites massless or ultra-relativistic and Boltzmann/Juttner-like assumptions, and says the script is not final validation. | Tests code-file retrieval. |
| RAG-10 | What does `tsallis_physics_validation.py` say about the simplified Tsallis-like helper versus a literature-matched baseline? | `physics/src/tsallis_physics_validation.py`; `docs/ops/critical-components.md` | Code/provenance summary | Pass if it cites that the helper is simplified and not yet literature-matched. | Prevents overclaiming baseline quality. |
| RAG-11 | What blocks the `2026-04-26-baseline-fit` run from producing fit artifacts? | `research/robert/runs/2026-04-26-baseline-fit/README.md` | Blocker lookup | Pass if it cites the missing full `pT` data table and does not create or imply empty artifacts. | Run hygiene check. |
| RAG-12 | Retrieve the literature-matched Tsallis or Tsallis-Pareto formula intended for charged-particle `pT` spectra and compare its parameters to the local simplified helper. | `HEP Phenomenology References`; literature-matched Tsallis/Tsallis-Pareto paper | Formula comparison | Pass only if an ingested paper is cited and the local helper is cited separately. Fail if no paper source is available. | Missing or incomplete coverage until comparison papers are ingested. |
| RAG-13 | Retrieve a Blast-Wave baseline formula and identify which fit parameters and collision systems are relevant for comparison. | `HEP Phenomenology References`; literature-matched Blast-Wave source | Formula/context extraction | Pass only with an ingested Blast-Wave citation and a warning about pp versus p-Pb/AA applicability. | Missing coverage until Blast-Wave sources are ingested. |
| RAG-14 | Find a comparison paper that reports fit quality such as chi2/ndf for Tsallis/Tsallis-Pareto fits in LHC `pT` spectra. | `HEP Phenomenology References`; arXiv/INSPIRE plus optional Semantic Scholar/OpenAlex fallback | Literature retrieval | Pass only if the answer cites the paper and the fit-quality table/section. | Missing coverage until literature-matched comparison papers are ingested or retrieved and recorded. |
| RAG-15 | Find baseline literature discussing multiplicity dependence of radial-flow-like behavior in small systems, without using it as causal evidence for Robert's fitted trends. | `HEP Phenomenology References`; Scite/Consensus/arXiv/INSPIRE once available | Literature context | Pass if it cites source context and explicitly avoids causal inference for Robert's model. | External curation task. |
| RAG-16 | For the ATLAS 13 TeV data used in the manuscript, retrieve the arXiv or INSPIRE record and identify DOI, collaboration, and citation metadata. | arXiv/INSPIRE-HEP tool; manuscript references | Identifier lookup | Pass only with an external identifier and citation metadata from the tool or ingested record. | Read-only arXiv/INSPIRE tools and ingested metadata are now available; run and record actual citations/latency. |
| RAG-17 | Locate the HEPData table corresponding to the charged-particle `pT` spectra and multiplicity bins used by the manuscript. | HEPData tool or ingested HEPData record | Dataset lookup | Pass only if it returns table name, record identifier, observable, binning, and uncertainties. | HEPData tool plus selected `ins1419652` table ingestion are now available; run and check whether JSON chunks ground binning/uncertainties clearly. |
| RAG-18 | Does the source dataset provide full `pT` uncertainties for every multiplicity bin needed by the fitting pipeline? | HEPData record; Robert-provided data table if available | Data availability answer | Pass if it cites the dataset/table or states that the required data are unavailable from indexed sources. | Partially covered by selected HEPData table ingestion; reproducible fitting still needs source-to-pipeline table mapping. |
| RAG-19 | Use external citation tooling to find whether Robert's cited Tsallis or Blast-Wave references are standard for this comparison. | Scite/Consensus plus arXiv/INSPIRE; Semantic Scholar/OpenAlex remain optional fallbacks | Citation-context answer | Pass only if it cites external records and separates citation context from scientific endorsement. | Run still needs recorded citation outcomes. |
| RAG-20 | Which document sets and tools are attached to `Physics Validation Mode`, and what coverage gaps remain? | This audit; `docs/ops/critical-components.md`; Onyx metadata if queried | Platform status answer | Pass if it lists Physics, Robert Boson Draft, HEP Phenomenology References, internal search/file reader/Python/open URL/Scite/Consensus/arXiv/INSPIRE-HEP/HEPData, and the remaining baseline-source gaps. | Platform persona check. |
| RAG-21 | What active embedding model and dimension are in use, and why should embedding swaps wait? | This audit | Platform status answer | Pass if it cites Nomic 768-dimensional active indexes and the reindex requirement for model/dimension changes. | Tuning safety gate. |
| RAG-22 | What local Unstructured integration caveat could affect PDF parsing quality? | This audit | Platform status answer | Pass if it cites that the local Unstructured API works but Onyx may not pass `UNSTRUCTURED_API_URL` into `UnstructuredClient`. | Parser tuning gate. |
| RAG-23 | Which manuscript figure or section demonstrates the effect of `pT` or eta cuts on the distribution? | `Robert Boson Draft` | Figure/section lookup | Pass if it cites the manuscript figure/section and does not substitute the local script's illustrative checks as manuscript evidence. | Tests PDF figure/table retrieval. |
| RAG-24 | What happens in the `U -> 0` limit, and which part is manuscript evidence versus a local sanity check? | `Robert Boson Draft`; `physics/src/boson_paper_analysis.py` | Source-separated explanation | Pass if it distinguishes manuscript derivation from the local Boltzmann/Juttner-like script check. | Avoids blending evidence types. |
| RAG-25 | What evidence is still required before a referee-style report can make model-quality or novelty claims? | `research/robert/evidence-ledger.md`; `research/robert/validation-plan.md`; `research/robert/referee-report-draft.md` | Evidence-gap summary | Pass if it cites full data, chi2/ndf, covariance/correlations, residuals, fit-range sensitivity, and literature-matched baselines. | Final report readiness gate. |

Recommended run sheet columns:

| ID | Persona/document set | Observed cited source | Observed chunk/page | Answer status | Latency | Failure mode | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `<question id>` | `Physics Validation Mode` / Physics + Robert Boson Draft + HEP Phenomenology References |  |  |  |  |  |  |

## Unstructured Functional Test

The container is not just healthy; it partitions content successfully.

API discovery:

- `GET http://localhost:9560/healthcheck` returned OK.
- `GET http://localhost:9560/general/docs` returned Swagger UI.
- `GET http://localhost:9560/general/openapi.json` returned the OpenAPI schema.
- The documented local partition endpoint is `POST /general/v0/general`.
- `GET /general/v0/general` returns 405 because only POST is supported.

Host-side partition test:

```bash
curl -fsS -X POST http://localhost:9560/general/v0/general \
  -F files=@README.md \
  -F strategy=fast \
  -F coordinates=true
```

Result:

- Returned 36 elements.
- First elements included `Title`, `NarrativeText`, and `ListItem`.
- Metadata included `filename=README.md`, `filetype=text/markdown`, and detected language `eng`.

Internal Docker-network test:

```bash
docker exec onyx-api_server-1 python - <<'PY'
import requests
files = {"files": ("probe.txt", b"Local Unstructured probe for Onyx parsing.\\nSecond line.", "text/plain")}
data = {"strategy": "fast"}
r = requests.post("http://unstructured:8000/general/v0/general", files=files, data=data, timeout=30)
print(r.status_code, len(r.json()), r.json()[0]["type"], r.json()[0]["metadata"]["filetype"])
PY
```

Result:

- Status `200`.
- Returned one text element with metadata `filetype=text/plain`.

Important Onyx integration caveat:

- The running Onyx code at `/app/onyx/file_processing/unstructured.py` creates `UnstructuredClient(api_key_auth=get_unstructured_api_key())`.
- It does not pass the `UNSTRUCTURED_API_URL` env var as `server_url`.
- The key-value store currently has no `unstructured_api_key` key.
- This means local Unstructured is operational, but Onyx likely falls back to built-in/local parsers or an SDK default rather than the local container unless this code path is patched or configured through the admin/key mechanism in a way that also sets the server URL.

## External Research Notes

- Onyx Standard includes vector/keyword RAG, background connector workers, model inference servers, Redis, and MinIO. The local deployment here matches that shape.
- Onyx Index Settings are the right place for embedding model selection, reranking, multipass indexing, contextual RAG, precision, and reduced dimensions. Onyx warns that embedding swaps require re-indexing.
- Onyx says self-hosted embedding models keep data inside the deployment, but recommends GPU access for the indexing model server.
- Onyx Contextual RAG adds document-level information to each chunk and can improve hybrid retrieval, but it materially increases data added to embedding calls.
- Onyx v3 uses both Vespa and OpenSearch, automatically migrates existing content to OpenSearch, and lets retrieval use either backend during v3. v4 is planned to remove Vespa.
- Onyx OpenSearch local docs describe OpenSearch as the document index used for retrieval in v3-style deployments.
- LiteLLM supports `/embeddings` and `/rerank`, including NVIDIA NIM embeddings and rerankers. Its rerank endpoint follows the Cohere-style request/response shape.
- Onyx can use LiteLLM Proxy as an LLM gateway and reads available model IDs from `/v1/models`, but the local Onyx search code distinguishes local model-server embeddings/rerank from provider/API-based embedding/rerank paths.
- OpenRouter documents embeddings and rerank APIs. Its public catalog on 2026-04-27 listed free or low-cost embedding/rerank options, including `nvidia/llama-nemotron-embed-vl-1b-v2:free` for text+image embeddings and Cohere rerank models.
- Nomic `nomic-ai/nomic-embed-text-v1` is Apache-2.0, 8192-token context, and requires task prefixes such as `search_document:` and `search_query:`.
- BGE-M3 is MIT licensed, supports dense/sparse/multi-vector retrieval modes, multilingual retrieval, and up to 8192 tokens. In Onyx it would likely be used only for dense embeddings unless custom sparse/multi-vector support is added.
- `BAAI/bge-reranker-v2-m3` is Apache-2.0 and is a practical local cross-encoder reranker.
- Qwen3 Embedding 8B is Apache-2.0, supports 32k context, 100+ languages, and configurable output dimensions up to 4096. It is a quality candidate but heavy for this stack and would require a controlled embedding swap/reindex.
- Ollama's `nomic-embed-text` is easy to run but the Ollama library page lists a 2K context window. For this project, the Hugging Face `nomic-ai/nomic-embed-text-v1` path is a better match to the active 768-dim Onyx index and prefixes.
- NVIDIA retrieval APIs list `bge-m3`, NVIDIA text embedding models, NVIDIA rerankers, and multimodal embedding models. NVIDIA also publishes open Nemotron model weights on Hugging Face, while hosted/self-hosted NIM usage has its own API/key/license terms.
- The NVIDIA `llama-nemotron-embed-vl-1b-v2` model card describes a 2048-dimensional text/image embedding model available on Hugging Face and as NVIDIA NIM, useful for visual document retrieval experiments but not a drop-in replacement for the current 768-dim Onyx index.
- Ollama supports `qwen2.5vl` as a local text+image chat model; the 7B tag is about 6 GB and the 32B tag is about 21 GB. This can be useful for image summarization if Onyx's vision LLM provider is configured and verified.

Sources:

- Onyx deployment overview: https://docs.onyx.app/deployment/overview
- Onyx Index Settings: https://docs.onyx.app/admins/advanced_configs/search_configs
- Onyx OpenSearch migration: https://docs.onyx.app/admins/advanced_configs/opensearch_document_index_migration
- Onyx local OpenSearch: https://docs.onyx.app/deployment/local/opensearch
- Onyx Ollama provider: https://docs.onyx.app/admins/ai_models/ollama
- Onyx LiteLLM Proxy provider: https://docs.onyx.app/admins/ai_models/litellm_proxy
- Onyx OpenRouter provider: https://docs.onyx.app/admins/ai_models/openrouter
- Unstructured partition API parameters: https://docs.unstructured.io/api-reference/partition/api-parameters
- Unstructured partition overview: https://docs.unstructured.io/platform-api/partition-api/overview
- LiteLLM embeddings: https://docs.litellm.ai/docs/embedding/supported_embedding
- LiteLLM rerank: https://docs.litellm.ai/docs/rerank
- LiteLLM OpenRouter provider: https://docs.litellm.ai/docs/providers/openrouter
- LiteLLM Ollama provider: https://docs.litellm.ai/docs/providers/ollama
- OpenRouter embeddings: https://openrouter.ai/docs/api/reference/embeddings
- OpenRouter rerank: https://openrouter.ai/docs/api/api-reference/rerank/create-rerank
- OpenRouter model catalog API: https://openrouter.ai/api/v1/models
- Ollama `nomic-embed-text`: https://ollama.com/library/nomic-embed-text
- Ollama `qwen2.5vl`: https://ollama.com/library/qwen2.5vl
- Nomic embedding model card: https://huggingface.co/nomic-ai/nomic-embed-text-v1
- BGE-M3 model card: https://huggingface.co/BAAI/bge-m3
- BGE reranker model card: https://huggingface.co/BAAI/bge-reranker-v2-m3
- Qwen3 Embedding model card: https://huggingface.co/Qwen/Qwen3-Embedding-8B
- NVIDIA retrieval APIs: https://docs.api.nvidia.com/nim/reference/retrieval-apis
- NVIDIA reranking NIM overview: https://docs.nvidia.com/nim/nemo-retriever/text-reranking/1.9.0/overview.html
- NVIDIA `llama-nemotron-embed-vl-1b-v2` model card: https://huggingface.co/nvidia/llama-nemotron-embed-vl-1b-v2
- NVIDIA NIM overview: https://www.nvidia.com/en-us/ai-data-science/products/nim-microservices/

## Recommended Target Architecture

### Local-first baseline

1. Keep the active embedding model as `nomic-ai/nomic-embed-text-v1` at 768 dimensions for now.
   - The live OpenSearch indexes are already built for this model and dimension.
   - The model card requires `search_document:` and `search_query:` prefixes, and the active search settings already have the Nomic-style model/dimension configuration.
   - Changing the embedding model or dimension requires reindexing and careful swap validation.

2. Fix model-server runtime alignment before reindexing or model swaps.
   - API/background settings and OpenSearch indexes say Nomic/768.
   - Model-server processes currently show MiniLM/384 environment.
   - The model servers also lack GPU access. Add explicit local Compose GPU device configuration, then recreate only the model server and Ollama containers after approval.

3. Treat LiteLLM as the chat and fallback gateway, not the primary embedding path, until Onyx search settings are explicitly configured for API-based embeddings/rerank.
   - Onyx reads LiteLLM model IDs for language models.
   - LiteLLM can expose embeddings/rerank, but Onyx must be configured to use those provider/API paths. Adding entries to LiteLLM alone does not make the active Onyx search index use them.

4. Use local Onyx model servers for embeddings.
   - Preferred immediate model: Hugging Face `nomic-ai/nomic-embed-text-v1`.
   - Later quality experiment: `BAAI/bge-m3` or `Qwen/Qwen3-Embedding-4B/8B`, but only through a planned embedding swap and benchmark run.

5. Use a reranker, but verify the actual route first.
   - Preferred local reranker: `BAAI/bge-reranker-v2-m3`.
   - Current env sets `DEFAULT_CROSS_ENCODER_MODEL_NAME=BAAI/bge-reranker-v2-m3`, but the running model-server OpenAPI does not expose `/encoder/cross-encoder-scores`.
   - If local rerank is needed now, either use a model server image/version that exposes cross-encoder scores or configure Onyx's API-based reranker provider to call LiteLLM `/rerank`.

6. Use contextual RAG selectively.
   - Keep contextual RAG enabled for the science document set if cost/latency is acceptable.
   - Use a cheap, reliable chat LLM endpoint for contextual chunk generation. Current settings use an OpenRouter model; verify credentials in the admin UI without printing keys.
   - For fully private indexing, switch contextual RAG to a local Ollama chat model after the model is pulled, GPU access is fixed, and indexing latency is measured.

7. Fix Unstructured integration before importing more HEP PDFs.
   - The local API works and should be used for high-quality parsing.
   - Patch/configure Onyx so `UnstructuredClient` targets `http://unstructured:8000` and does not silently default to the hosted endpoint.
   - After that, test a representative arXiv-style PDF with `fast`, then evaluate `hi_res` and table/image extraction settings for plot/table-heavy papers.

8. Visual/image analysis should be treated as an explicit verification track, not assumed from `IMAGE_MODEL_NAME`.
   - Onyx image summarization uses the default vision-capable LLM from admin LLM settings when image extraction/analysis is enabled.
   - The env values `IMAGE_MODEL_NAME` and `IMAGE_MODEL_PROVIDER` are also used for image generation tooling; they do not by themselves prove PDF visual RAG is active.
   - Local candidate: Ollama `qwen2.5vl:7b` for figure/chart summaries after GPU/Ollama are fixed.
   - Cloud/free fallback: OpenRouter vision-capable free models or NVIDIA VL models, but do not send private papers to cloud endpoints unless that is acceptable.

9. Keep OpenSearch enabled, but do not remove Vespa or force migration yet.
   - OpenSearch is already active and has the current Nomic indexes.
   - Onyx v3 is designed to run both Vespa and OpenSearch while migration completes.
   - Wait to remove Vespa or run broad reindex/migration changes until model-server alignment, Unstructured usage, persona configuration, and a small retrieval evaluation set are fixed.

### Cheap/cloud fallback

- Chat/contextual RAG: OpenRouter through the Onyx OpenRouter provider or LiteLLM Proxy, with per-model credentials and data policy reviewed.
- Embeddings: OpenRouter or NVIDIA endpoints can be useful for experiments, especially `baai/bge-m3`, Qwen3 embeddings, or NVIDIA multimodal embeddings, but they create a new embedding index and reindex requirement.
- Reranking: Cohere-style rerank through OpenRouter or LiteLLM `/rerank`, or NVIDIA NIM rerankers through LiteLLM, if Onyx is configured for API-based reranking.
- Visual document retrieval experiments: NVIDIA `llama-nemotron-embed-vl-1b-v2` is promising for page-image + text embeddings, but it is 2048-dimensional and is not a drop-in replacement for the active Onyx 768-dimensional index.

## Next Actions

Do not run the destructive/recreate/reindex commands below without explicit approval. They are included so the next change is exact and auditable.

### Safe checks

```bash
cd /home/ubuntu/aisci/deployment/onyx
docker compose ps
curl -fsS http://localhost:3000/api/health
curl -fsS http://localhost:4000/v1/models | jq '.data[].id'
docker exec onyx-ollama-1 ollama list
curl -fsS http://localhost:9560/healthcheck
curl -fsS -X POST http://localhost:9560/general/v0/general \
  -F files=@/home/ubuntu/aisci/README.md \
  -F strategy=fast | jq 'length, .[0]'
docker exec onyx-inference_model_server-1 python -c "import urllib.request,json; print(sorted(json.load(urllib.request.urlopen('http://localhost:9000/openapi.json'))['paths'].keys()))"
docker exec onyx-relational_db-1 psql -U postgres -P pager=off \
  -c "select id, model_name, model_dim, status, multipass_indexing, enable_contextual_rag, contextual_rag_llm_name, contextual_rag_llm_provider from search_settings order by id;"
docker exec onyx-opensearch-1 bash -lc 'curl -fsS -k -u "admin:${OPENSEARCH_INITIAL_ADMIN_PASSWORD}" "https://localhost:9200/_cat/indices?v&h=health,status,index,docs.count,store.size&s=index"'
```

### Later changes requiring approval

1. Fix GPU access in `deployment/onyx/docker-compose.yml` for `ollama`, `inference_model_server`, and `indexing_model_server`, likely with explicit Compose `gpus: all` or equivalent device requests that work outside Swarm.

2. Recreate only the affected containers after the Compose change:

```bash
cd /home/ubuntu/aisci/deployment/onyx
docker compose up -d --no-deps --force-recreate inference_model_server indexing_model_server ollama
```

3. Pull only the selected local models:

```bash
docker exec onyx-ollama-1 ollama pull qwen2.5:32b
docker exec onyx-ollama-1 ollama pull qwen2.5-coder:32b
docker exec onyx-ollama-1 ollama pull qwen2.5vl:7b
docker exec onyx-ollama-1 ollama pull nomic-embed-text
```

4. Fix LiteLLM aliases so they match pulled Ollama model tags and working cloud model IDs, then verify:

```bash
curl -fsS http://localhost:4000/health | jq '{healthy_count, unhealthy_count, healthy:[.healthy_endpoints[].model], unhealthy:[.unhealthy_endpoints[].model]}'
```

5. Patch the Onyx custom backend or admin configuration so Unstructured SDK calls target the local server:

```python
UnstructuredClient(
    api_key_auth=get_unstructured_api_key() or "local",
    server_url=os.environ.get("UNSTRUCTURED_API_URL", "http://unstructured:8000"),
)
```

6. Recreate API/background only after the Unstructured integration patch is reviewed:

```bash
cd /home/ubuntu/aisci/deployment/onyx
docker compose up -d --no-deps --build --force-recreate api_server background
```

7. Run the HEP retrieval evaluation set above before any reindex:

- Use all 25 questions and record observed source, chunk/page, answer status, latency, and failure mode.
- Keep expected-missing literature/tool questions separate from questions answerable from the current local document sets.
- Do not treat expected-missing coverage failures as evidence for or against the embedding model.

8. Only after the above, decide whether to keep Nomic/768 or run a planned embedding swap to BGE-M3/Qwen3. Any embedding model or dimension change requires a full reindex/swap and should not be mixed into this cleanup.

## RAG vs. Canonical-Science File Boundary

| Question Family | Canonical Source | Agent Action |
| --- | --- | --- |
| Claim Status | `research/robert/evidence-ledger.md` | Read file directly; do not query RAG. |
| Pending Tasks | `research/robert/next-actions.md` | Read file directly; do not query RAG. |
| Fit Validation | `research/robert/validation-plan.md` | Read file directly; do not query RAG. |

**Practical Agent Rule:**
Never edit research/robert/evidence-ledger.md, validation-plan.md, fit-plan.md, or referee-report-draft.md for ops reasons. Never answer claim-status, validation-gate, run-blocker, or script-assumption questions from RAG. Read the canonical file directly.

## OpenSearch Cutover and Model-Server Fix Order

This section records the concrete dependency order for the remaining blocking issues: LiteLLM contextual-summary timeouts, model-server misalignment, and OpenSearch migration bookkeeping. It is a planning note only; it does not authorize a deployment change.

### Dependency order

1. Fix the contextual-summary path so rebuild attempts can complete instead of timing out in LiteLLM.
2. Fix the OpenSearch write-path bookkeeping bug (`KeyError: 'document_id'` in `transformer.py`) so every OpenSearch document carries a stable `document_id`.
3. Rerun the rebuild sweep for the tracked connector/credential pairs and clear any orphaned or zombie attempts.
4. Verify that `opensearch_document_migration_record` is populated and that `deployment/helper/onyx_opensearch_cutover.py --json` reports chunk parity or a bounded explanation for any remaining mismatch.
5. Only after steps 1 through 4 succeed should the tenant retrieval flag be considered for cutover.

Parallel to that sequence, but still approval-gated:

- align `inference_model_server` and `indexing_model_server` runtime env with the active `nomic-ai/nomic-embed-text-v1` / 768-dimensional search settings
- expose working GPU devices to `ollama`, `inference_model_server`, and `indexing_model_server`
- verify live 768-dimensional embedding output and GPU visibility before any reindex or model swap

### File locations for the minimal implementation diffs

| Step | File location | Minimal change |
| --- | --- | --- |
| LiteLLM timeout | `deployment/onyx/litellm_config.yaml` | Raise the contextual-summary timeout to `300s` for the affected path |
| OpenSearch write bookkeeping | Onyx source file containing `transformer.py` write path | Ensure `document_id` is always present or guarded before the OpenSearch write |
| Rebuild/parity verification | `deployment/helper/onyx_opensearch_cutover.py` plus read-only SQL checks | No code change required for the rerun itself; use it to verify parity and bookkeeping population |
| Model-server alignment | `deployment/onyx/docker-compose.yml` | Set both model servers to `nomic-ai/nomic-embed-text-v1` and `768`, plus working GPU exposure for model servers and `ollama` |

### Cross-links

- Backlog tracker: `docs/ops/platform-backlog.md`
- Current cutover-readiness evidence: `docs/ops/onyx-rag-optimization-2026-04-27.md` section `OpenSearch Retrieval Cutover Readiness - 2026-04-27`
- Current runtime mismatch evidence: `docs/ops/onyx-rag-optimization-2026-04-27.md` section `Remaining Platform Blockers Sweep - 2026-04-27`
- Operational component map: `docs/ops/critical-components.md`
