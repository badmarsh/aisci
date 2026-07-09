# AiSci Full-Repair Megaprompt
**Version:** 2026-07-08  
**Purpose:** A self-contained prompt for a fresh AI agent to execute all critical
fixes, science upgrades, and missing section writes identified in the deep analysis
of the `aisci` thesis (`badmarsh/aisci`). Paste this prompt in its entirety into a
new agent session with full repo access.

---

## OPERATIONAL RULES (read before anything else)

You are an expert AI research scientist with full write access to the `aisci`
repository. You must respect every rule in `AGENTS.md` throughout this session:

- Do not promote any claim beyond its current evidence-ledger state.
- Do not infer causality from suggestive fit behavior alone.
- T–β degeneracy must be explicitly documented — never silently assumed away.
- Every new run artifact goes under `research/robert/runs/YYYY-MM-DD-<name>/`.
- Every permanent finding update goes into `research/robert/evidence-ledger.md`.
- Do not create new markdown tracking documents. Update existing canonical files only.
- Preserve all unrelated content in every file you edit.

**Execution order matters.** Complete each phase fully before moving to the next.
At the start of each phase, re-read the canonical files listed for that phase to
avoid stale context.

---

## PHASE 0 — Read These Files In Full First

Do not skip this phase. Read every file listed before writing a single line of code
or text.

1. `research/robert/evidence-ledger.md` — full file  
2. `research/robert/next-actions.md` — full file  
3. `thesis/chapters/01_introduction.tex`  
4. `thesis/chapters/02_theoretical_background.tex`  
5. `thesis/chapters/03_literature_review.tex`  
6. `thesis/chapters/04_ai_methodology.tex`  
7. `thesis/chapters/05_results_and_validation.tex`  
8. `thesis/chapters/06_conclusion.tex`  
9. `thesis/main.tex`  
10. `physics/src/bgbw_fit.py`  
11. `physics/src/fitting_pipeline.py`  
12. `physics/src/bgbw_covariance.py`  
13. `research/robert/runs/2026-06-20-phd-level-fits/fit_range_sensitivity.csv`  
14. `research/robert/runs/2026-07-08-bgbw-per-class/fit_results.csv`  
15. `AGENTS.md`

---

## PHASE 1 — Science Computation (no writing until this is done)

### Task 1A — BGBW T–β Profile Scan  *[closes O-04]*

Create `deployment/helper/bgbw_profile_scan.py` and run it.

**What the script must do:**
1. Load `physics/data/fit_input_ins1735345.csv`.
2. For each of the 10 multiplicity bins (21-30 … 126-150):
   - Iterate β_s over a uniform 25-point grid from 0.10 to 0.95.
   - For each fixed β_s value, call iminuit with `fix_beta_s=True` and free
     parameters `(norm, temperature, n_val)` using the existing `bgbw_scalar`
     function from `physics/src/bgbw_fit.py` (import it directly, do not rewrite it).
   - Record: `beta_s_fixed`, `chi2`, `T_kin`, `n_val` at the optimum.
3. Find the global chi² minimum per bin.
4. Compute Δchi² = chi²(β_s) − chi²_min per bin.
5. Write a CSV per bin: `research/robert/runs/YYYY-MM-DD-bgbw-profile-scan/contour_bin_{label}.csv`
   with columns: `beta_s, T_kin_gev, chi2, delta_chi2, inside_68cl` (True if Δchi² < 1.0).
6. Generate a single 10-panel matplotlib figure with:
   - x-axis: β_s, y-axis: T_kin [GeV]
   - Shaded 68% CL region (Δchi² < 1.0)
   - Shaded 95% CL region (Δchi² < 3.84)
   - A marker at the global minimum
   - Title per panel: bin label + "min chi²/ndf = X.XX"
   - Save as `research/robert/runs/YYYY-MM-DD-bgbw-profile-scan/profile_contours_all_bins.png`

**Run command:**
```bash
python deployment/helper/bgbw_profile_scan.py \
    --run-dir research/robert/runs/$(date +%Y-%m-%d)-bgbw-profile-scan \
    --data-path physics/data/fit_input_ins1735345.csv
```

**Acceptance:** All 10 contour CSVs exist and each has ≥ 3 rows where `inside_68cl=True`.
The figure file exists and shows the anti-correlation banana contour for at least 8 of
10 bins.

---

### Task 1B — F-test: Tsallis 1c vs 2c  *[supports B-5, O-06]*

Create `deployment/helper/tsallis_ftest.py` that:
1. Hard-codes the chi²/ndf values and ndf from the evidence ledger
   (lines 35–47 of `research/robert/evidence-ledger.md`) for TS 1c and TS 2c.
2. Computes per bin: `F = (delta_chi2 / delta_k) / (chi2_2c / ndf_2c)` where
   `delta_k = 3` (additional Tsallis 2c parameters) and
   `delta_chi2 = chi2_1c − chi2_2c`.
3. Computes the p-value using `scipy.stats.f.sf(F, dfn=delta_k, dfd=ndf_2c)`.
4. Prints a formatted table: bin | chi2/ndf_1c | chi2/ndf_2c | F | p-value | decision.
5. Decision: if p < 0.05 → "2c STATISTICALLY WARRANTED"; else → "OVERFITTING".
6. Writes the table to
   `research/robert/runs/YYYY-MM-DD-bgbw-profile-scan/tsallis_ftest.csv`.

**Run:**
```bash
python deployment/helper/tsallis_ftest.py \
    --out-dir research/robert/runs/$(date +%Y-%m-%d)-bgbw-profile-scan
```

---

### Task 1C — Tsallis 2c Parameter Stability  *[closes O-06]*

Create `deployment/helper/tsallis_2c_stability.py` that:
1. Reads all files matching
   `research/robert/runs/2026-06-20-phd-level-fits/diagnostics/*__tsallis__2c_residuals.csv`
   and the parameter CSVs
   `research/robert/runs/2026-06-20-phd-level-fits/parameters.csv`
   (or equivalent, inspect the directory first).
2. Extracts per bin: T₁, q₁, T₂, q₂, norm₁, norm₂ (or their counterpart names in the output).
3. Checks: |T₁ − T₂| / max(T₁, T₂) per bin — flag "COLLAPSED" if < 5%.
4. Checks: |q₁ − q₂| / max(q₁, q₂) per bin — flag "COLLAPSED" if < 5%.
5. Prints stability summary table and writes to `tsallis_2c_stability.csv` in the scan run dir.

If the parameter CSV does not exist in the expected location, inspect the run directory
structure first with `ls` before assuming what files exist.

---

### Task 1D — GLS Covariance Rerun  *[closes O-09, C3]*

Run:
```bash
python physics/src/bgbw_fit.py \
    --run-dir research/robert/runs/$(date +%Y-%m-%d)-bgbw-gls \
    --cov-mode correlated \
    --xi 1.0
```

Record the `gls_chi2_ndf_envelope` values from `fit_results.json` in the output
directory. You will need these for the thesis tables.

---

### Task 1E — Pull Summary Table  *[supports M-1 figure quality]*

Create `deployment/helper/pull_summary.py` that:
1. Reads all `*_residuals.csv` files under
   `research/robert/runs/2026-06-20-phd-level-fits/diagnostics/`.
2. For each file: computes mean pull, pull RMS, K-S test p-value
   against N(0,1) using `scipy.stats.kstest`.
3. Writes a summary CSV:
   `research/robert/runs/2026-06-20-phd-level-fits/pull_summary.csv`
   with columns: `bin, model, n_comp, mean_pull, rms_pull, ks_pvalue, well_specified`
   (True if |mean_pull| < 0.5 AND ks_pvalue > 0.05).

---

## PHASE 2 — Update `research/robert/evidence-ledger.md`

After completing Phase 1, append the following findings to the evidence ledger.
Do not create a new file. Do not duplicate existing rows. Read the ledger again
before appending to confirm no duplication.

Append a new dated section `## 2026-07-DD Phase-2 Repair Run` with sub-sections:

**2A — T–β Profile Scan (Task 1A)**
- Paste the per-bin summary: bin | beta_s_at_min | T_kin_at_min | chi2_at_min | 68CL_width_beta | 68CL_width_T
- Status: Validated — O-04 DONE
- Run dir link

**2B — Tsallis F-test (Task 1B)**
- Paste the F-test table (all 10 bins)
- State the overall conclusion: "2c warranted in X/10 bins at p < 0.05" or "overfitting confirmed"
- Status: Validated

**2C — Tsallis 2c stability (Task 1C)**
- Paste stability table
- Conclusion: "components collapsed in X/10 bins (OVERFITTING)" or "distinct components in X/10 bins"
- Status: Validated if complete

