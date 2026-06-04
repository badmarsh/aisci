#!/usr/bin/env python3
"""Data collector for physics pipeline dashboard.

Parses run artifacts, evidence ledger, and next actions to provide
dashboard data.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = REPO_ROOT / "research" / "robert" / "runs"
EVIDENCE_LEDGER = REPO_ROOT / "research" / "robert" / "evidence-ledger.md"
NEXT_ACTIONS = REPO_ROOT / "research" / "robert" / "next-actions.md"


def collect_status() -> dict[str, Any]:
    """Collect current pipeline status."""
    # Check if data is available
    data_available = check_data_availability()

    # Check recent runs
    recent_runs = list(RUNS_DIR.glob("*"))
    has_recent_runs = len(recent_runs) > 0

    # Determine overall status
    if not data_available:
        status = "blocked"
        message = "Blocked: Awaiting per-multiplicity-bin pT spectra"
    elif not has_recent_runs:
        status = "ready"
        message = "Ready: No runs yet"
    else:
        status = "complete"
        message = f"Complete: {len(recent_runs)} runs available"

    return {
        "status": status,
        "message": message,
        "data_available": data_available,
        "run_count": len(recent_runs),
        "last_updated": datetime.utcnow().isoformat(),
    }


def check_data_availability() -> bool:
    """Check if HEPData is available."""
    # Check for any fit_input.csv in runs
    for run_dir in RUNS_DIR.glob("*"):
        if (run_dir / "fit_input.csv").exists():
            return True
    return False


def collect_recent_runs(limit: int = 10) -> list[dict[str, Any]]:
    """Collect recent run history."""
    runs = []

    # Get all run directories
    run_dirs = sorted(RUNS_DIR.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)

    for run_dir in run_dirs[:limit]:
        run_data = parse_run_directory(run_dir)
        if run_data:
            runs.append(run_data)

    return runs


def parse_run_directory(run_dir: Path) -> dict[str, Any] | None:
    """Parse a single run directory."""
    if not run_dir.is_dir():
        return None

    run_data = {
        "name": run_dir.name,
        "date": datetime.fromtimestamp(run_dir.stat().st_mtime).isoformat(),
        "models": [],
    }

    # Parse fit_quality.csv if exists
    quality_file = run_dir / "fit_quality.csv"
    if quality_file.exists():
        try:
            with open(quality_file, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    run_data["models"].append({
                        "model": row.get("model", ""),
                        "components": row.get("components", ""),
                        "chi2_ndf": float(row.get("chi2_ndf", 0)),
                        "aic": float(row.get("aic", 0)),
                        "bic": float(row.get("bic", 0)),
                    })
        except Exception:
            pass

    # Parse model_comparison.csv if exists
    comparison_file = run_dir / "model_comparison.csv"
    if comparison_file.exists():
        try:
            with open(comparison_file, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                if rows:
                    run_data["best_model"] = rows[0].get("model", "")
        except Exception:
            pass

    return run_data


def collect_agenda() -> list[dict[str, Any]]:
    """Collect next actions from next-actions.md."""
    if not NEXT_ACTIONS.exists():
        return []

    agenda = []
    content = NEXT_ACTIONS.read_text(encoding="utf-8")

    # Parse markdown list items
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("- ["):
            # Parse checkbox status
            if "[ ]" in line:
                status = "pending"
            elif "[x]" in line or "[X]" in line:
                status = "completed"
            else:
                status = "unknown"

            # Extract text after checkbox
            text = line.split("]", 1)[1].strip() if "]" in line else line

            # Extract ID if present (e.g., [B-01])
            task_id = ""
            if text.startswith("[") and "]" in text:
                task_id = text[1:text.index("]")]
                text = text[text.index("]")+1:].strip()

            agenda.append({
                "id": task_id,
                "text": text,
                "status": status,
            })

    return agenda


def collect_evidence_summary() -> dict[str, Any]:
    """Collect evidence ledger summary."""
    if not EVIDENCE_LEDGER.exists():
        return {
            "total_claims": 0,
            "verified": 0,
            "pending": 0,
            "blocked": 0,
            "claims": [],
        }

    content = EVIDENCE_LEDGER.read_text(encoding="utf-8")

    # Count claims by status
    verified = content.count("✅ VERIFIED") + content.count("✅ CONFIRMED")
    pending = content.count("🟡 OPEN") + content.count("⏳ PENDING")
    blocked = content.count("🔴 BLOCKED")

    # Parse individual claims
    claims = []
    current_claim = None

    for line in content.splitlines():
        line = line.strip()

        # Detect claim headers (## Claim: ...)
        if line.startswith("## Claim:") or line.startswith("## "):
            if current_claim:
                claims.append(current_claim)

            claim_text = line.replace("## Claim:", "").replace("##", "").strip()
            current_claim = {
                "text": claim_text,
                "status": "unknown",
                "evidence": [],
            }

        # Detect status
        elif current_claim and "**Status:**" in line:
            if "✅" in line or "VERIFIED" in line or "CONFIRMED" in line:
                current_claim["status"] = "verified"
            elif "🟡" in line or "OPEN" in line or "PENDING" in line:
                current_claim["status"] = "pending"
            elif "🔴" in line or "BLOCKED" in line:
                current_claim["status"] = "blocked"

    # Add last claim
    if current_claim:
        claims.append(current_claim)

    return {
        "total_claims": len(claims),
        "verified": verified,
        "pending": pending,
        "blocked": blocked,
        "claims": claims[:10],  # Return first 10 claims
    }


if __name__ == "__main__":
    # Test collectors
    print("Status:", json.dumps(collect_status(), indent=2))
    print("\nRecent Runs:", json.dumps(collect_recent_runs(limit=3), indent=2))
    print("\nAgenda:", json.dumps(collect_agenda(), indent=2))
    print("\nEvidence:", json.dumps(collect_evidence_summary(), indent=2))
