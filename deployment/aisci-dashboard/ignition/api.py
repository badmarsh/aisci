import os
import json
import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import asyncio
import sys
import time
import uuid
import json
sys.path.insert(0, os.path.dirname(__file__))
import sync_markdown
from datetime import datetime

from database import init_db
from config import RUNS_BASE, AUTH_TOKEN
import fit_parser
from validation_policy import default_policy

app = FastAPI(title="AiSci Dashboard API")

def verify_token(authorization: Optional[str] = Header(None)):
    if AUTH_TOKEN and authorization != f"Bearer {AUTH_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

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

from config import RUNS_BASE
from database import get_connection

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
    return get_connection()

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
    url: Optional[str] = None
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
def update_evidence(evidence_id: int, body: StatusUpdate, _: None = Depends(verify_token)):
    req_id = str(uuid.uuid4())
    conn = get_db()
    conn.execute(
        "INSERT INTO ReviewDecisions (id, target_id, requested_state, reviewer, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (req_id, str(evidence_id), body.status, "User", "Proposed", datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    log_activity("Review Requested", "User", f"Requested evidence #{evidence_id} status change to {body.status}")
    return {"status": "review_requested", "requestId": req_id}

@app.get("/api/fits")
def get_fits(run: Optional[str] = None, compare_run: Optional[str] = None):
    try:
        run_path = os.path.join(RUNS_BASE, run) if run else get_latest_run_path()
        parsed = fit_parser.parse_fit_artifacts(run_path)
    except Exception as e:
        return {
            "status": "Incomplete",
            "error": str(e),
            "runId": run if run else "unknown",
            "fitRows": [],
            "chi2Series": [],
            "bins": []
        }

    # Build chi2Series
    chi2_series = []
    for b in parsed["bins"]:
        entry = {"bin": b}
        for row in parsed["fitRows"]:
            if row["bin"] == b:
                entry[row["model"]] = row["chi2"]
        chi2_series.append(entry)

    compare_series = None
    if compare_run:
        try:
            cmp_path = os.path.join(RUNS_BASE, compare_run)
            cmp_parsed = fit_parser.parse_fit_artifacts(cmp_path)
            compare_series = []
            for b in cmp_parsed["bins"]:
                entry = {"bin": b}
                for row in cmp_parsed["fitRows"]:
                    if row["bin"] == b:
                        entry[f"{row['model']} (cmp)"] = row["chi2"]
                compare_series.append(entry)
        except Exception:
            compare_series = None

    return {
        "fitRows": parsed["fitRows"],
        "chi2Series": chi2_series,
        "compareSeries": compare_series,
        "bins": parsed["bins"],
        "runId": parsed["runId"]
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
def get_anomalies(run: Optional[str] = None):
    """Scan the latest (or specified) run for physics anomalies using ValidationPolicy."""
    try:
        run_path = os.path.join(RUNS_BASE, run) if run else get_latest_run_path()
        parsed = fit_parser.parse_fit_artifacts(run_path)
    except FileNotFoundError:
        return []

    anomalies: List[AnomalyItem] = []

    # Chi2 checks
    for _, row in parsed["quality_df"].iterrows():
        m_nice = fit_parser.parse_model_name(row['model_name'])
        chi2_val = float(row.get('chi2_ndf', 0.0))
        sev, msg = default_policy.validate_chi2(chi2_val)
        if sev != "ok":
            anomalies.append(AnomalyItem(
                bin=row['group_label'], model=m_nice, type="chi2", severity=sev,
                message=msg, value=chi2_val
            ))

    # Correlation checks
    for _, row in parsed["corr_df"].iterrows():
        if row['parameter_left'] == row['parameter_right']:
            continue
        rho = float(row['correlation'])
        sev, msg = default_policy.validate_correlation(rho, row['parameter_left'], row['parameter_right'])
        if sev != "ok":
            m_nice = fit_parser.parse_model_name(row['model_name'])
            anomalies.append(AnomalyItem(
                bin=row['group_label'], model=m_nice, type="correlation", severity=sev,
                message=msg, value=abs(rho)
            ))

    # Boundary checks
    for _, row in parsed["params_df"].iterrows():
        pname = row['parameter_name']
        val = float(row['value'])
        m_nice = fit_parser.parse_model_name(row['model_name'])
        
        if pname in ['beta_1', 'beta_s', 'velocity_1', 'v_1']:
            sev, msg = default_policy.validate_velocity(val)
            if sev != "ok":
                anomalies.append(AnomalyItem(
                    bin=row['group_label'], model=m_nice, type="boundary", severity=sev,
                    message=msg, value=val
                ))
        elif pname in ['U_1', 'u_1']:
            sev, msg = default_policy.validate_four_velocity(val)
            if sev != "ok":
                anomalies.append(AnomalyItem(
                    bin=row['group_label'], model=m_nice, type="boundary", severity=sev,
                    message=msg, value=val
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
    cursor.execute("SELECT count(*) FROM Papers")
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


@app.get("/api/tasks", response_model=List[TaskModel])
def get_tasks():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Tasks")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.patch("/api/tasks/{task_id}")
def update_task(task_id: str, body: StatusUpdate, _: None = Depends(verify_token)):
    req_id = str(uuid.uuid4())
    conn = get_db()
    conn.execute(
        "INSERT INTO ReviewDecisions (id, target_id, requested_state, reviewer, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (req_id, task_id, body.status, "User", "Proposed", datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    log_activity("Review Requested", "User", f"Requested task {task_id} status change to {body.status}")
    return {"status": "review_requested", "requestId": req_id}

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
async def manual_sync(_: None = Depends(verify_token)):
    """Force a re-sync from canonical Markdown files. Call after external agent writes."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, sync_markdown.sync_evidence_to_db)
    await loop.run_in_executor(None, sync_markdown.sync_tasks_to_db)
    log_activity("Manual Sync", "User", "Re-synced Evidence and Tasks from Markdown files.")
    return {"status": "ok", "message": "Synced from evidence-ledger.md and next-actions.md"}

@app.post("/api/materialize")
async def materialize_decisions(_: None = Depends(verify_token)):
    """Apply all 'Proposed' review decisions to the canonical Markdown files safely."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, sync_markdown.materialize_approved_decisions)
    return {"status": "ok", "message": "Materialized approved decisions to canonical files."}

async def run_job_in_background(job_id: str, name: str, cmd: list[str], log_path: str):
    conn = get_db()
    conn.execute("UPDATE JobExecutions SET status = 'running', log_path = ? WHERE id = ?", (log_path, job_id))
    conn.commit()
    conn.close()
    
    with open(log_path, 'w') as f:
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=f, stderr=f
        )
        await process.communicate()
    
    status = 'completed' if process.returncode == 0 else 'failed'
    conn = get_db()
    conn.execute("UPDATE JobExecutions SET status = ?, updated_at = ? WHERE id = ?", 
                 (status, datetime.now().isoformat(), job_id))
    conn.commit()
    conn.close()

@app.post("/api/ingest")
async def trigger_ingest(_: None = Depends(verify_token)):
    job_id = str(uuid.uuid4())
    conn = get_db()
    conn.execute("INSERT INTO JobExecutions (id, name, status, created_at) VALUES (?, ?, ?, ?)",
                 (job_id, "Ingest Pipeline", "pending", datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    log_activity("Started Run Ingest", "AI", "Triggered ingest_pipeline.py via dashboard")
    script_path = os.path.join(os.path.dirname(__file__), "ingest_pipeline.py")
    log_path = os.path.join(os.path.dirname(__file__), '..', 'ingest.log')
    
    asyncio.create_task(run_job_in_background(job_id, "Ingest Pipeline", [sys.executable, "-u", script_path], log_path))
    return {"status": "accepted", "jobId": job_id, "message": "Ingest pipeline started"}

@app.post("/api/fits/run")
async def trigger_fits(_: None = Depends(verify_token)):
    job_id = str(uuid.uuid4())
    conn = get_db()
    conn.execute("INSERT INTO JobExecutions (id, name, status, created_at) VALUES (?, ?, ?, ?)",
                 (job_id, "Fit Pipeline", "pending", datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    log_activity("Started Fit Pipeline", "AI", "Triggered run_fit_fast.py via dashboard")
    script_path = os.path.join(os.path.dirname(__file__), '..', '..', 'helper', 'run_fit_fast.py')
    log_path = os.path.join(os.path.dirname(__file__), '..', 'fits.log')
    
    asyncio.create_task(run_job_in_background(job_id, "Fit Pipeline", ["python3", script_path], log_path))
    return {"status": "accepted", "jobId": job_id, "message": "Fit runs started"}