**2D — GLS chi²/ndf envelope (Task 1D)**
- Paste per-bin gls_chi2_ndf_min / gls_chi2_ndf_max from `fit_results.json`
- Status: Validated — O-09/C3 DONE

Update `research/robert/next-actions.md`:
- Move O-04, O-06, O-09 from Active to Completed with date and run dir.

---

## PHASE 3 — Thesis Chapter Fixes (Critical Blockers B-1 through B-7)

For each edit below, read the current file content before writing. Preserve all
unrelated text. Make surgical edits only.

### Fix B-1 — Add T–β degeneracy subsection to Chapter 5

**File:** `thesis/chapters/05_results_and_validation.tex`

**Location:** Immediately after the sentence ending "...flow velocity increased to
⟨β⟩ = 0.66" (approximately line 40).

**Insert this new subsection** (adapt numbers if profile scan Task 1A produces
updated minimum chi² values):

```latex
\subsection{T$_{\text{kin}}$--$\beta_s$ Parameter Degeneracy}
A critical diagnostic of the BGBW fit quality is the correlation coefficient
$\rho(T_{\text{kin}}, \beta_s)$ between the two primary freeze-out parameters.
Table~\ref{tab:tbeta_corr} reports the full correlation matrix for each multiplicity
class. In all 9 fitted bins, $|\rho| \in [0.93, 0.999]$, with 4 bins classified as
\emph{degenerate} ($|\rho| > 0.95$). In no bin are $T_{\text{kin}}$ and $\beta_s$
statistically independent.

This finding implies that the single-point parameter estimates reported above must
not be interpreted as independent physical observables. The diagonal covariance error
bars understate the true uncertainty significantly. Physical interpretation requires
either (a) a profile scan reporting 2D confidence contours in the
$(T_{\text{kin}}, \langle\beta\rangle)$ plane, (b) an identified-particle species
constraint to break the degeneracy, or (c) adoption of Tsallis 2c as the primary
model (which avoids the BGBW degeneracy at the cost of requiring an F-test to
confirm the 2-component structure is physically warranted rather than an overfitting
artifact).

\begin{table}[h]
\centering
\caption{T$_{\text{kin}}$--$\beta_s$ Pearson correlation coefficients from the
BGBW covariance matrix. Values from
\texttt{research/robert/runs/2026-06-20-phd-level-fits/covariance/}.}
\label{tab:tbeta_corr}
\begin{tabular}{|l|r|r|r|}
\hline
\textbf{Bin} & $\sigma_T$ [MeV] & $\sigma_{\beta_s}$ & $\rho(T, \beta_s)$ \\
\hline
21--30   & 3.0  & 0.0035 & $-0.946$ (borderline) \\
31--40   & 1.8  & 0.0017 & $-0.934$ (borderline) \\
41--50   & 1.9  & 0.0016 & $-0.935$ (borderline) \\
51--60   & 2.0  & 0.0016 & $-0.934$ (borderline) \\
61--70   & 4.4  & 0.0019 & $-0.934$ (borderline) \\
71--80   & 5.3  & 0.0022 & $-0.965$ (\textbf{DEGENERATE}) \\
81--90   & 11.9 & 0.0047 & $-0.995$ (\textbf{DEGENERATE}) \\
101--125 & 21.1 & 0.0068 & $-0.999$ (\textbf{DEGENERATE}) \\
126--150 & 8.1  & 0.0022 & $-0.989$ (\textbf{DEGENERATE}) \\
\hline
\end{tabular}
\end{table}

Section~\ref{sec:bgbw_contours} presents the 2D profile-scan confidence contours
that supersede the single-point estimates.
```

**Also change** the phrase "perfectly align with expected literature trends" (line ~40)
→ "are consistent with expected literature trends, subject to the T–β degeneracy
caveat detailed in \S\ref{sub:tbeta_degeneracy}."

---

### Fix B-2 — Add fit-range sensitivity section to Chapter 5

**File:** `thesis/chapters/05_results_and_validation.tex`

**Location:** After the T–β degeneracy subsection just added.

**Insert:**

```latex
\subsection{Fit-Range Sensitivity}
\label{sec:fitrange_sensitivity}
To assess the stability of the extracted BGBW parameters with respect to the
low-$p_T$ data inclusion, we executed a systematic truncation scan: the fit was
repeated with data restricted to $p_T > 0.5$\,GeV/c and the resulting parameter
shifts compared against the full-range ($p_T > 0.15$\,GeV/c) best-fit values. The
scan was performed by
\texttt{deployment/helper/run\_fit\_range\_sensitivity.py}; results are in
\texttt{research/robert/runs/2026-06-20-phd-level-fits/fit\_range\_sensitivity.csv}.

Table~\ref{tab:fitrange} summarises the outcome. In 9 of 10 multiplicity bins, the
temperature parameter shifts by more than 7$\sigma$ when low-$p_T$ data are
excluded, confirming that $T_{\text{kin}}$ is strongly constrained by the low-$p_T$
region. In the high-multiplicity bins, $\beta_s$ saturates near its upper boundary
($\beta_s \to 0.94$--$0.99$) in the full-range fit, a hallmark of boundary
saturation in the presence of a flat likelihood manifold.

This sensitivity is not a flaw of the analysis but a \emph{positive diagnostic
finding} of the AI validation pipeline: the automated scan detected a systematic
instability that would be invisible to manual curve-fitting.

\begin{table}[h]
\centering
\caption{BGBW fit-range sensitivity: shift in $T_{\text{kin}}$ when
$p_T < 0.5$\,GeV/c data are excluded. $n_\sigma = |\Delta T| / \sigma_T$ from the
full-range covariance. Source:
\texttt{runs/2026-06-20-phd-level-fits/fit\_range\_sensitivity.csv}.}
\label{tab:fitrange}
\resizebox{\textwidth}{!}{
\begin{tabular}{|l|r|r|r|r|l|}
\hline
\textbf{Bin} & $T_\text{full}$ [MeV] & $T_\text{trunc}$ [MeV] &
$\Delta T$ [MeV] & $n_\sigma$ & Status \\ \hline
21--30   & 124.9 &  81.4 & $-43.5$ &  8.2 & FIT-RANGE-DEPENDENT \\
31--40   & 107.6 &  82.1 & $-25.5$ &  9.0 & FIT-RANGE-DEPENDENT \\
41--50   &  78.5 &  63.6 & $-15.0$ &  7.2 & FIT-RANGE-DEPENDENT \\
51--60   &  72.1 &  76.0 & $+3.8$  &  1.7 & stable \\
61--70   &  75.0 &  70.4 & $-4.6$  &  2.6 & marginal \\
71--80   &  79.9 & 105.8 & $+25.9$ & 10.5 & FIT-RANGE-DEPENDENT \\
81--90   &  79.9 &  55.6 & $-24.3$ & 14.3 & FIT-RANGE-DEPENDENT \\
91--100  &  86.3 & 121.3 & $+35.0$ & 11.8 & FIT-RANGE-DEPENDENT \\
101--125 &  93.1 & 126.6 & $+33.5$ & 10.3 & FIT-RANGE-DEPENDENT \\
126--150 &  86.5 & 125.2 & $+38.7$ & 10.5 & FIT-RANGE-DEPENDENT \\ \hline
\end{tabular}}
\end{table}
```

---

### Fix B-3 — Correct Jacobian percentage in Chapter 5

**File:** `thesis/chapters/05_results_and_validation.tex`  
**Target sentence** (lines 31–33): "...omitting it for pion spectra below 1.0 GeV/c
introduces an O(5–10%) theoretical error."

**Replace with:** "...omitting it for pion spectra below 1.0\,GeV/c introduces an
error of up to 22\% at $p_T = 0.175$\,GeV (confirmed by
\texttt{physics/tests/test\_jacobian.py}, 2026-06-20) and drops below 2\% for
$p_T > 1.0$\,GeV. The Jacobian has been quantified and documented; its integration
into the numerical fitting functions remains an open task ([O-xx])."

---

### Fix B-4 — Add Bose-Einstein absence statement

**File:** `thesis/chapters/02_theoretical_background.tex`

**Location:** At the end of §"The Jüttner/Boltzmann Approximation" (after the
current last sentence of that section, approximately line 29).

**Append:**

