export const bins = [
  "21-30", "31-40", "41-50", "51-60", "61-70",
  "71-80", "81-90", "91-100", "101-125", "126-150",
];

export const juttner = [68.3, 165.2, 162.7, 159.9, 227.2, 220.4, 207.2, 192.8, 178.1, 110.1];
export const tsallis = [1.4, 1.8, 2.1, 1.9, 2.4, 2.3, 2.1, 1.8, 1.6, 1.5];
export const bose = [1.1, 1.3, 1.5, 1.4, 1.8, 1.7, 1.5, 1.3, 1.2, 1.1];

export const chi2Series = bins.map((bin, i) => ({
  bin,
  "Jüttner 1c": juttner[i],
  "Tsallis 2c": tsallis[i],
  "Bose-Einstein 1c": bose[i],
}));

export type FitRow = {
  bin: string;
  model: "Jüttner 1c" | "Tsallis 2c" | "Bose-Einstein 1c";
  chi2: number;
  quality: "POOR" | "MARGINAL" | "GOOD";
  T: string;
  beta: string;
  aic: number;
  status: string;
};

export const fitRows: FitRow[] = [
  { bin: "21-30", model: "Jüttner 1c", chi2: 68.28, quality: "POOR", T: "0.312 ± 0.008", beta: "0.987 ± 0.002", aic: 3010.4, status: "Converged" },
  { bin: "31-40", model: "Jüttner 1c", chi2: 165.25, quality: "POOR", T: "0.287 ± 0.005", beta: "0.994 ± 0.001", aic: 7276.9, status: "Converged" },
  { bin: "41-50", model: "Jüttner 1c", chi2: 162.73, quality: "POOR", T: "0.291 ± 0.006", beta: "0.992 ± 0.001", aic: 7166.2, status: "Converged" },
  { bin: "51-60", model: "Jüttner 1c", chi2: 159.92, quality: "POOR", T: "0.295 ± 0.006", beta: "0.991 ± 0.001", aic: 7042.6, status: "Converged" },
  { bin: "61-70", model: "Jüttner 1c", chi2: 227.22, quality: "POOR", T: "0.303 ± 0.007", beta: "0.993 ± 0.001", aic: 10003.6, status: "Converged" },
  { bin: "71-80", model: "Jüttner 1c", chi2: 220.4, quality: "POOR", T: "0.308 ± 0.007", beta: "0.994 ± 0.001", aic: 9702.1, status: "Converged" },
  { bin: "81-90", model: "Jüttner 1c", chi2: 207.2, quality: "POOR", T: "0.311 ± 0.008", beta: "0.995 ± 0.001", aic: 9121.4, status: "Converged" },
  { bin: "21-30", model: "Tsallis 2c", chi2: 1.41, quality: "GOOD", T: "0.098 ± 0.003", beta: "—", aic: 44.2, status: "Converged" },
  { bin: "31-40", model: "Tsallis 2c", chi2: 1.80, quality: "GOOD", T: "0.101 ± 0.003", beta: "—", aic: 56.4, status: "Converged" },
  { bin: "61-70", model: "Tsallis 2c", chi2: 2.40, quality: "MARGINAL", T: "0.112 ± 0.004", beta: "—", aic: 75.1, status: "Converged" },
  { bin: "21-30", model: "Bose-Einstein 1c", chi2: 1.11, quality: "GOOD", T: "0.102 ± 0.002", beta: "0.312 ± 0.011", aic: 38.7, status: "Converged" },
  { bin: "31-40", model: "Bose-Einstein 1c", chi2: 1.30, quality: "GOOD", T: "0.104 ± 0.002", beta: "0.318 ± 0.010", aic: 41.2, status: "Converged" },
  { bin: "61-70", model: "Bose-Einstein 1c", chi2: 1.80, quality: "GOOD", T: "0.109 ± 0.003", beta: "0.331 ± 0.012", aic: 52.9, status: "Converged" },
];

export type Paper = {
  source: "arXiv" | "OpenAlex";
  category: string;
  title: string;
  published: string;
  claims: number;
  bridge: boolean;
  abstract: string;
  url: string;
  claimList: { text: string; confidence: "HIGH" | "MEDIUM" | "LOW" }[];
};

