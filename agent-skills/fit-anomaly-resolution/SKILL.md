---
name: fit-anomaly-resolution
description: Playbook for translating mathematical fit anomalies (e.g. chi2 > 10, rho > 0.99) into physically sound model modifications using literature-grounded heuristics.
---

# Fit Anomaly Resolution (Physics Ideation)

## Purpose
When performing physics fits on High Energy Physics (HEP) transverse momentum ($p_T$) spectra, it is common for the optimizer to fail, return unphysical parameters, or produce massive residuals in specific kinematic regions. 
**Your job is NOT to blindly tweak math (e.g., arbitrarily add polynomials). Your job is to identify the missing physics.**

Invoke this skill whenever you encounter an anomaly during a fit (e.g., $\chi^2/ndf > 10$, correlation $|\rho| > 0.99$, or unphysical parameter bounds).

---

## Standard Operating Procedure (SOP)

When an anomaly triggers this skill, follow these 4 strict steps:

### Step 1: Identify the Mathematical Signature
Is the fit failing exclusively at low-$p_T$? High-$p_T$? Are parameters perfectly anti-correlated? Document the exact nature of the failure.

### Step 2: Hypothesize the Missing Physics
Map the mathematical failure to a physical mechanism. Use the **Historical Archetypes** below as few-shot examples of the required caliber of reasoning. 
*Ask yourself: Is the system lacking collective flow? Are there resonance decays polluting the data? Is the source not truly thermalized?*

### Step 3: Formulate the Model Modification
Propose a mathematically rigorous modification to the probability function that explicitly implements your physical hypothesis (e.g., wrapping the function in a feed-down integral, coupling parameters to string density).

### Step 4: Mandatory Literature Grounding (Ignition Pipeline)
Before presenting your hypothesis to the user, you MUST prove it exists in the literature.
1. Run the Ignition Literature Intake pipeline (`ignition/ingest_pipeline.py`) or perform an arXiv search for papers validating your specific mechanism.
2. If no literature supports the modification, discard it.
3. Propose the finalized, literature-backed modification to `research/robert/next-actions.md` under `## 🤖 Agent-Proposed`.

---

## Historical Archetypes (Few-Shot Context)

Use these 5 real, literature-grounded examples to calibrate your ideation. Your proposed solutions must match this level of domain expertise.

### 1. Thermodynamically Consistent Tsallis
**Anomaly Target:** Standard Tsallis fits showing unphysical parameter correlations or violating energy conservation across bins.
**Physical Foundation:** Early applications of Tsallis non-extensive statistics to particle spectra used a "naive" form that mathematically violated basic thermodynamic Maxwell relations. Cleymans & Worku (2012) derived a rigorously consistent form where entropy, volume, and temperature are properly defined.
**Model Modification:** Propose replacing the standard `tsallis_1c` function with the Cleymans-Worku form, shifting the exponent and integral boundaries to ensure the extracted temperature $T$ has true physical meaning.

### 2. Tsallis Blast-Wave (TBW) Model
**Anomaly Target:** BGBW (Blast-Wave) fits succeeding at low-$p_T$ but failing catastrophically at high-$p_T$ (where hard scattering dominates).
**Physical Foundation:** Traditional BGBW assumes the fireball is a perfectly thermalized Boltzmann-Gibbs source. The TBW model combines the macroscopic radial flow geometry of BGBW with the microscopic temperature fluctuations of Tsallis statistics.
**Model Modification:** Inject the non-extensivity parameter $q$ into the Blast-Wave integral. This captures hydrodynamical collective flow at low-$p_T$ while naturally producing the power-law tail at high-$p_T$ caused by temperature fluctuations in the QGP.

### 3. Mass-Dependent Non-Extensivity ($q_m$)
**Anomaly Target:** Joint/simultaneous fits across multiple particle species (e.g., $\pi, K, p$) failing when forced to share a single global $q$ parameter.
**Physical Foundation:** A single $q$ parameter over-constrains the medium. Heavier particles decouple (freeze-out) earlier or experience different local temperature fluctuations than lighter mesons.
**Model Modification:** Extend the TBW model to "TBW4", where $q$ is a function of particle rest mass $q(m)$. This tests if heavier baryons exhibit more or less non-equilibrium behavior than light mesons.

### 4. Resonance Feed-Down Integrals
**Anomaly Target:** Fits consistently missing the lowest $p_T$ bins (especially for pions), causing massive residual spikes.
**Physical Foundation:** A vast majority of low-$p_T$ pions are not "primordial" (from the thermal freeze-out surface), but are actually decay products of short-lived heavier resonances ($\rho \rightarrow \pi\pi$, $\Delta \rightarrow N\pi$, etc.) that decay after freeze-out.
**Model Modification:** Wrap the base function in a kinematic integral that accounts for resonance decay. This separates the true thermal spectrum from the "pollution" of decay products.