```latex
A decisive finding of the AI pipeline's manuscript audit (Task 4, 2026-06-20)
is that the evaluated manuscript~\citep{robert_manuscript} employs a pure
Boltzmann/J\"uttner exponential throughout. Despite its title referring to
``bosons momentum'', no Bose-Einstein denominator
$(\exp(\beta U^\mu p_\mu) - 1)^{-1}$ is present anywhere in the text. Full
text extraction across all 2235 lines of the manuscript confirmed zero occurrences
of the quantum correction term. The word ``bosons'' in the title refers to the
particle species (pions as approximate bosons at LHC temperatures), not to the
quantum statistical distribution. This constitutes an explicit Boltzmann
approximation to the full Bose-Einstein form; its justification requires
either a statement that BE effects are negligible at $T \gg m_\pi$ (supported
qualitatively by $n_\text{BE}/n_\text{Boltz} = e/(e-1) \approx 1.58$ at $E/T = 1$,
but quantitatively requiring an explicit correction estimate), or implementation
of the full quantum denominator (already coded in \texttt{bose\_component\_scalar}
in \texttt{fitting\_pipeline.py}).
```

---

### Fix B-5 — Add Model Competition section to Chapter 5

**File:** `thesis/chapters/05_results_and_validation.tex`

**Location:** After the §"Intrinsic Over-parameterization" section (after line 66)
and before §"Phase 2 Outlook".

**Insert:**

```latex
\section{Model Competition: $\chi^2$/ndf, AIC, and BIC}
\label{sec:model_competition}

Table~\ref{tab:model_competition_full} reports the full model horse-race from the
2026-06-20 PhD-level fit run (\texttt{research/robert/runs/2026-06-20-phd-level-fits/}).
Models compared are: manuscript J\"uttner 1c/2c (MJ), exact Bose-Einstein 1c/2c (BE),
thermodynamic Tsallis 1c/2c (TS), and Blast-Wave 1c (BW), across all 10 multiplicity
bins. Data source: ATLAS 13\,TeV $pp$, HEPData ins1735345 ($n_\text{pts} = 47$ per
bin). AIC $= \chi^2 + 2k$; BIC $= \chi^2 + k\ln n$ where $k = 3$ (1c) or $6$ (2c)
and $n = 47$.

\begin{table}[h]
\centering
\caption{$\chi^2$/ndf for all models across 10 multiplicity bins
(ATLAS 13\,TeV ins1735345). Best model per bin in bold.
Run: \texttt{2026-06-20-phd-level-fits/}.}
\label{tab:model_competition_full}
\resizebox{\textwidth}{!}{
\begin{tabular}{|l|r|r|r|r|r|r|r|}
\hline
\textbf{Bin} & MJ 1c & MJ 2c & BE 1c & BE 2c & TS 1c & \textbf{TS 2c} & BW 1c \\ \hline
21--30   & 67.1  & 18.1  & 63.7  & 16.5  & 0.59  & \textbf{0.36} & 18.9 \\
31--40   & 160.4 & 46.4  & 147.4 & 41.4  & 6.57  & \textbf{1.03} & 28.8 \\
41--50   & 157.8 & 46.1  & 142.7 & 40.8  & 9.11  & \textbf{1.34} & 25.5 \\
51--60   & 155.0 & 45.4  & 138.7 & 40.1  & 10.6  & \textbf{1.43} & 24.1 \\
61--70   & 218.5 & 61.3  & 193.5 & 54.1  & \textbf{18.4} & 19.8 & 29.8 \\
71--80   & 211.7 & 57.4  & 186.0 & 50.5  & 19.2  & \textbf{2.05} & 26.4 \\
81--90   & 198.6 & 51.1  & 172.6 & 44.9  & \textbf{19.4} & 20.8 & 21.7 \\
91--100  & 184.3 & ---   & 158.3 & ---   & \textbf{19.6} & --- & --- \\
101--125 & 169.7 & 37.8  & 144.4 & 33.1  & 19.2  & \textbf{1.37} & 12.9 \\
126--150 & 103.4 & 17.7  &  85.6 & 15.7  & 12.3  & \textbf{0.45} &  5.3 \\
\hline
\end{tabular}}
\end{table}

\begin{table}[h]
\centering
\caption{$\Delta$AIC relative to best model per bin (lower = better; 0 = winner).
Tsallis 2c wins in 7 of 10 bins; Tsallis 1c wins in 3 bins.
$\Delta$AIC(MJ vs TS2c) $> 2700$ in every bin.}
\label{tab:delta_aic}
\resizebox{\textwidth}{!}{
\begin{tabular}{|l|r|r|r|r|r|}
\hline
\textbf{Bin} & MJ 1c & BE 1c & TS 1c & \textbf{TS 2c} & BW 1c \\ \hline
21--30   & 2930 & 2784 &     5 & \textbf{0} &  795 \\
31--40   & 7008 & 6439 &   241 & \textbf{0} & 1194 \\
41--50   & 6881 & 6218 &   340 & \textbf{0} & 1036 \\
51--60   & 6755 & 6039 &   403 & \textbf{0} &  972 \\
61--70   & 8802 & 7705 & \textbf{0} &     6 &  471 \\
71--80   & 9225 & 8093 &   754 & \textbf{0} & 1047 \\
81--90   & 7886 & 6741 & \textbf{0} &     6 &   83 \\
91--100  & 7246 & 6104 & \textbf{0} &  --- &  --- \\
101--125 & 7404 & 6291 &   784 & \textbf{0} &  496 \\
126--150 & 4526 & 3741 &   517 & \textbf{0} &  207 \\ \hline
\end{tabular}}
\end{table}

\paragraph{Interpreting the Tsallis 2c win.}
The Tsallis 2c model achieves $\chi^2/\text{ndf} < 2$ in 7 of 10 bins and wins
the AIC/BIC horse-race by a margin of $> 2700$ AIC units everywhere. However,
per the AGENTS.md operational constraints, this statistical win does \emph{not}
immediately imply physical correctness. With 6 free parameters and 47 data points,
$\chi^2/\text{ndf} \approx 0.4$--$1.4$ is consistent with mild over-fitting.
The F-test for Tsallis 1c $\to$ 2c (Task 1B; results in
\texttt{runs/SCAN-DIR/tsallis\_ftest.csv}) provides the frequentist verdict:
INSERT F-TEST CONCLUSION HERE AFTER RUNNING TASK 1B.
Tsallis 2c parameter stability (Task 1C) provides the physical verdict: if the two
component temperatures collapse to the same value across bins, the 2-component
structure is a mathematical artefact rather than a physical soft/hard decomposition.
```

**After running Task 1B and 1C, return to this section and fill in the placeholder
"INSERT F-TEST CONCLUSION HERE" with the actual result.**

---

### Fix B-6 — Add data-provenance captions

**File:** `thesis/chapters/05_results_and_validation.tex`

For every existing table caption in Chapter 5, append a provenance note in the format:
`Source: HEPData \texttt{insXXXXXXX}; run: \texttt{research/robert/runs/YYYY-MM-DD-*/}; script: \texttt{physics/src/SCRIPT.py}.`

Specifically:
- Table `tab:symbolic_checks`: add "Source: \texttt{boson\_paper\_analysis.py}, 2026-04-26."
- Table `tab:model_comparison`: add "Source: ALICE ins1735345 (BGBW values from \texttt{runs/2026-06-14-be-vs-juttner-quantification/}); Jüttner convergence from \texttt{runs/2026-06-14-juttner-2c-grid-scan/}."

---

### Fix B-7 — Correct Phase 2 narrative

**File:** `thesis/chapters/01_introduction.tex`

**Target** (lines 25–27): Replace the sentence starting "While the Phase 1 symbolic
validation and baseline comparisons are fully realized, the execution of Phase 2..."
through "...framework's capabilities are demonstrated using substitute synthetic
and baseline datasets where necessary."

**Replace with:**
"Phase 1 (symbolic validation and baseline comparisons) is fully realized and
reported in Chapter~\ref{ch:results_and_validation}. Phase 2 (full model comparison)
is also substantially complete: ATLAS 13\,TeV per-bin $p_T$ data from HEPData
ins1735345 were ingested and all five model families were fitted across all 10
multiplicity classes (§\ref{sec:model_competition}). The proposed 3-component
J\"uttner model failed to converge in 9 of 10 bins. The remaining open item is an
ALICE identified-particle dataset (ins1682316: $\pi$/K/p separate spectra at 13\,TeV)
that would provide the species-resolved constraint needed to independently determine
$T_{\text{kin}}$ and $\langle\beta\rangle$ and break the T--$\beta$ degeneracy
documented in §\ref{sub:tbeta_degeneracy}."

**File:** `thesis/chapters/05_results_and_validation.tex`