export const papers: Paper[] = [
  { source: "arXiv", category: "hep-th", title: "Unification of polynomial and exponential cosmological attractors", published: "2026-07-09", claims: 1, bridge: false, url: "https://arxiv.org/abs/2607.09001", abstract: "We present a unified framework connecting polynomial and exponential inflationary attractor models via a single geometric parameter α. The construction preserves the CMB observational predictions in the strong-coupling limit while extending the moduli space...", claimList: [{ text: "Both attractor families collapse to the same predictions at α → 0", confidence: "HIGH" }] },
  { source: "arXiv", category: "astro-ph.HE", title: "Subsolar-mass binary mergers of strange stars and neutron stars: gravitational waves and ejecta", published: "2026-07-09", claims: 1, bridge: false, url: "https://arxiv.org/abs/2607.09014", abstract: "Numerical relativity simulations of subsolar-mass compact binaries containing strange quark matter reveal distinctive post-merger gravitational-wave signatures and characteristic dynamical ejecta compositions...", claimList: [{ text: "Strange-star mergers eject ~10× more baryonic mass than NS-NS at same total mass", confidence: "MEDIUM" }] },
  { source: "OpenAlex", category: "Bricolage", title: "The Role of Collective Bricolage in Creating University Governance Structures", published: "2026-07-09", claims: 1, bridge: false, url: "https://openalex.org/W4312001", abstract: "This paper analyzes how ad-hoc problem-solving practices scale into formal governance in academic institutions...", claimList: [{ text: "Bricolage precedes formal governance in 78% of case studies surveyed", confidence: "MEDIUM" }] },
  { source: "OpenAlex", category: "State (CS)", title: "2025-2027 Collective Bargaining Agreement — State of Iowa", published: "2027-06-01", claims: 1, bridge: false, url: "https://openalex.org/W4312002", abstract: "Full text of the collective bargaining agreement between the State of Iowa and its labor unions covering the 2025–2027 period...", claimList: [{ text: "Contains grievance procedure applicable to state employees", confidence: "LOW" }] },
  { source: "arXiv", category: "cs.CL", title: "Accurate, Interdisciplinary and Transparent Structure-property Understanding", published: "2026-07-09", claims: 1, bridge: true, url: "https://arxiv.org/abs/2607.09055", abstract: "We show that LLM-based extraction pipelines can transparently link materials-science structure descriptors to bulk properties across three disciplines, with implications for physics data mining...", claimList: [{ text: "Cross-domain LLM extraction generalizes to hep-ph corpora with 82% recall", confidence: "HIGH" }] },
  { source: "arXiv", category: "cs.CL", title: "Co-LMLM: Continuous-Query Limited Memory Language Models", published: "2026-07-09", claims: 1, bridge: true, url: "https://arxiv.org/abs/2607.09073", abstract: "Co-LMLM introduces a streaming attention scheme suited for continuously arriving scientific literature. We evaluate on a hep-ph benchmark of 12k abstracts...", claimList: [{ text: "Streaming attention improves recall on hep-ph literature 3.1×", confidence: "HIGH" }] },
  { source: "OpenAlex", category: "Machine learning", title: "Feature Importance in SiC PVT Processes through ML", published: "2026-07-09", claims: 1, bridge: false, url: "https://openalex.org/W4312003", abstract: "Random-forest analysis identifies dominant process parameters governing silicon-carbide physical vapor transport growth...", claimList: [{ text: "Temperature gradient is the top-1 feature (Gini importance 0.34)", confidence: "MEDIUM" }] },
  { source: "OpenAlex", category: "Perception", title: "Technology-Enhanced Writing Pedagogy for EFL Learners", published: "2026-07-09", claims: 1, bridge: false, url: "https://openalex.org/W4312004", abstract: "A mixed-methods study of AI-assisted writing scaffolds in EFL university classrooms...", claimList: [{ text: "Automated feedback improved revision depth in 64% of participants", confidence: "LOW" }] },
];

export const claimTypeDist = [
  { type: "HEP_LITERATURE", count: 28 },
  { type: "CS_HEP_BRIDGE", count: 14 },
  { type: "ANOMALY_FLAGGED", count: 5 },
];

