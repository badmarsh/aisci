import os
import json
import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import asyncio
import sys
import time
sys.path.insert(0, os.path.dirname(__file__))
import sync_markdown
from datetime import datetime

from database import init_db

app = FastAPI(title="AiSci Dashboard API")

@app.on_event("startup")
async def startup():
    init_db()
    for log_name in ['ingest.log', 'fits.log']:
        log_path = os.path.join(os.path.dirname(__file__), '..', log_name)
        if not os.path.exists(log_path):
            open(log_path, 'a').close()
    sync_markdown.sync_evidence_to_db()
    sync_markdown.sync_tasks_to_db()

# Allow requests from Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'evidence_graph.db')
RUNS_BASE = os.path.join(os.path.dirname(__file__), '..', 'research', 'robert', 'runs')

def get_latest_run_path() -> str:
    """Return the most recently modified run directory that contains fit_quality.csv."""
    candidates = [
        d for d in os.listdir(RUNS_BASE)
        if os.path.isdir(os.path.join(RUNS_BASE, d))
        and os.path.exists(os.path.join(RUNS_BASE, d, 'fit_quality.csv'))
    ]
    if not candidates:
        raise FileNotFoundError("No completed run directories found.")
    return os.path.join(RUNS_BASE, sorted(candidates)[-1])

def list_run_dirs() -> list[str]:
    """Return all run directory names, newest first."""
    if not os.path.exists(RUNS_BASE):
        return []
    candidates = [
        d for d in os.listdir(RUNS_BASE)
        if os.path.isdir(os.path.join(RUNS_BASE, d))
    ]
    return sorted(candidates, reverse=True)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def log_activity(action, user, details):
    conn = get_db()
    conn.execute("INSERT INTO ActivityLogs (timestamp, action, user, details) VALUES (?, ?, ?, ?)",
                 (datetime.now().isoformat() + "Z", action, user, details))
    conn.commit()
    conn.close()

# --- Pydantic Models ---

class Claim(BaseModel):
    text: str
    confidence: str

class Paper(BaseModel):
    source: str
    category: str
    title: str
    published: str
    claims: int
    bridge: bool
    abstract: str
    url: str
    claimList: List[Claim]

class EvidenceRow(BaseModel):
    id: int
    claim: str
    status: str
    nextGate: str
    run: str
    narrative: str

class TaskModel(BaseModel):
    id: str
    title: str
    description: str
    priority: str
    assignee: str
    date: str
    citation: Optional[str] = None
    status: str

class AgentModel(BaseModel):
    name: str
    status: str
    last: str
    summary: str
    log: List[str]

class StatusUpdate(BaseModel):
    status: str

# --- Endpoints ---

@app.get("/api/literature", response_model=List[Paper])
def get_literature():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Papers")
    papers_rows = cursor.fetchall()
    
    result = []
    for p in papers_rows:
        cursor.execute("SELECT claim_text, confidence FROM Claims WHERE paper_id = ?", (p['id'],))
        claims_rows = cursor.fetchall()
        
        claim_list = [{"text": c["claim_text"], "confidence": c["confidence"]} for c in claims_rows]
        
        # Hardcoding openalex vs arxiv source based on id format for now, bridge based on category
        source = "OpenAlex" if p['id'].startswith("W") else "arXiv"
        bridge = p['category'] in ["cs.CL", "cs.AI"]
        
        result.append({
            "source": source,
            "category": p["category"],
            "title": p["title"],
            "published": p["published_date"],
            "claims": len(claim_list),
            "bridge": bridge,
            "abstract": p["abstract"],
            "url": p["url"],
            "claimList": claim_list
        })
    conn.close()
    
    # If DB is empty, return a fallback just for demonstration, otherwise return results
    return result