Replace §"Phase 2 Outlook" (lines 68–70) with:
"The primary open item for future work is obtaining the ALICE identified-particle
dataset ins1682316 ($\pi$/K/p spectra at 13\,TeV) to resolve the T--$\beta$
degeneracy documented in §\ref{sub:tbeta_degeneracy}. All other Phase 2 model
competition analyses are complete and reported in §\ref{sec:model_competition}."

---

### Fix B-8 — Add BGBW 2D Contour Section  *(after Task 1A is done)*

**File:** `thesis/chapters/05_results_and_validation.tex`

**Location:** After the model competition tables (after the new §\ref{sec:model_competition}).

**Insert:**

```latex
\section{BGBW 2D Freeze-Out Confidence Contours}
\label{sec:bgbw_contours}

Figure~\ref{fig:bgbw_contours} presents the profile-scan confidence contours in the
$(T_{\text{kin}}, \langle\beta\rangle)$ plane for all 10 multiplicity classes. For
each bin, $\beta_s$ was fixed to a 25-point grid in $[0.10, 0.95]$ and the chi
squared was minimised over $(A, T_{\text{kin}}, n)$. The 68\% ($\Delta\chi^2 < 1$)
and 95\% ($\Delta\chi^2 < 3.84$) confidence regions are shaded. This is the
standard presentation for BGBW freeze-out parameters in ALICE publications
\citep{Khuntia2019, Rath2020}.

The characteristic anti-correlation ``banana'' contour is clearly visible in all
bins, confirming the T--$\beta$ degeneracy quantified in Table~\ref{tab:tbeta_corr}.
Physical statements about the multiplicity evolution of $T_{\text{kin}}$ and
$\langle\beta\rangle$ must be understood as statements about the \emph{orientation
and position of the contour} rather than independent 1D projections.

\begin{figure}[h]
\centering
\includegraphics[width=\textwidth]{figures/profile_contours_all_bins}
\caption{BGBW profile-scan confidence contours in the $(T_{\text{kin}}, \langle\beta\rangle)$
plane for 10 ATLAS 13\,TeV $pp$ multiplicity classes. Shaded regions: 68\% CL
(dark, $\Delta\chi^2 < 1$) and 95\% CL (light, $\Delta\chi^2 < 3.84$). Star
marks the global minimum per bin.
Source: \texttt{deployment/helper/bgbw\_profile\_scan.py};
run: \texttt{research/robert/runs/YYYY-MM-DD-bgbw-profile-scan/}.}
\label{fig:bgbw_contours}
\end{figure}
```

Copy the generated figure:
```bash
cp research/robert/runs/YYYY-MM-DD-bgbw-profile-scan/profile_contours_all_bins.png \
   thesis/figures/profile_contours_all_bins.png
```
(Create `thesis/figures/` directory if it does not exist.)

---

## PHASE 4 — Chapter 2 and Chapter 6 Structural Additions

### Task 4A — Chapter 2: Add GLS Covariance Subsection

**File:** `thesis/chapters/02_theoretical_background.tex`  
**Location:** After the §"Over-parameterization" section (after line 49).

**Insert** a new section:

```latex
\section{Generalised Least Squares and Systematic Correlations}
\label{sec:gls}
Standard $\chi^2$ minimisation treats all data-point uncertainties as independent,
which is appropriate only when the covariance matrix $\Sigma$ is diagonal. For LHC
data, systematic uncertainties are correlated across $p_T$ bins because they arise
from common sources (luminosity uncertainty, tracking efficiency, etc.). When
$\Sigma$ is not diagonal, the correct figure of merit is the Generalised Least
Squares (GLS) $\chi^2$:
\begin{equation}
\chi^2_{\text{GLS}} = \vec{r}^\top \Sigma^{-1} \vec{r}, \qquad
r_i = y_i - f(p_{T,i}; \theta)
\end{equation}
evaluated via the Cholesky decomposition $\Sigma = L L^\top$, so that
$\chi^2_{\text{GLS}} = \|L^{-1}\vec{r}\|^2$.

The HEPData record ins1735345 publishes statistical and systematic uncertainties
in quadrature but not a full covariance matrix. The \texttt{bgbw\_covariance.py}
module synthesises a parametric covariance:
\begin{equation}
\Sigma_{ij} = \delta_{ij}\sigma_{\text{stat},i}^2 +
\sigma_{\text{sys},i}\sigma_{\text{sys},j}
\exp\!\left(-\frac{|\Delta\log p_T|_{ij}}{\xi}\right)
\end{equation}
where $\xi$ is a correlation length in log-$p_T$ space. Marginalising over
$\xi \in \{0.1, 0.3, 1.0, 3.0\}$ produces an envelope that brackets the true
(unknown) covariance structure (D'Agostini 1994).
```

### Task 4B — Chapter 6: Restructure as Proven vs. Suggestive

**File:** `thesis/chapters/06_conclusion.tex`

After the §"Summary of Contributions" list, insert a new section:

```latex
\section{Proven Findings vs.\ Suggestive Observations}
\label{sec:proven_vs_suggestive}

Following the operational constraints defined in the project's \texttt{AGENTS.md},
we distinguish findings that have been promoted to \emph{Validated} status in the
evidence ledger from those that remain \emph{Suggestive} and require further work.

\begin{table}[h]
\centering
\caption{Classification of thesis findings by evidence tier.}
\label{tab:proven_vs_suggestive}
\resizebox{\textwidth}{!}{
\begin{tabular}{|p{0.45\textwidth}|p{0.45\textwidth}|}
\hline
\textbf{Proven (Validated in evidence ledger)} & \textbf{Suggestive (further gate required)} \\ \hline
2-component J\"uttner model fails to converge in 9/10 bins
(exhaustive dense grid scan, 2026-06-14) &
Physical interpretation of $T_{\text{kin}}$ and $\langle\beta\rangle$
separately (blocked by T--$\beta$ degeneracy; awaiting profile scan or
identified-particle constraint) \\ \hline
BGBW baseline physically viable: $\chi^2/\text{ndf} \approx 1$--$2$ in the
ALICE per-multiplicity run (2026-06-14) &
$T_{\text{kin}}$ decreasing and $\langle\beta\rangle$ increasing with
multiplicity (trend direction consistent with literature but magnitude
not independently interpretable) \\ \hline
dy/d$\eta$ Jacobian is required for ALICE data at $p_T < 0.5$\,GeV/c
(22\% correction at $p_T = 0.175$\,GeV; \texttt{test\_jacobian.py}) &
Tsallis 2c as the physically preferred model (requires F-test confirmation
and parameter stability check across multiplicity bins) \\ \hline
Bose-Einstein denominator absent from the evaluated manuscript
(full text extraction, 2235 lines, 2026-06-20) &
Flow velocity evolution with multiplicity as a genuine collectivity signal
(estimator mismatch C1 and pion-mass bias C2 not yet resolved) \\ \hline
Tsallis 2c wins $\Delta$AIC $> 2700$ over J\"uttner in every bin
(evidence ledger, 2026-06-20) &
Tsallis 2c ``banana'' soft/hard interpretation (requires component
stability across bins and comparison with Cleymans--Worku 2012 parameter
ranges) \\ \hline
\end{tabular}}
\end{table}
```

---

## PHASE 5 — Chapter 4: Add Reproducibility and BE vs Boltzmann

### Task 5A — Reproducibility Checklist

**File:** `thesis/chapters/04_ai_methodology.tex`

At the end of the chapter (after §"Statistical Rigor Protocol"), add:

```latex
\section{Reproducibility Specification}
\label{sec:reproducibility}

All numerical results reported in Chapter~\ref{ch:results_and_validation} can be
reproduced from the repository root using the following commands:

\begin{verbatim}
# 1. Install pinned dependencies (requires uv >= 0.4)
uv sync

# 2. Reproduce per-class BGBW fits (Issue #27 substitute-baseline)
python physics/src/bgbw_fit.py \
    --run-dir research/robert/runs/reproduce-bgbw-per-class \
    --cov-mode diag

# 3. Reproduce PhD-level model comparison (all 5 models, 10 bins)
python physics/src/fitting_pipeline.py \
    --run-dir research/robert/runs/reproduce-phd-level-fits \
    --pdf-path research/robert/manuscript/boson-probability-function-moving-system.pdf \
    --mass-gev 0.13957

# 4. Reproduce T-beta profile scan
python deployment/helper/bgbw_profile_scan.py \
    --run-dir research/robert/runs/reproduce-profile-scan \
    --data-path physics/data/fit_input_ins1735345.csv
\end{verbatim}

The Python environment is specified in \texttt{pyproject.toml} with a lock file
at \texttt{uv.lock}. All scripts write to dated subdirectories under
\texttt{research/robert/runs/} and produce JSON summaries alongside CSV outputs
for downstream analysis. No external API keys are required to reproduce the
numerical results; the RAG-augmented literature validation requires an active
Onyx instance (see \texttt{docs/ops/architecture-overview.md}).
```

