import sqlite3
import os
from database import get_connection

def seed_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Seed Tasks
    tasks = [
        ("t1", "Run bose_1c head-to-head vs Tsallis 2c", "Fit the corrected Bose-Einstein formula across all 10 multiplicity bins and compare AIC/BIC against Tsallis 2c baseline.", "HIGH", "AI", "2026-07-09", "", "active"),
        ("t2", "Regenerate Table 1 with χ²/ndf and uncertainties", "Produce a publication-ready replacement for manuscript Table 1 including all validated models.", "HIGH", "AI", "2026-07-09", "", "active"),
        ("t3", "Write thesis chapter 04_ai_methodology", "Document the multi-agent pipeline, fitting architecture, and OpenAlex integration.", "MEDIUM", "RB", "2026-07-08", "", "active"),
        ("t4", "Enable Ollama LLM extraction", "Replace mock extraction_engine with real LLM calls. Blocked: Ollama endpoint not configured.", "MEDIUM", "AI", "2026-07-07", "", "blocked"),
        ("t5", "Scite.ai citation lookup integration", "Query Scite for each claim's supporting literature. Blocked: API key not in environment.", "LOW", "AI", "2026-07-06", "", "blocked"),
        ("t6", "Full covariance scan: ρ(T,β) correlation across all bins", "Triggered by observation: ρ(T,β) = 0.97 in bin 61-70. Proposed action: systematically compute off-diagonal covariance.", "HIGH", "AI", "2026-07-09", "Lafferty & Wyatt (1995) — NIM A355", "proposed")
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO Tasks (id, title, description, priority, assignee, date, citation, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', tasks)

    # Seed Evidence
    evidence = [
        ("Jüttner 1c model gives χ²/ndf >> 1 across all bins at 13 TeV", "Supported", "—", "2026-07-09-jacobian-fix", "All 10 multiplicity bins fitted with Jüttner 1c yield χ²/ndf in the range 68–227, far above the acceptance threshold of 5."),
        ("Jacobian dy/dη missing from manuscript_component_scalar", "Supported", "—", "2026-07-09-jacobian-fix", "Direct diff of the manuscript source vs the fitting code confirmed the Jacobian was applied in code but omitted from the written derivation."),
        ("T-β degeneracy: ρ(T,β) > 0.9 in high-multiplicity bins", "Sanity Checked", "Full covariance scan across all bins needed", "2026-07-09-jacobian-fix", "Correlation observed in bin 61-70 (ρ=0.97) and reproduced in bins 71-80, 81-90."),
        ("PySR independently recovers threshold at m ≈ 136 MeV (pion mass)", "Sanity Checked", "Rerun PySR with 5-fold cross-validation", "pysr-run-2026-07-04", "Symbolic regression converged on a functional form with a break-scale at 136 MeV in 4/5 seeds."),
        ("Bose-Einstein denominator improves χ²/ndf over Boltzmann", "Proposed", "Run bose_1c head-to-head against Tsallis 2c", "—", "Preliminary single-bin tests are promising but a full 10-bin comparison against Tsallis 2c baseline is pending."),
        ("Multiplicity dependence captured by effective temperature T(N)", "Proposed", "Fit T vs N_ch across all bins", "—", "T appears to rise with N_ch monotonically in the Tsallis 2c fits.")
    ]
    cursor.executemany('''
        INSERT INTO Evidence (claim, status, nextGate, run, narrative)
        VALUES (?, ?, ?, ?, ?)
    ''', evidence)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed_db()
    print("Database seeded with initial data.")