### 5. Color String Percolation Model (CSPM) Constraints
**Anomaly Target:** The optimizer gets stuck in an infinite valley where $T$ and $q$ are perfectly anti-correlated ($|\rho| > 0.99$), unable to distinguish between a hotter thermal source and a highly non-equilibrium cold source.
**Physical Foundation:** Instead of treating $q$ as a free parameter, CSPM connects it to the initial state of the collision—specifically, the density and overlap of QCD color strings, which percolate and thermalize the medium as density increases.
**Model Modification:** Hard-couple $q$ to the event multiplicity (or string density), reducing degrees of freedom by explicitly constraining $q$ based on the initial collision geometry rather than leaving it free.

### 6. The Two-Component Model (Bylinkin & Rostovtsev)
**Anomaly Target:** A single continuous function (like TBW or Tsallis) failing to simultaneously capture the ultra-soft $p_T$ region (< 0.5 GeV/c) and the hard partonic tail (> 4 GeV/c), resulting in systemic residuals at both ends.
**Physical Foundation:** The $p_T$ spectrum is physically formed by two distinct production mechanisms that overlap: thermalized particle production from the "soft" bulk medium, and perturbative QCD (pQCD) "hard" scatterings (mini-jets) that fragment into hadrons.
**Model Modification:** Fit the spectrum with an explicit additive two-component function: an exponential (or BGBW) term for the soft thermal bulk, plus a power-law term for the hard partonic scatterings. This stops the optimizer from artificially raising the thermal temperature just to fit the pQCD tail.

### 7. Quantum Tsallis Statistics (Bose-Einstein / Fermi-Dirac Tsallis)
**Anomaly Target:** The standard `tsallis_1c` function systematically missing the lowest $p_T$ bins for pions (bosons) and protons (fermions), even with resonance feed-down included.
**Physical Foundation:** The phenomenological Tsallis distribution used in most fits is derived in the classical Maxwell-Boltzmann limit (ignoring the $\pm 1$ term in the denominator). However, at very low momenta, quantum statistics matter immensely—pions experience Bose enhancement, and protons experience Pauli blocking.
**Model Modification:** Swap the classical Tsallis function for the full Quantum Tsallis numerical integration, explicitly including the $-1$ (Bose-Einstein) or $+1$ (Fermi-Dirac) in the non-extensive denominator.

### 8. Sequential (Multiple) Kinetic Freeze-Out Surfaces
**Anomaly Target:** A global BGBW fit across all particle species simultaneously ($\pi, K, p, \Lambda, \Xi, \Omega$) returning an unacceptably high $\chi^2/ndf$, driven by the multi-strange baryons.
**Physical Foundation:** Multi-strange baryons ($\Xi, \Omega$) have significantly smaller hadronic scattering cross-sections than light unflavored hadrons ($\pi, p$). Therefore, they decouple (freeze out) from the hadronic gas earlier in the expansion—meaning they should reflect a hotter temperature $T_{kin}$ and a smaller radial flow velocity $\langle\beta\rangle$.
**Model Modification:** Split the global fit into a two-surface model. One set of $T_{kin}$ and $\langle\beta\rangle$ parameters is constrained to the light hadrons, and a separate, independent set is constrained to the multi-strange baryons.

### 9. Excluded Volume (Van der Waals) HRG Corrections
**Anomaly Target:** Fits in very high-multiplicity Pb-Pb collisions yielding unphysically high temperatures or suggesting particle densities that exceed the physical size of hadrons.
**Physical Foundation:** Standard models treat hadrons as point-like particles (an Ideal Hadron Resonance Gas). In extremely dense environments, the finite physical size of hadrons creates a repulsive Van der Waals-like effect (Excluded Volume).
**Model Modification:** Modify the thermodynamic integrals to include an Excluded Volume correction factor (using a hard-core radius of $\sim 0.3$ fm for mesons and $\sim 0.5$ fm for baryons). This physically suppresses particle densities at high multiplicities and corrects the extracted temperature downwards.

### 10. Non-Boost-Invariant (3D) Blast-Wave (Kramer-Lietava)
**Anomaly Target:** BGBW fits struggling to describe data when integrating over wider pseudorapidity ($\eta$) or rapidity ($y$) acceptance windows.
**Physical Foundation:** The standard BGBW model uses Bjorken longitudinal expansion, assuming the fireball is an infinitely long cylinder that is completely boost-invariant. Real collisions, especially at lower energies or away from mid-rapidity, are finite in the longitudinal direction and experience 3D expansion.
**Model Modification:** Swap the infinite cylinder geometry for a Kramer-Lietava (KL) style non-boost-invariant Blast-Wave. This introduces a finite longitudinal velocity gradient, which subtly alters the resulting transverse momentum projection compared to the flat Bjorken assumption.