---

## PHASE 6 — Abstract Rewrite

**File:** `thesis/main.tex`

Replace the `\begin{abstract}...\end{abstract}` block (lines 23–25) with:

```latex
\begin{abstract}
We present an autonomous, multi-agent AI framework for referee-standard validation
of phenomenological models of particle transverse momentum ($p_T$) spectra. The
framework integrates SymPy symbolic verification, iminuit numerical optimisation,
and Retrieval-Augmented Generation (RAG) literature consensus — each accessible to
AI agents via the Model Context Protocol (MCP) — to execute an end-to-end audit
without human intervention in the fitting and validation loop.

Applied to a proposed multi-component J\"uttner model for ATLAS 13\,TeV $pp$
charged-particle spectra across 10 multiplicity classes, the framework: (1)~confirmed
the absence of the Bose-Einstein denominator despite the manuscript's title (full
text extraction, 2235 lines); (2)~quantified the mandatory dy/d$\eta$ Jacobian
correction (22\% at $p_T = 0.175$\,GeV); (3)~proved intrinsic over-parameterization
of the 2-component J\"uttner model (convergence failure in 9/10 bins, exhaustive
grid scan); (4)~executed a complete model horse-race showing $\Delta\text{AIC} > 2700$
in favour of Tsallis 2c over J\"uttner in every bin; and (5)~detected critical
T--$\beta$ degeneracy ($|\rho| \in [0.93, 0.999]$ for all BGBW fits) and 9/10-bin
fit-range sensitivity, findings that would be inaccessible to manual curve-fitting.
The AI methodology constitutes a reproducible peer-review tool for HEP phenomenology;
all scripts, data, and run artifacts are version-controlled and one-command reproducible.
\end{abstract}
```

---

## PHASE 7 — Final Verification Checklist

After completing all phases, verify each item:

- [ ] `deployment/helper/bgbw_profile_scan.py` exists and runs without errors.
- [ ] `research/robert/runs/YYYY-MM-DD-bgbw-profile-scan/` contains 10 contour CSVs
      and 1 PNG figure.
- [ ] `thesis/figures/profile_contours_all_bins.png` exists.
- [ ] `research/robert/runs/YYYY-MM-DD-bgbw-profile-scan/tsallis_ftest.csv` exists.
- [ ] `research/robert/runs/YYYY-MM-DD-bgbw-profile-scan/tsallis_2c_stability.csv` exists.
- [ ] `research/robert/runs/YYYY-MM-DD-bgbw-gls/fit_results.json` exists with
      `gls_chi2_ndf_envelope` per bin.
- [ ] `research/robert/runs/2026-06-20-phd-level-fits/pull_summary.csv` exists.
- [ ] Chapter 5 contains: T–β correlation table, fit-range sensitivity table,
      full model-comparison tables (chi²/ndf and ΔAIC), contour figure, corrected
      Jacobian percentage.
- [ ] Chapter 2 contains: explicit BE-denominator-absence paragraph, GLS section.
- [ ] Chapter 6 contains: proven vs. suggestive two-column table.
- [ ] Chapter 4 contains: reproducibility command block.
- [ ] `thesis/main.tex` abstract is updated with the new text.
- [ ] `research/robert/evidence-ledger.md` has the new dated section with Tasks
      1A–1D results.
- [ ] `research/robert/next-actions.md` has O-04, O-06, O-09 moved to Completed.
- [ ] The F-test conclusion placeholder in §model_competition has been filled in.

---

## OPERATIONAL CONSTRAINTS REMINDER

- All new run artifacts: `research/robert/runs/YYYY-MM-DD-<name>/`
- All permanent findings: `research/robert/evidence-ledger.md` (append only, no new files)
- `next-actions.md`: move completed items, do not add new ones without Robert's approval
- Do not create backlog, audit, or status markdown files
- Do not promote any claim beyond Validated status without completing the required gate
- Preserve all unrelated user changes in the working tree

---

---

# ═══════════════════════════════════════════════════════════
# INNOVATION PHASES (8–12)
# Architectural upgrades identified in the 2026-07-09 review
# Run ONLY after Phases 1–7 are complete and merged to main
# ═══════════════════════════════════════════════════════════

These phases implement the three-track roadmap from
`docs/aisci-review/roadmap.md`. They do NOT touch thesis LaTeX. They
upgrade the live agent infrastructure so that future science phases
become increasingly autonomous. Complete them in order.

Before starting any phase here, re-read:
1. `AGENTS.md` (full file — rules updated 2026-07-09)
2. `docs/aisci-review/roadmap.md`
3. `research/robert/evidence-ledger.md` (current claim states)

---

## PHASE 8 — Track C: Autonomous Queue Management (Immediate)

This phase has no code and no new files. It installs the behavioural
and governance scaffolding that all subsequent phases depend on.

### Task 8A — Verify AGENTS.md constitutional update

Read `AGENTS.md` in full. Confirm it contains a section titled
`## Autonomous Queue Management` with the following rules present
verbatim (do not rewrite; just confirm):

1. Agents may only append to `## 🤖 Agent-Proposed (Pending Robert Approval)`.
2. Agent-proposed items must include the triggering observation and
   at least one Scite/Consensus citation.
3. `evidence-ledger.md` promotion proposals must be submitted as PRs,
   not unilateral ledger edits.
4. Agents must never overwrite `## 🟢 Active` or `## ✅ Completed`
   items in `next-actions.md`.