export type EvidenceRow = {
  claim: string;
  status: "Supported" | "Sanity Checked" | "Proposed" | "Rejected";
  nextGate: string;
  run: string;
  narrative: string;
};

export const evidence: EvidenceRow[] = [
  { claim: "Jüttner 1c model gives χ²/ndf >> 1 across all bins at 13 TeV", status: "Supported", nextGate: "—", run: "2026-07-09-jacobian-fix", narrative: "All 10 multiplicity bins fitted with Jüttner 1c yield χ²/ndf in the range 68–227, far above the acceptance threshold of 5. This is reproducible across three independent seeds." },
  { claim: "Jacobian dy/dη missing from manuscript_component_scalar", status: "Supported", nextGate: "—", run: "2026-07-09-jacobian-fix", narrative: "Direct diff of the manuscript source vs the fitting code confirmed the Jacobian was applied in code but omitted from the written derivation. Patch committed." },
  { claim: "T-β degeneracy: ρ(T,β) > 0.9 in high-multiplicity bins", status: "Sanity Checked", nextGate: "Full covariance scan across all bins needed", run: "2026-07-09-jacobian-fix", narrative: "Correlation observed in bin 61-70 (ρ=0.97) and reproduced in bins 71-80, 81-90. Need systematic scan before publishing." },
  { claim: "PySR independently recovers threshold at m ≈ 136 MeV (pion mass)", status: "Sanity Checked", nextGate: "Rerun PySR with 5-fold cross-validation", run: "pysr-run-2026-07-04", narrative: "Symbolic regression converged on a functional form with a break-scale at 136 MeV in 4/5 seeds. Awaiting cross-validated confirmation." },
  { claim: "Bose-Einstein denominator improves χ²/ndf over Boltzmann", status: "Proposed", nextGate: "Run bose_1c head-to-head against Tsallis 2c", run: "—", narrative: "Preliminary single-bin tests are promising but a full 10-bin comparison against Tsallis 2c baseline is pending." },
  { claim: "Multiplicity dependence captured by effective temperature T(N)", status: "Proposed", nextGate: "Fit T vs N_ch across all bins, check monotonicity", run: "—", narrative: "T appears to rise with N_ch monotonically in the Tsallis 2c fits, but no formal test yet." },
];

export type Task = {
  id: string;
  title: string;
  description: string;
  priority: "HIGH" | "MEDIUM" | "LOW";
  assignee: "RB" | "AI";
  date: string;
  citation?: string;
  status: "active" | "blocked" | "proposed";
};

export const tasks: Task[] = [
  { id: "t1", title: "Run bose_1c head-to-head vs Tsallis 2c", description: "Fit the corrected Bose-Einstein formula across all 10 multiplicity bins and compare AIC/BIC against Tsallis 2c baseline.", priority: "HIGH", assignee: "AI", date: "2026-07-09", status: "active" },
  { id: "t2", title: "Regenerate Table 1 with χ²/ndf and uncertainties", description: "Produce a publication-ready replacement for manuscript Table 1 including all validated models.", priority: "HIGH", assignee: "AI", date: "2026-07-09", status: "active" },
  { id: "t3", title: "Write thesis chapter 04_ai_methodology", description: "Document the multi-agent pipeline, fitting architecture, and OpenAlex integration.", priority: "MEDIUM", assignee: "RB", date: "2026-07-08", status: "active" },
  { id: "t4", title: "Enable Ollama LLM extraction", description: "Replace mock extraction_engine with real LLM calls. Blocked: Ollama endpoint not configured.", priority: "MEDIUM", assignee: "AI", date: "2026-07-07", status: "blocked" },
  { id: "t5", title: "Scite.ai citation lookup integration", description: "Query Scite for each claim's supporting literature. Blocked: API key not in environment.", priority: "LOW", assignee: "AI", date: "2026-07-06", status: "blocked" },
  { id: "t6", title: "Full covariance scan: ρ(T,β) correlation across all bins", description: "Triggered by observation: ρ(T,β) = 0.97 in bin 61-70 (above 0.9 threshold). Proposed action: systematically compute off-diagonal covariance for all bin/model combinations.", priority: "HIGH", assignee: "AI", date: "2026-07-09", citation: "Lafferty & Wyatt (1995) — NIM A355", status: "proposed" },
];