@app.get("/api/evidence", response_model=List[EvidenceRow])
def get_evidence():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Evidence")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.patch("/api/evidence/{evidence_id}")
def update_evidence(evidence_id: int, body: StatusUpdate):
    sync_markdown.sync_db_to_evidence(evidence_id, body.status)
    conn = get_db()
    conn.execute("UPDATE Evidence SET status = ? WHERE id = ?", (body.status, evidence_id))
    conn.commit()
    conn.close()
    log_activity("Updated Evidence", "User", f"Set evidence #{evidence_id} to {body.status}")
    return {"status": "success"}

@app.get("/api/fits")
def get_fits(run: Optional[str] = None, compare_run: Optional[str] = None):
    try:
        run_path = os.path.join(RUNS_BASE, run) if run else get_latest_run_path()
        run_name = os.path.basename(run_path)
        
        # Check if CSVs exist, if not return Incomplete payload
        if not os.path.exists(os.path.join(run_path, "fit_quality.csv")):
            return {
                "status": "Incomplete",
                "error": "Missing fit_quality.csv",
                "runId": run_name,
                "fitRows": [],
                "chi2Series": [],
                "bins": []
            }
            
        quality_df = pd.read_csv(os.path.join(run_path, "fit_quality.csv"))
        params_df = pd.read_csv(os.path.join(run_path, "fit_parameters.csv"))
        corr_df = pd.read_csv(os.path.join(run_path, "parameter_correlations.csv"))
    except Exception as e:
        # Fallback for other errors (e.g., malformed CSV)
        return {
            "status": "Incomplete",
            "error": str(e),
            "runId": run if run else "unknown",
            "fitRows": [],
            "chi2Series": [],
            "bins": []
        }

    # Map model names to nice names
    model_map = {
        "manuscript_juttner": "Jüttner 1c",
        "tsallis": "Tsallis 2c",
        "exact_bose_einstein": "Bose-Einstein 1c"
    }

    # Build correlation lookup: { bin: { model_nice: { "param_left|param_right": rho } } }
    corr_lookup: dict = {}
    for _, row in corr_df.iterrows():
        b = row['group_label']
        m_nice = model_map.get(row['model_name'], row['model_name'])
        key = f"{row['parameter_left']}|{row['parameter_right']}"
        corr_lookup.setdefault(b, {}).setdefault(m_nice, {})[key] = round(float(row['correlation']), 4)

    run_name = os.path.basename(run_path)
    run_date = run_name[:10] if len(run_name) >= 10 else "unknown"
    run_timestamp = f"{run_date}T00:00:00Z"

    # First we build the fitRows
    fit_rows = []
    
    for _, row in quality_df.iterrows():
        bin_label = row['group_label']
        model_nice = model_map.get(row['model_name'], row['model_name'])
        
        # get params
        subset = params_df[(params_df['group_label'] == bin_label) & (params_df['model_name'] == row['model_name'])]
        
        t_str = "—"
        beta_str = "—"
        
        t_row = subset[subset['parameter_name'] == 'temperature_1']
        if not t_row.empty:
            t_val = t_row.iloc[0]['value']
            t_err = t_row.iloc[0]['error']
            t_str = f"{t_val:.3f} ± {t_err:.3f}"
            
        beta_row = subset[subset['parameter_name'] == 'beta_1'] # hypothetical, might be 'beta_1' or 'velocity_1'
        if not beta_row.empty:
            b_val = beta_row.iloc[0]['value']
            b_err = beta_row.iloc[0]['error']
            beta_str = f"{b_val:.3f} ± {b_err:.3f}"

        fit_rows.append({
            "bin": bin_label,
            "model": model_nice,
            "chi2": round(row['chi2_ndf'], 2),
            "quality": row['fit_quality_flag'].upper(),
            "T": t_str,
            "beta": beta_str,
            "aic": round(row['aic'], 1),
            "status": "Converged" if row['success'] else "Failed",
            "correlations": corr_lookup.get(bin_label, {}).get(model_nice, {}),
            "seedIndex": int(row['seed_index']) if 'seed_index' in row and not pd.isna(row['seed_index']) else None,
            "runTimestamp": run_timestamp,
        })

    # Now build the chi2Series (for the chart)
    # We need bins and for each bin, chi2 for each model
    bins = sorted(quality_df['group_label'].unique(), key=lambda x: int(x.split('-')[0]))
    chi2_series = []
    for b in bins:
        entry = {"bin": b}
        for m in ["Jüttner 1c", "Tsallis 2c", "Bose-Einstein 1c"]:
            val = None
            subset = quality_df[(quality_df['group_label'] == b) & (quality_df['model_name'].map(lambda x: model_map.get(x, x)) == m)]
            if not subset.empty:
                val = subset.iloc[0]['chi2_ndf']
            entry[m] = round(val, 2) if val is not None and not pd.isna(val) else None
        chi2_series.append(entry)

    compare_series = None
    if compare_run:
        try:
            cmp_path = os.path.join(RUNS_BASE, compare_run)
            cmp_quality = pd.read_csv(os.path.join(cmp_path, "fit_quality.csv"))
            compare_series = []
            for b in bins:
                entry = {"bin": b}
                for m_raw, m_nice in model_map.items():
                    val = cmp_quality[(cmp_quality['group_label'] == b) & (cmp_quality['model_name'] == m_raw)]
                    if not val.empty:
                        entry[f"{m_nice} (cmp)"] = val.iloc[0]['chi2_ndf']
                compare_series.append(entry)
        except Exception:
            compare_series = None

    return {
        "fitRows": fit_rows,
        "chi2Series": chi2_series,
        "compareSeries": compare_series,
        "bins": bins,
        "runId": run_name
    }