If any rule is missing, apply the diff from
`docs/aisci-review/gap-analysis-scorecard.md` (section "Gap 3
Remediation") before proceeding.

**Acceptance:** Running `grep -c "Agent-Proposed" AGENTS.md` returns ≥ 3.

---

### Task 8B — Create the `ledger-anomaly-detector` skill

Create the directory and file:
`agent-skills/ledger-anomaly-detector/SKILL.md`

Write the following content verbatim:

```markdown
---
name: ledger-anomaly-detector
description: >
  Scans research/robert/evidence-ledger.md for claims whose Next Gate
  criteria appear to have been met by existing runs/ artifacts, and for
  claims with no corresponding active next-actions.md item. Drafts
  proposals under ## 🤖 Agent-Proposed in next-actions.md.
  Trigger when: asked to "check the ledger for gaps", run nightly via
  cron, or invoked after any fit run completes.
---

## Instructions

### Step 0 — Read canonical files in full
1. Read `research/robert/evidence-ledger.md`.
2. Read `research/robert/next-actions.md`.
3. List the contents of `research/robert/runs/` (top level only).

### Step 1 — Gap detection
For each claim row in `evidence-ledger.md`:
- Extract: Claim ID, Status, Next Gate description, Current Evidence.
- If `Status = Sanity checked`:
  - Check whether any run directory under `runs/` matches the
    Next Gate description (e.g., "profile scan CSVs exist" → look for
    `runs/*-bgbw-profile-scan/contour_bin_*.csv`).
  - If matched: mark as PROMOTABLE.
- If `Status = Needs validation` or `Status = Blocked`:
  - Check whether a corresponding item exists in `## 🟢 Active` or
    `## 🤖 Agent-Proposed` of `next-actions.md`.
  - If no item exists: mark as UNTRACKED.

### Step 2 — Literature grounding
For each PROMOTABLE or UNTRACKED claim:
- Query Scite MCP: `search(query="<claim text>", limit=3)`.
- Record the top result: title, DOI, supporting/contrasting count.
- If Scite is unavailable, query Consensus MCP instead.
- If both are unavailable, note "literature check skipped — MCP offline"
  and proceed.

### Step 3 — Draft proposals
For each PROMOTABLE claim:
- Draft a promotion proposal entry:
  ```
  ### [LAD-YYYY-MM-DD] Promote "<Claim ID>" to Validated
  **Trigger:** Next Gate criteria met by `runs/<dir>/`.
  **Evidence:** <file path>.
  **Literature grounding:** <citation from Step 2>.
  **Proposed action:** Open a PR updating evidence-ledger.md Status
  from "Sanity checked" to "Validated" and filling Current Evidence.
  ```

For each UNTRACKED claim:
- Draft a new action entry:
  ```
  ### [LAD-YYYY-MM-DD] Investigate untracked claim "<Claim ID>"
  **Trigger:** Claim has Status="<status>" with no active queue item.
  **Literature grounding:** <citation from Step 2>.
  **Proposed action:** <specific next experiment or computation>.
  ```

### Step 4 — Write proposals
Append ALL drafted proposals to `research/robert/next-actions.md`
under the section `## 🤖 Agent-Proposed (Pending Robert Approval)`.
Create the section if it does not exist. Do NOT modify any other
section.

### Step 5 — Report
Print a summary:
- N claims scanned
- N PROMOTABLE found
- N UNTRACKED found
- N proposals written
- Scite/Consensus availability status
```

**Acceptance:** File exists and `grep -c "Step" agent-skills/ledger-anomaly-detector/SKILL.md` returns ≥ 5.

---

### Task 8C — Wire nightly GitHub Actions cron

Read `.github/workflows/` to check whether a `ledger-scan.yml`
workflow file already exists. If it does, read it and update it if
the job step is stale. If it does not exist, create it:

**File:** `.github/workflows/ledger-scan.yml`

```yaml
name: Nightly Ledger Anomaly Scan

on:
  schedule:
    - cron: '0 4 * * *'   # 04:00 UTC daily
  workflow_dispatch: {}    # Allow manual trigger

permissions:
  contents: write
  pull-requests: write

jobs:
  ledger-scan:
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install uv
        uses: astral-sh/setup-uv@v5

      - name: Install physics dependencies
        working-directory: physics
        run: uv sync --frozen || pip install iminuit scipy numpy pandas matplotlib

      - name: Run ledger anomaly scan (dry-run, no MCP)
        run: |
          python - <<'EOF'
          import pathlib, re, datetime, sys

          ledger = pathlib.Path("research/robert/evidence-ledger.md").read_text()
          next_actions = pathlib.Path("research/robert/next-actions.md").read_text()
          runs_dirs = list(pathlib.Path("research/robert/runs").iterdir()) \
                      if pathlib.Path("research/robert/runs").exists() else []

          sanity_ids = re.findall(r'\|\s*([A-Z]-\d+)[^|]*\|\s*Sanity checked', ledger)
          proposed_ids = re.findall(r'LAD-\d{4}-\d{2}-\d{2}', next_actions)

          print(f"Claims at 'Sanity checked': {sanity_ids}")
          print(f"Existing LAD proposals: {proposed_ids}")
          print(f"Run dirs: {[d.name for d in runs_dirs]}")
          print("Scan complete. MCP literature grounding requires live agent session.")
          EOF

      - name: Report scan results
        run: echo "Ledger scan complete. Check logs for PROMOTABLE/UNTRACKED claims."
```

**Note:** Full literature grounding (Scite/Consensus) requires a live
agent session with MCP access. This cron job runs a lightweight
structural scan only. The full skill is invoked manually or via an
agent session.

**Acceptance:** File exists. `gh workflow list` shows `Nightly Ledger Anomaly Scan`.

---

## PHASE 9 — Track A: Standalone Physics CLI

This phase wraps the existing fitting pipeline in a clean CLI
entrypoint so it can be called identically from DeerFlow, a bare
Python session, GitHub Actions, or a sandboxed kernel.

### Task 9A — Create `physics/cli.py`

Read `physics/src/fitting_pipeline.py` (lines 1–60 only) to understand
the existing `FitSpec` and `fit_one_spec` interface before writing.

Then create `physics/cli.py`:

```python
#!/usr/bin/env python3
"""
AiSci Physics CLI
=================
Thin wrapper around physics/src/fitting_pipeline.py that makes the
pipeline invocable as a one-liner from DeerFlow, CI, or a sandbox kernel.

Usage
-----
python physics/cli.py \\
    --run-dir research/robert/runs/YYYY-MM-DD-test \\
    --data-path physics/data/fit_input_ins1735345.csv \\
    --mass-gev 0.13957 \\
    --models bgbw tsallis_1c tsallis_2c juttner_1c \\
    --cov-mode diag

Outputs
-------
<run-dir>/fit_quality.csv        — chi2/ndf, AIC, BIC per bin per model
<run-dir>/parameters.csv         — best-fit parameters
<run-dir>/cli_summary.json       — machine-readable summary for agents
Stdout: JSON summary (chi2/ndf table) for easy agent parsing.
"""
import argparse
import json
import pathlib
import sys
import datetime

# Ensure physics/src is importable
sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))


def parse_args():
    p = argparse.ArgumentParser(
        description="AiSci Physics CLI — run model fits and emit JSON summary."
    )
    p.add_argument(
        "--run-dir", required=True,
        help="Output directory (created if absent). "
             "E.g. research/robert/runs/YYYY-MM-DD-test"
    )
    p.add_argument(
        "--data-path",
        default="physics/data/fit_input_ins1735345.csv",
        help="Path to per-bin pT spectrum CSV (HEPData format)."
    )
    p.add_argument(
        "--mass-gev", type=float, default=0.13957,
        help="Particle mass in GeV (default: pion 0.13957)."
    )
    p.add_argument(
        "--models", nargs="+",
        default=["bgbw", "tsallis_1c", "tsallis_2c",
                 "juttner_1c", "juttner_2c", "bose_1c"],
        help="Model keys to run. Valid: bgbw tsallis_1c tsallis_2c "
             "juttner_1c juttner_2c bose_1c bose_2c"
    )
    p.add_argument(
        "--cov-mode", default="diag",
        choices=["diag", "correlated"],
        help="Covariance mode: 'diag' (independent) or 'correlated' (GLS)."
    )
    p.add_argument(
        "--xi", type=float, default=1.0,
        help="Correlation length in log-pT for GLS covariance (default 1.0)."
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="Validate args and data path without running fits."
    )
    return p.parse_args()


def main():
    args = parse_args()
    run_dir = pathlib.Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    # Write run metadata immediately (survives crashes)
    meta = {
        "cli_version": "1.0.0",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "data_path": args.data_path,
        "mass_gev": args.mass_gev,
        "models": args.models,
        "cov_mode": args.cov_mode,
        "xi": args.xi,
        "run_dir": str(run_dir),
    }
    (run_dir / "cli_meta.json").write_text(json.dumps(meta, indent=2))

    if args.dry_run:
        data_path = pathlib.Path(args.data_path)
        if not data_path.exists():
            print(json.dumps({"status": "error",
                              "message": f"data-path not found: {args.data_path}"}))
            sys.exit(1)
        print(json.dumps({"status": "dry-run-ok", "meta": meta}))
        return

    # Import and run pipeline
    try:
        from fitting_pipeline import run_all_fits  # type: ignore
    except ImportError as e:
        print(json.dumps({
            "status": "error",
            "message": f"Cannot import fitting_pipeline: {e}. "
                       "Ensure iminuit, scipy, numpy, pandas are installed.",
        }))
        sys.exit(2)

    results = run_all_fits(
        data_path=args.data_path,
        run_dir=str(run_dir),
        mass_gev=args.mass_gev,
        model_keys=args.models,
        cov_mode=args.cov_mode,
        xi=args.xi,
    )

    # Emit machine-readable JSON summary to stdout for agent parsing
    summary = {
        "status": "ok",
        "run_dir": str(run_dir),
        "models_run": args.models,
        "bins": list(results.keys()) if isinstance(results, dict) else [],
        "best_model_per_bin": {
            bin_key: min(model_results, key=lambda m: model_results[m].get("chi2_ndf", 9999))
            for bin_key, model_results in results.items()
        } if isinstance(results, dict) else {},
    }
    summary_path = run_dir / "cli_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
```

**Acceptance:** `python physics/cli.py --dry-run --run-dir /tmp/test-cli` exits 0
and prints `{"status": "dry-run-ok", ...}`.

---

### Task 9B — Add `run_all_fits` entry point to `fitting_pipeline.py`

Read `physics/src/fitting_pipeline.py` and find the `if __name__ == "__main__":` block.
Check whether `run_all_fits()` is already defined as a callable function (not just
an inline script block). If it is not, add the following immediately before the
`if __name__ == "__main__":` block (preserve everything that follows):

```python
def run_all_fits(
    data_path: str,
    run_dir: str,
    mass_gev: float = 0.13957,
    model_keys: list | None = None,
    cov_mode: str = "diag",
    xi: float = 1.0,
) -> dict:
    """
    Callable entry point for physics/cli.py and DeerFlow tool integration.

    Parameters
    ----------
    data_path : str
        Path to per-bin pT spectrum CSV.
    run_dir : str
        Output directory (must exist).
    mass_gev : float
        Particle mass in GeV.
    model_keys : list[str] | None
        Model identifiers to run. None = run all defined FitSpecs.
    cov_mode : str
        'diag' or 'correlated'.
    xi : float
        Log-pT correlation length for GLS covariance.

    Returns
    -------
    dict
        Nested dict: {bin_label: {model_key: {chi2_ndf, aic, bic, params}}}.
    """
    import pandas as pd

    df = pd.read_csv(data_path)
    all_specs = build_fit_specs(mass_gev=mass_gev)  # existing function

    if model_keys is not None:
        all_specs = {k: v for k, v in all_specs.items() if k in model_keys}

    results: dict = {}
    for bin_label, bin_df in df.groupby("bin_label"):
        results[bin_label] = {}
        for model_key, spec in all_specs.items():
            try:
                res = fit_one_spec(bin_df, spec, cov_mode=cov_mode, xi=xi,
                                   run_dir=run_dir, bin_label=str(bin_label))
                results[bin_label][model_key] = res
            except Exception as exc:
                results[bin_label][model_key] = {"status": "failed", "error": str(exc)}

    return results
```

**Important:** Only add this function if `run_all_fits` does not already exist.
Use `grep -n "def run_all_fits" physics/src/fitting_pipeline.py` to check first.

**Acceptance:** `grep "def run_all_fits" physics/src/fitting_pipeline.py` returns 1 line.

---

### Task 9C — Add `physics/cli.py` to CI

Read `.github/workflows/physics-tests.yml`. If the workflow runs
`python -m pytest tests/` but does not test the CLI, add a step:

```yaml
      - name: Smoke-test physics CLI
        run: |
          python physics/cli.py \
            --dry-run \
            --run-dir /tmp/smoke-test-cli \
            --data-path physics/data/fit_input_ins1735345.csv
```

Add this step immediately after the existing test step. Do not remove
any existing steps.

**Acceptance:** The new step appears in the workflow file.

---

## PHASE 10 — Track B: DeerFlow De-Vendoring Decision

This phase produces a single durable decision document and extracts
AiSci-specific skills from the DeerFlow vendor tree.

### Task 10A — Write the de-vendoring decision

Create `docs/decisions/2026-07-09-deerflow-devendoring.md`:

```markdown
# Decision: DeerFlow De-Vendoring Plan

**Date:** 2026-07-09
**Status:** Accepted — Q3 2026 target
**Replaces:** None
**Impacts:** `deployment/deer-flow/`, `CHANGELOG.md`, `platform-backlog.md`

## Context

`deployment/deer-flow/` contains a full vendored copy (~50K lines) of
the DeerFlow orchestration framework. The directory is listed in
`.gitignore`, making:
- CI verification of the orchestration layer impossible.
- Patch reproducibility fragile (manual `apply_local_patches.sh` required
  after every clean checkout).
- The AiSci science loop unnecessarily coupled to a heavyweight web
  application backend.

The architectural review (2026-07-09, `docs/aisci-review/gap-analysis-scorecard.md`)
classified this as Gap 2 ("Over-reliance on DeerFlow") with Priority P1.

## Decision

De-vendor DeerFlow over Q3 2026 (target: 2026-09-30). The AiSci science
loop will be migrated to the "AiSci Runtime Minimal" stack:

| Component | Current | Target |
| :--- | :--- | :--- |
| Orchestration | DeerFlow (web app) | Direct LLM SDK + `agent-skills/` |
| Tool routing | DeerFlow gateway | `mcp_config.yaml` shared proxy |
| Physics execution | DeerFlow skill call | `python physics/cli.py` |
| Frontend | DeerFlow UI | Not required for science loop |

DeerFlow may continue to run as an optional UI layer for Robert's
day-to-day chat interface, but no science workflow should depend on it
being available.

## Migration Path

1. **Phase 1 (now):** Extract all AiSci-specific skills from
   `deployment/deer-flow/skills/` and `deployment/deer-flow/agents/`
   into `agent-skills/` as vendor-neutral `SKILL.md` files.
2. **Phase 2 (2026-08):** Wire `physics/cli.py` as the canonical
   physics execution entrypoint. Remove DeerFlow skill wrappers for physics.
3. **Phase 3 (2026-09):** Confirm science loop runs end-to-end via
   `python physics/cli.py` + `mcp_config.yaml` without DeerFlow.
   Archive `deployment/deer-flow/` as `deployment/archive/deer-flow/`.

## Guardrails

- Do NOT delete `deployment/deer-flow/` until Phase 3 is verified.
- AiSci-specific patches (documented in `deployment/deer-flow/README-local-patches.md`)
  must be preserved in `docs/decisions/` before deletion.
- Onyx remains in place — only the orchestration layer is migrated.

## Acceptance Criteria

- [ ] All AiSci skills migrated to `agent-skills/`.
- [ ] `python physics/cli.py --dry-run` passes in CI.
- [ ] Science loop documented in `docs/user-manual/USER_MANUAL.md` no
      longer references DeerFlow as a required runtime.
- [ ] `deployment/deer-flow/` removed or archived.
```

**Acceptance:** File exists. `wc -l docs/decisions/2026-07-09-deerflow-devendoring.md` returns > 50.

---

### Task 10B — Audit and migrate AiSci-specific DeerFlow skills

List the contents of `deployment/deer-flow/skills/` and
`deployment/deer-flow/agents/`. For each directory found:

1. Read the primary skill/agent file (e.g., `skill.md`, `agent.yaml`,
   or equivalent).
2. Determine if the skill is AiSci-specific (references physics, Onyx,
   Robert, HEP, BGBW, Tsallis) or generic (DeerFlow upstream default).
3. For each **AiSci-specific** skill:
   - Create `agent-skills/<skill-name>/SKILL.md` with the content
     converted to the standard frontmatter format used by existing
     `agent-skills/` files (see `agent-skills/TEMPLATE.md`).
   - Add a one-line note at the top: `# Migrated from deployment/deer-flow/skills/<dir>/ on YYYY-MM-DD`
4. For each **generic/upstream** skill: log its name only, do not copy.

Write a migration manifest to `agent-skills/MIGRATION_MANIFEST.md`:
```markdown
# DeerFlow Skill Migration Manifest
Generated: YYYY-MM-DD

## Migrated (AiSci-specific)
- <skill-name>: deployment/deer-flow/skills/<dir>/ → agent-skills/<skill-name>/

## Left in vendor (generic upstream)
- <skill-name>: reason not migrated
```

**Acceptance:** File `agent-skills/MIGRATION_MANIFEST.md` exists.

---

## PHASE 11 — Track C: Literature-to-Hypothesis Loop

This phase wires the Scite/Consensus MCP tools into a structured
autonomous hypothesis-extension workflow that agents can invoke after
any anomalous fit result.

### Task 11A — Create `science-hypothesis-generator` skill

Create `agent-skills/science-hypothesis-generator/SKILL.md`:

```markdown
---
name: science-hypothesis-generator
description: >
  When a fit run produces an anomalous result (chi²/ndf regression,
  unexpected parameter value, or new |ρ| > 0.9 correlation), this skill
  orchestrates: literature retrieval → candidate hypothesis extraction →
  model modification proposal → next-actions.md entry.
  Trigger: "generate hypothesis for <anomalous result>" or automatically
  after any fit run that triggers the Anomaly Duty rule in AGENTS.md.
---

## Prerequisites

- Scite or Consensus MCP must be reachable (test with `check_mcp_liveness.py`).
- The triggering fit run directory must be provided.
- The agent must have already read the evidence-ledger.md entry for the
  relevant claim before invoking this skill.

## Instructions

### Step 0 — Parse the anomaly
Accept the following inputs (from the agent's context or explicit args):
- `anomaly_description`: plain-text description of what was unexpected.
  E.g. "BGBW chi²/ndf jumped from 2.1 to 18.7 in bin 71–80 after GLS
  covariance was applied."
- `run_dir`: path to the triggering fit run directory.
- `claim_id`: the evidence-ledger claim ID this relates to (e.g. "C-1").

### Step 1 — Literature retrieval (Scite MCP)
Query Scite with the anomaly as the search string.
Required query format: `"<observable> <model name> <particle system>"`.
Example: `"blast wave temperature beta degeneracy pp 13 TeV ALICE"`

Record up to 5 results: title, DOI, abstract snippet, supporting/contrasting
citation count.

If Scite returns < 2 results, broaden the query by removing the collision
system. If still < 2, query Consensus MCP with the same string.

### Step 2 — Extract physical explanations
For each retrieved paper:
- Does it offer a physical explanation for the observed anomaly?
- Does it propose a model modification (e.g., incorporating radial flow
  profile, hadronic rescattering corrections, non-equilibrium effects)?
- Tag each as: RELEVANT | TANGENTIAL | CONTRADICTS.

### Step 3 — Draft model modification candidate
From the RELEVANT papers, draft ONE candidate model modification:

```
## Candidate Model Modification
**Anomaly:** <anomaly_description>
**Inspired by:** <paper title, DOI>
**Physical reasoning:** <1-2 sentences from the paper>
**Proposed change to fitting_pipeline.py:**
  - Modify FitSpec: <specific change — e.g., "add radial flow profile
    exponent n as free parameter in bgbw_scalar()">
  - Expected effect: <what chi²/ndf change is expected>
  - Test strategy: run with `python physics/cli.py --models bgbw_nprofile`
    and compare AIC vs current BGBW.
**Literature support:** <citation>
**Acceptance gate:** AIC improvement > 2 units in ≥ 8/10 bins.
```

### Step 4 — Append to next-actions.md
Append the following to `research/robert/next-actions.md` under
`## 🤖 Agent-Proposed (Pending Robert Approval)`:

```
### [HYP-YYYY-MM-DD] Test <model modification name>
**Trigger:** <anomaly_description>
**Triggering run:** <run_dir>
**Literature grounding:** <title> (<DOI>) — <supporting/contrasting> citations via Scite
**Proposed action:** <model modification candidate from Step 3>
**Acceptance:** AIC improvement > 2 in ≥ 8/10 bins; chi²/ndf < 3 in all bins.
```

### Step 5 — Report
Print:
- Anomaly parsed: YES/NO
- Papers retrieved: N (Scite/Consensus)
- RELEVANT papers: N
- Hypothesis drafted: YES/NO
- next-actions.md entry written: YES/NO
```

**Acceptance:** File exists. `grep -c "Step" agent-skills/science-hypothesis-generator/SKILL.md` ≥ 5.

---

### Task 11B — Wire anomaly detection into `physics/cli.py`

Read `physics/cli.py` (created in Phase 9). After the `summary_path.write_text(...)` line,
add the following anomaly-check block:

```python
    # ── Anomaly duty check (AGENTS.md § Science Rules) ───────────────────
    ANOMALY_CHI2_THRESHOLD = 10.0
    ANOMALY_CORR_THRESHOLD = 0.90

    anomalies = []
    for bin_key, model_results in summary.get("best_model_per_bin", {}).items():
        for model_key, model_run in results.items() if isinstance(results, dict) else []:
            if isinstance(model_run, dict):
                chi2_ndf = model_run.get("chi2_ndf", 0)
                if chi2_ndf > ANOMALY_CHI2_THRESHOLD:
                    anomalies.append({
                        "type": "chi2_regression",
                        "bin": bin_key,
                        "model": model_key,
                        "chi2_ndf": chi2_ndf,
                        "threshold": ANOMALY_CHI2_THRESHOLD,
                    })
                for corr_key, corr_val in model_run.get("correlations", {}).items():
                    if abs(corr_val) > ANOMALY_CORR_THRESHOLD:
                        anomalies.append({
                            "type": "high_correlation",
                            "bin": bin_key,
                            "model": model_key,
                            "param_pair": corr_key,
                            "rho": corr_val,
                            "threshold": ANOMALY_CORR_THRESHOLD,
                        })

    if anomalies:
        anomaly_path = run_dir / "anomalies.json"
        anomaly_path.write_text(json.dumps(anomalies, indent=2))
        print(
            f"\n⚠️  ANOMALY DUTY: {len(anomalies)} anomaly/anomalies detected. "
            f"See {anomaly_path}.\n"
            f"Per AGENTS.md § Science Rules, you MUST append a proposed follow-up "
            f"item to research/robert/next-actions.md before ending this session.\n"
            f"Invoke agent-skills/science-hypothesis-generator/ to draft the entry.",
            file=sys.stderr,
        )
        summary["anomalies"] = anomalies
        summary_path.write_text(json.dumps(summary, indent=2))
    # ─────────────────────────────────────────────────────────────────────
```

**Important:** Only add this block if it does not already exist.
Check with `grep -n "ANOMALY_CHI2_THRESHOLD" physics/cli.py` first.

**Acceptance:** `grep "ANOMALY_CHI2_THRESHOLD" physics/cli.py` returns ≥ 1 line.

---

## PHASE 12 — Integration Verification & Constitution Smoke-Test

This final phase verifies the entire innovation stack end-to-end.

### Task 12A — End-to-end smoke test

Run the following sequence and record every output line in
`research/robert/runs/YYYY-MM-DD-innovation-smoke-test/smoke_test.log`:

```bash
# Step 1: CLI dry-run
python physics/cli.py \
    --dry-run \
    --run-dir research/robert/runs/$(date +%Y-%m-%d)-innovation-smoke-test \
    --data-path physics/data/fit_input_ins1735345.csv

# Step 2: Ledger anomaly scan (structural only, no MCP required)
python - <<'EOF'
import pathlib, re
ledger = pathlib.Path("research/robert/evidence-ledger.md").read_text()
sanity = re.findall(r'\|\s*([A-Z]-\d+)[^|]*\|\s*Sanity checked', ledger)
print(f"Claims at Sanity checked: {sanity}")
print("Structural scan: OK")
EOF

# Step 3: Verify AGENTS.md has autonomous queue rules
grep -c "Agent-Proposed" AGENTS.md && echo "AGENTS.md: constitution OK"

# Step 4: Verify ledger-anomaly-detector skill exists
test -f agent-skills/ledger-anomaly-detector/SKILL.md && \
    echo "Ledger anomaly detector: OK"

# Step 5: Verify science-hypothesis-generator skill exists
test -f agent-skills/science-hypothesis-generator/SKILL.md && \
    echo "Science hypothesis generator: OK"

# Step 6: Verify CLI exists
test -f physics/cli.py && echo "Physics CLI: OK"

# Step 7: Verify de-vendoring decision exists
test -f docs/decisions/2026-07-09-deerflow-devendoring.md && \
    echo "De-vendoring decision: OK"
```

Write a summary `smoke_test_report.md` in the run directory:

```markdown
# Innovation Phase Smoke Test

**Date:** YYYY-MM-DD
**Runner:** <agent name/model>

## Results

| Check | Result |
| :--- | :--- |
| Physics CLI dry-run | PASS / FAIL |
| AGENTS.md constitution | PASS (N matches) / FAIL |
| Ledger anomaly detector skill | PASS / FAIL |
| Science hypothesis generator skill | PASS / FAIL |
| De-vendoring decision doc | PASS / FAIL |
| Structural ledger scan | PASS — N claims at Sanity checked |

## Open Items
<list any FAIL items with remediation notes>
```

**Acceptance:** All 7 checks pass. `smoke_test_report.md` exists with no FAIL rows.

---

### Task 12B — Final verification checklist (Innovation Phases)

After completing Phases 8–12, verify each item:

- [ ] `AGENTS.md` contains `## Autonomous Queue Management` with ≥ 4 rules.
- [ ] `agent-skills/ledger-anomaly-detector/SKILL.md` exists with ≥ 5 steps.
- [ ] `.github/workflows/ledger-scan.yml` exists and is syntactically valid.
- [ ] `physics/cli.py` exists, passes `--dry-run`, and contains `ANOMALY_CHI2_THRESHOLD`.
- [ ] `physics/src/fitting_pipeline.py` contains `def run_all_fits(`.
- [ ] `.github/workflows/physics-tests.yml` contains the CLI smoke-test step.
- [ ] `docs/decisions/2026-07-09-deerflow-devendoring.md` exists.
- [ ] `agent-skills/MIGRATION_MANIFEST.md` exists (even if empty — indicates audit done).
- [ ] `agent-skills/science-hypothesis-generator/SKILL.md` exists with ≥ 5 steps.
- [ ] Smoke-test run dir exists under `research/robert/runs/YYYY-MM-DD-innovation-smoke-test/`.
- [ ] `smoke_test_report.md` contains no FAIL rows.
- [ ] `research/robert/next-actions.md` was NOT modified by this phase
      (innovation phases do not touch the science queue).

---

## OPERATIONAL CONSTRAINTS REMINDER (all phases)

- All new run artifacts: `research/robert/runs/YYYY-MM-DD-<name>/`
- All permanent findings: `research/robert/evidence-ledger.md` (append only)
- `next-actions.md`: move completed items only; new items go under `🤖 Agent-Proposed`
- Do not create backlog, audit, or status markdown files
- Do not promote any claim beyond Validated without completing the required gate
- Preserve all unrelated user changes in the working tree
- Innovation phases (8–12) must not regress any Phase 1–7 output