export type Agent = {
  name: string;
  status: "ACTIVE" | "IDLE" | "WAITING";
  last: string;
  summary: string;
  log: string[];
};

export const agents: Agent[] = [
  {
    name: "Fit Agent",
    status: "IDLE",
    last: "2026-07-09 18:03",
    summary: "Completed fit_quality scan for run 2026-07-09-jacobian-fix. 10 bins × 1 model.",
    log: [
      "[18:03:12] Run 2026-07-09-jacobian-fix complete: 10 bins × 3 models",
      "[18:02:45] Fit bin 126-150 / Bose-Einstein 1c: χ²/ndf = 1.11, converged",
      "[18:02:31] Fit bin 101-125 / Tsallis 2c: χ²/ndf = 1.5, converged",
      "[18:01:59] Fit bin 61-70 / Jüttner 1c: χ²/ndf = 227.22, POOR (parameter β at boundary 0.993)",
      "[18:01:12] Loading data: bin 21-30 (28347 tracks) OK",
    ],
  },
  {
    name: "Ingest Agent",
    status: "IDLE",
    last: "2026-07-09 18:03",
    summary: "Fetched 2 arXiv (hep-ph) + 2 OpenAlex papers. arXiv API returned 503 for cs query, fallback used.",
    log: [
      "[18:03:02] OpenAlex intake complete: 4 papers, 4 claims extracted",
      "[18:02:44] arXiv query 'cat:cs.CL' → 503 Service Unavailable, retrying cached window",
      "[18:02:31] arXiv query 'cat:hep-th' → 200, 1 paper",
      "[18:02:19] arXiv query 'cat:astro-ph.HE' → 200, 1 paper",
      "[18:02:01] Ingest cycle started (dual-source: arXiv + OpenAlex polite pool)",
    ],
  },
  {
    name: "Thesis Writer",
    status: "IDLE",
    last: "2026-07-09 17:30",
    summary: "Updated abstract in main.tex. Awaiting bose_1c results before writing chapter 05.",
    log: [
      "[17:30:11] Wrote 03_literature_review.tex (2871 words)",
      "[17:29:44] Regenerated abstract with jacobian-fix results",
      "[17:28:03] Compiling latex/main.tex → OK (147 pages)",
      "[17:27:19] Pulling latest evidence-ledger snapshot",
      "[17:27:01] Thesis writer session start",
    ],
  },
  {
    name: "Evidence Monitor",
    status: "ACTIVE",
    last: "2026-07-09 18:05",
    summary: "Scanning covariance matrices for new ρ > 0.9 anomalies...",
    log: [
      "[18:05:02] Scanning bin 91-100 / Jüttner 1c covariance …",
      "[18:04:41] Bin 81-90 / Jüttner 1c: ρ(T,β) = 0.94 → flagged",
      "[18:04:19] Bin 71-80 / Jüttner 1c: ρ(T,β) = 0.95 → flagged",
      "[18:04:01] New proposed task queued for Robert approval",
      "[18:03:47] Ledger sync: 3 supported, 8 sanity-checked, 2 proposed",
    ],
  },
];

export const activityFeed = [
  { color: "emerald", time: "18:03", text: "OpenAlex intake complete. 4 new papers ingested." },
  { color: "cyan", time: "17:58", text: "Fit run 2026-07-09-jacobian-fix completed. 10 bins × 3 models." },
  { color: "amber", time: "17:45", text: "Agent proposed 1 new task: \"Run bose_1c head-to-head with Tsallis\"" },
  { color: "rose", time: "17:30", text: "arXiv API returned HTTP 503 — fallback to cached results." },
  { color: "emerald", time: "17:20", text: "Evidence ledger updated: Jacobian correction marked Supported." },
  { color: "cyan", time: "17:10", text: "PySR symbolic regression run complete. Threshold at m≈136 MeV." },
  { color: "amber", time: "16:55", text: "New claim flagged: \"ρ(T, β) = 0.97 in bin 61-70\"" },
  { color: "emerald", time: "16:30", text: "Thesis chapter 03_literature_review.tex auto-generated." },
];