@app.get("/api/fits/runs")
def get_fit_runs():
    return {"runs": list_run_dirs()}

class AnomalyItem(BaseModel):
    bin: str
    model: str
    type: str      # "chi2" | "correlation" | "boundary"
    severity: str  # "critical" | "warning"
    message: str
    value: float

@app.get("/api/anomalies", response_model=List[AnomalyItem])
def get_anomalies(
    run: Optional[str] = None,
    chi2_critical: float = 200.0,
    chi2_warning: float = 10.0,
    rho_warning: float = 0.95
):
    """Scan the latest (or specified) run for physics anomalies."""
    try:
        run_path = os.path.join(RUNS_BASE, run) if run else get_latest_run_path()
        quality_df = pd.read_csv(os.path.join(run_path, "fit_quality.csv"))
        corr_df = pd.read_csv(os.path.join(run_path, "parameter_correlations.csv"))
        params_df = pd.read_csv(os.path.join(run_path, "fit_parameters.csv"))
    except FileNotFoundError:
        return []

    model_map = {
        "manuscript_juttner": "Jüttner 1c",
        "tsallis": "Tsallis 2c",
        "exact_bose_einstein": "Bose-Einstein 1c"
    }
    anomalies: List[AnomalyItem] = []

    # Chi2/ndf checks
    for _, row in quality_df.iterrows():
        m = model_map.get(row['model_name'], row['model_name'])
        chi2_val = float(row['chi2_ndf'])
        if chi2_val > chi2_critical:
            anomalies.append(AnomalyItem(
                bin=row['group_label'], model=m, type="chi2", severity="critical",
                message=f"χ²/ndf = {chi2_val:.0f} — model fails completely",
                value=chi2_val
            ))
        elif chi2_val > chi2_warning:
            anomalies.append(AnomalyItem(
                bin=row['group_label'], model=m, type="chi2", severity="warning",
                message=f"χ²/ndf = {chi2_val:.1f} — poor fit quality",
                value=chi2_val
            ))

    # Off-diagonal correlation checks
    for _, row in corr_df.iterrows():
        if row['parameter_left'] == row['parameter_right']:
            continue
        rho = float(row['correlation'])
        if abs(rho) > rho_warning:
            m = model_map.get(row['model_name'], row['model_name'])
            anomalies.append(AnomalyItem(
                bin=row['group_label'], model=m, type="correlation", severity="warning",
                message=f"ρ({row['parameter_left']}, {row['parameter_right']}) = {rho:.3f}",
                value=abs(rho)
            ))

    # Boundary checks (U_1 at speed-of-light limit)
    for _, row in params_df.iterrows():
        if row['parameter_name'] == 'U_1' and float(row['value']) > 2.99:
            m = model_map.get(row['model_name'], row['model_name'])
            anomalies.append(AnomalyItem(
                bin=row['group_label'], model=m, type="boundary", severity="warning",
                message=f"U_1 = {float(row['value']):.4f} — at speed-of-light boundary (U < c)",
                value=float(row['value'])
            ))

    return anomalies

