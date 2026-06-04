#!/usr/bin/env python3
"""Physics Pipeline Dashboard Backend

Simple Flask server providing dashboard data for physics pipeline status,
recent runs, agenda, and evidence ledger.

Usage:
    python3 physics/dashboard/backend.py

Access at: http://localhost:5050
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template
from flask_cors import CORS

from collector import (
    collect_agenda,
    collect_evidence_summary,
    collect_recent_runs,
    collect_status,
)


app = Flask(__name__, static_folder="static", template_folder=".")
CORS(app)

REPO_ROOT = Path(__file__).resolve().parents[2]


@app.route("/")
def index():
    """Serve dashboard HTML."""
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    """Get current pipeline status."""
    try:
        status = collect_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/runs")
def api_runs():
    """Get recent run history."""
    try:
        runs = collect_recent_runs(limit=10)
        return jsonify({"runs": runs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/agenda")
def api_agenda():
    """Get next actions from next-actions.md."""
    try:
        agenda = collect_agenda()
        return jsonify({"agenda": agenda})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/evidence")
def api_evidence():
    """Get evidence ledger summary."""
    try:
        evidence = collect_evidence_summary()
        return jsonify({"evidence": evidence})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/models")
def api_models():
    """Get available models and their status."""
    models = [
        {
            "name": "Manuscript Jüttner",
            "type": "Covariant Boltzmann",
            "parameters": ["norm", "T", "U"],
            "status": "available",
        },
        {
            "name": "Exact Bose-Einstein",
            "type": "Quantum Statistics",
            "parameters": ["norm", "T", "U"],
            "status": "available",
        },
        {
            "name": "Tsallis",
            "type": "Non-extensive",
            "parameters": ["norm", "T", "q"],
            "status": "available",
        },
        {
            "name": "Blast-Wave",
            "type": "Radial Flow",
            "parameters": ["norm", "T", "β_s", "n"],
            "status": "available",
        },
    ]
    return jsonify({"models": models})


@app.route("/api/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})


if __name__ == "__main__":
    print("Starting Physics Pipeline Dashboard...")
    print("Access at: http://localhost:5050")
    app.run(host="0.0.0.0", port=5050, debug=True)