@app.get("/api/export/summary")
def get_export_summary():
    """Generates a text summary of the current project state for GitHub Issues/Logs."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get active fits count
    run_path = get_latest_run_path()
    active_fits_count = 0
    try:
        if run_path:
            qual = pd.read_csv(os.path.join(run_path, "fit_quality.csv"))
            active_fits_count = len(qual)
    except Exception:
        pass

    # Get anomalies
    anomalies = get_anomalies()
    anom_str = f"Found {len(anomalies)} anomalies in latest run.\n"
    if anomalies:
        for a in anomalies[:5]:
            anom_str += f"- [{a.bin}] {a.model}: {a.message}\n"
        if len(anomalies) > 5:
            anom_str += f"- ... and {len(anomalies)-5} more.\n"
    else:
        anom_str = "No physics anomalies detected in latest run.\n"

    # Get evidence pending review
    cursor.execute("SELECT count(*) FROM Evidence WHERE status='Proposed'")
    evidence_pending = cursor.fetchone()[0]

    # Get open tasks
    cursor.execute("SELECT count(*) FROM Tasks WHERE status != 'closed'")
    open_tasks = cursor.fetchone()[0]

    # Get latest literature
    cursor.execute("SELECT count(*) FROM Literature")
    lit_count = cursor.fetchone()[0]
    
    conn.close()

    markdown = f"""### AiSci Dashboard Export: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

**State Overview:**
- **Literature Ingested**: {lit_count}
- **Active Fits**: {active_fits_count} (latest run)
- **Pending Evidence**: {evidence_pending} claims awaiting review
- **Open Tasks**: {open_tasks}

**Physics Anomalies:**
{anom_str}
"""
    return {"markdown": markdown}

@app.post("/api/sync")
def sync_from_files():
    try:
        sync_markdown.sync_evidence_to_db()
        sync_markdown.sync_tasks_to_db()
        return {"status": "success", "message": "Synced successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks", response_model=List[TaskModel])
def get_tasks():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Tasks")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.patch("/api/tasks/{task_id}")
def update_task(task_id: str, body: StatusUpdate):
    sync_markdown.sync_db_to_tasks(task_id, body.status)
    conn = get_db()
    conn.execute("UPDATE Tasks SET status = ? WHERE id = ?", (body.status, task_id))
    conn.commit()
    conn.close()
    log_activity("Updated Task", "User", f"Set task {task_id} to {body.status}")
    return {"status": "success"}

def tail_log(filepath: str, lines: int = 10) -> list[str]:
    if not os.path.exists(filepath):
        # Pre-create empty log file to prevent subprocess error
        open(filepath, 'a').close()
        return ["[No log entries yet]"]
    try:
        res = subprocess.check_output(['tail', '-n', str(lines), filepath]).decode('utf-8', errors='replace')
        result = [l for l in res.split('\n') if l.strip()]
        return result if result else ["[Log is empty]"]
    except Exception as e:
        return [f"[Error reading log: {e}]"]

def stream_log_file(filepath: str, max_lines: int = 200):
    """Generator that yields new lines from a log file as they are written."""
    def generate():
        try:
            with open(filepath, 'r') as f:
                # First, yield all existing content
                existing = f.read()
                if existing:
                    yield f"data: {json.dumps({'lines': existing.splitlines()[-50:]})}\n\n"
                # Then tail for new lines
                for _ in range(60):  # max 60 seconds of streaming
                    line = f.readline()
                    if line:
                        yield f"data: {json.dumps({'line': line.rstrip()})}\n\n"
                    else:
                        time.sleep(0.5)
                yield 'data: {"done": true}\n\n'
        except FileNotFoundError:
            yield f"data: {json.dumps({'error': 'Log file not found: ' + filepath})}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@app.get("/api/logs/ingest")
def stream_ingest_log():
    log_path = os.path.join(os.path.dirname(__file__), '..', 'ingest.log')
    return stream_log_file(log_path)

@app.get("/api/logs/fits")
def stream_fits_log():
    log_path = os.path.join(os.path.dirname(__file__), '..', 'fits.log')
    return stream_log_file(log_path)

class ActivityModel(BaseModel):
    id: int
    timestamp: str
    action: str
    user: str
    details: str

@app.get("/api/activity", response_model=List[ActivityModel])
def get_activity():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ActivityLogs ORDER BY id DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/api/agents", response_model=List[AgentModel])
def get_agents():
    # Read actual tails from the log files
    log_dir = os.path.join(os.path.dirname(__file__), '..')
    backend_log = os.path.join(log_dir, 'backend.log')
    ingest_log = os.path.join(log_dir, 'ingest.log')
    fits_log = os.path.join(log_dir, 'fits.log')
    
    return [
        {
            "name": "FastAPI Backend",
            "status": "ACTIVE",
            "last": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "summary": "Main API server process",
            "log": tail_log(backend_log)
        },
        {
            "name": "Ingest Pipeline",
            "status": "IDLE" if not os.path.exists(ingest_log) else "ACTIVE",
            "last": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "summary": "Literature fetch and LLM extraction",
            "log": tail_log(ingest_log)
        },
        {
            "name": "Fit Pipeline",
            "status": "IDLE" if not os.path.exists(fits_log) else "ACTIVE",
            "last": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "summary": "Physics spectra fitting routines",
            "log": tail_log(fits_log)
        }
    ]

@app.post("/api/sync")
async def manual_sync():
    """Force a re-sync from canonical Markdown files. Call after external agent writes."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, sync_markdown.sync_evidence_to_db)
    await loop.run_in_executor(None, sync_markdown.sync_tasks_to_db)
    log_activity("Manual Sync", "User", "Re-synced Evidence and Tasks from Markdown files.")
    return {"status": "ok", "message": "Synced from evidence-ledger.md and next-actions.md"}

# Mutations
@app.post("/api/ingest")
async def trigger_ingest():
    log_activity("Started Run Ingest", "AI", "Triggered ingest_pipeline.py via dashboard")
    script_path = os.path.join(os.path.dirname(__file__), "ingest_pipeline.py")
    log_path = os.path.join(os.path.dirname(__file__), '..', 'ingest.log')
    with open(log_path, 'w') as f:
        subprocess.Popen([sys.executable, "-u", script_path], stdout=f, stderr=f)
    return {"status": "accepted", "message": "Ingest pipeline started"}

@app.post("/api/fits/run")
async def trigger_fits():
    log_activity("Started Fit Pipeline", "AI", "Triggered run_a1_jacobian_fits.py via dashboard")
    script_path = os.path.join(os.path.dirname(__file__), '..', 'deployment', 'helper', 'run_a1_jacobian_fits.py')
    log_path = os.path.join(os.path.dirname(__file__), '..', 'fits.log')
    with open(log_path, 'w') as f:
        subprocess.Popen(["python3", script_path], stdout=f, stderr=f)
    return {"status": "accepted", "message": "Fit runs started"}
