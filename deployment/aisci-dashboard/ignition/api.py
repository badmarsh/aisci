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
from config import AUTH_TOKEN, ENVIRONMENT, ALLOWED_ORIGINS
import fit_parser
from validation_policy import default_policy
from project_registry import registry, ProjectSpec
from pipelines import registry as pipeline_registry

app = FastAPI(title="AiSci Dashboard API")

def verify_token(authorization: Optional[str] = Header(None)):
    """
    Security contract: In production, AISCI_DASHBOARD_TOKEN must be set to ensure mutations are authenticated.
    In local development, the token is optional but enforced if provided.
    """
    if ENVIRONMENT == "production" and not AUTH_TOKEN:
        raise HTTPException(status_code=500, detail="Production environment requires AISCI_DASHBOARD_TOKEN to be set")
    if AUTH_TOKEN and authorization != f"Bearer {AUTH_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.on_event("startup")
async def startup():
    init_db()
    for p in registry.list_projects():
        sync_markdown.sync_evidence_to_db(p.id)
        sync_markdown.sync_tasks_to_db(p.id)

# Allow requests from Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from database import get_connection

def get_latest_run_path(project_id: str) -> str:
    """Return the most recently modified run directory that contains fit_quality.csv for a given project."""
    spec = registry.get_project(project_id)
    runs_base = spec.get_runs_dir()
    if not os.path.exists(runs_base):
        raise FileNotFoundError(f"Runs directory not found for project {project_id}.")
    candidates = [
        d for d in os.listdir(runs_base)
        if os.path.isdir(os.path.join(runs_base, d))
        and os.path.exists(os.path.join(runs_base, d, 'fit_quality.csv'))
    ]
    if not candidates:
        raise FileNotFoundError(f"No completed run directories found for project {project_id}.")
    return os.path.join(runs_base, sorted(candidates)[-1])

def list_run_dirs(project_id: str) -> list[str]:
    """Return all run directory names, newest first, for a given project."""
    spec = registry.get_project(project_id)
    runs_base = spec.get_runs_dir()
    if not os.path.exists(runs_base):
        return []
    candidates = [
        d for d in os.listdir(runs_base)
        if os.path.isdir(os.path.join(runs_base, d))
    ]
    return sorted(candidates, reverse=True)

def get_db():
    return get_connection()

def log_activity(project_id: str, action: str, user: str, details: str):
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO ActivityLogs (project_id, timestamp, action, user, details)
            VALUES (?, datetime('now'), ?, ?, ?)
        ''', (project_id, action, user, details))
        conn.commit()
    finally:
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

@app.get("/api/projects")
def get_projects():
    # Return all registered projects
    projects = []
    for pid, spec in registry._projects.items():
        projects.append({
            "id": pid,
            "title": spec.title,
            "owner": spec.owner,
            "research_type": spec.research_type,
            "sensitivity": spec.sensitivity,
            "capabilities": spec.capabilities
        })
    return projects

@app.get("/api/projects/{project_id}/pipelines")
def get_pipelines(project_id: str):
    spec = registry.get_project(project_id)
    pipelines = pipeline_registry.get_pipelines_for_project(spec)
    
    # Do pre-flight checks and return availability
    result = []
    for p in pipelines:
        status = "available"
        if p.requires_input:
            input_path = os.path.join(p.working_dir, p.requires_input)
            if not os.path.exists(input_path):
                status = f"unavailable: missing {p.requires_input}"
        
        result.append({
            "id": p.id,
            "name": p.name,
            "status": status,
            "requires_input": p.requires_input
        })
    return result

@app.get("/api/projects/{project_id}/literature", response_model=List[Paper])
def get_literature(project_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Papers WHERE project_id = ?", (project_id,))
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
            "category": p['category'],
            "title": p['title'],
            "published": p['published_date'],
            "claims": len(claim_list),
            "bridge": bridge,
            "abstract": p['abstract'],
            "url": p['url'],
            "claimList": claim_list,
            "provenance": p['provenance'],
            "source_hash": p['source_hash']
        })
    conn.close()
    
    return result

class IngestClaim(BaseModel):
    text: str
    confidence: str = "LOW"
    type: str = "Supporting"

class IngestPaperRequest(BaseModel):
    id: str
    title: str
    abstract: str
    published: str
    url: str
    category: str
    provenance: Optional[str] = None
    source_hash: Optional[str] = None
    claims: Optional[List[IngestClaim]] = None
    datasets: Optional[List[str]] = None

@app.post("/api/projects/{project_id}/literature")
def ingest_literature(project_id: str, req: IngestPaperRequest, _: None = Depends(verify_token)):
    from database import insert_paper, insert_claim, insert_dataset
    insert_paper(req.id, project_id, req.title, req.abstract, req.published, req.url, req.category, req.provenance, req.source_hash)
    if req.claims:
        for claim in req.claims:
            insert_claim(req.id, claim.text, claim.confidence, claim.type)
    if req.datasets:
        for dataset in req.datasets:
            insert_dataset(req.id, dataset)
    log_activity(project_id, "Ingested Literature", "System", f"Ingested paper: {req.title}")
    return {"status": "success", "id": req.id}

@app.get("/api/projects/{project_id}/evidence", response_model=List[EvidenceRow])
def get_evidence(project_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Evidence WHERE project_id = ?", (project_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.patch("/api/projects/{project_id}/evidence/{evidence_id}")
def update_evidence(project_id: str, evidence_id: int, body: StatusUpdate, _: None = Depends(verify_token)):
    req_id = str(uuid.uuid4())
    conn = get_db()
    conn.execute(
        "INSERT INTO ReviewDecisions (id, project_id, target_id, requested_state, reviewer, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (req_id, project_id, str(evidence_id), body.status, "User", "Proposed", datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    log_activity(project_id, "Review Requested", "User", f"Requested evidence #{evidence_id} status change to {body.status}")
    return {"status": "review_requested", "requestId": req_id}

@app.get("/api/projects/{project_id}/fits")
def get_fits(project_id: str, run: Optional[str] = None, compare_run: Optional[str] = None):
    try:
        spec = registry.get_project(project_id)
        runs_base = spec.get_runs_dir()
        run_path = os.path.join(runs_base, run) if run else get_latest_run_path(project_id)
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
            cmp_path = os.path.join(runs_base, compare_run)
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

@app.get("/api/projects/{project_id}/fits/runs")
def get_fit_runs(project_id: str):
    return {"runs": list_run_dirs(project_id)}

class AnomalyItem(BaseModel):
    bin: str
    model: str
    type: str      # "chi2" | "correlation" | "boundary"
    severity: str  # "critical" | "warning"
    message: str
    value: float

@app.get("/api/projects/{project_id}/anomalies", response_model=List[AnomalyItem])
def get_anomalies(project_id: str, run: Optional[str] = None):
    """Scan the latest (or specified) run for physics anomalies using ValidationPolicy."""
    try:
        spec = registry.get_project(project_id)
        runs_base = spec.get_runs_dir()
        run_path = os.path.join(runs_base, run) if run else get_latest_run_path(project_id)
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

@app.get("/api/projects/{project_id}/export/summary")
def get_export_summary(project_id: str):
    """Generates a text summary of the current project state for GitHub Issues/Logs."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get active fits count
    active_fits_count = 0
    try:
        run_path = get_latest_run_path(project_id)
        if run_path:
            qual = pd.read_csv(os.path.join(run_path, "fit_quality.csv"))
            active_fits_count = len(qual)
    except Exception:
        pass

    # Get anomalies
    anomalies = get_anomalies(project_id)
    anom_str = f"Found {len(anomalies)} anomalies in latest run.\n"
    if anomalies:
        for a in anomalies[:5]:
            anom_str += f"- [{a.bin}] {a.model}: {a.message}\n"
        if len(anomalies) > 5:
            anom_str += f"- ... and {len(anomalies)-5} more.\n"
    else:
        anom_str = "No physics anomalies detected in latest run.\n"

    # Get evidence pending review
    cursor.execute("SELECT count(*) FROM Evidence WHERE status='Proposed' AND project_id=?", (project_id,))
    evidence_pending = cursor.fetchone()[0]

    # Get open tasks
    cursor.execute("SELECT count(*) FROM Tasks WHERE status != 'closed' AND project_id=?", (project_id,))
    open_tasks = cursor.fetchone()[0]

    # Get latest literature
    cursor.execute("SELECT count(*) FROM Papers WHERE project_id=?", (project_id,))
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


@app.get("/api/projects/{project_id}/tasks", response_model=List[TaskModel])
def get_tasks(project_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Tasks WHERE project_id = ?", (project_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.patch("/api/projects/{project_id}/tasks/{task_id}")
def update_task(project_id: str, task_id: str, body: StatusUpdate, _: None = Depends(verify_token)):
    req_id = str(uuid.uuid4())
    conn = get_db()
    conn.execute(
        "INSERT INTO ReviewDecisions (id, project_id, target_id, requested_state, reviewer, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (req_id, project_id, task_id, body.status, "User", "Proposed", datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    log_activity(project_id, "Review Requested", "User", f"Requested task {task_id} status change to {body.status}")
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
    """
    Generator that yields new lines from a log file as they are written.
    Note: The time.sleep() call is safe here because this synchronous generator 
    is automatically run in a thread pool by FastAPI, so it won't block the main event loop.
    """
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

@app.get("/api/projects/{project_id}/logs/{pipeline_id}")
def stream_pipeline_log(project_id: str, pipeline_id: str):
    spec = registry.get_project(project_id)
    if not spec:
        raise HTTPException(status_code=404, detail="Project not found")
    
    runs_dir = spec.get_runs_dir()
    log_path = os.path.join(runs_dir, f"{pipeline_id}_latest.log")
    
    if not os.path.exists(log_path):
        return StreamingResponse(iter(["data: {\"line\": \"No logs found.\\n\"}\n\n"]), media_type="text/event-stream")
        
    return stream_log_file(log_path)

class ActivityModel(BaseModel):
    id: int
    timestamp: str
    action: str
    user: str
    details: str

@app.get("/api/projects/{project_id}/activity", response_model=List[ActivityModel])
def get_activity(project_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ActivityLogs WHERE project_id = ? ORDER BY id DESC LIMIT 50", (project_id,))
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

@app.post("/api/projects/{project_id}/sync")
async def manual_sync(project_id: str, _: None = Depends(verify_token)):
    """Force a re-sync from canonical Markdown files. Call after external agent writes."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, sync_markdown.sync_evidence_to_db, project_id)
    await loop.run_in_executor(None, sync_markdown.sync_tasks_to_db, project_id)
    log_activity(project_id, "Manual Sync", "User", f"Re-synced Evidence and Tasks for project {project_id}.")
    return {"status": "ok", "message": "Synced from evidence-ledger.md and next-actions.md"}

@app.post("/api/projects/{project_id}/materialize")
async def materialize_decisions(project_id: str, _: None = Depends(verify_token)):
    """Apply all 'Proposed' review decisions to the canonical Markdown files safely."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, sync_markdown.materialize_approved_decisions, project_id)
    return {"status": "ok", "message": "Materialized approved decisions to canonical files."}



@app.post("/api/projects/{project_id}/pipelines/{pipeline_id}/run")
async def trigger_pipeline(project_id: str, pipeline_id: str, _: None = Depends(verify_token)):
    spec = registry.get_project(project_id)
    pipeline_spec = pipeline_registry.get_pipeline(spec, pipeline_id)
    
    if pipeline_spec.requires_input:
        input_path = os.path.join(pipeline_spec.working_dir, pipeline_spec.requires_input)
        if not os.path.exists(input_path):
            raise HTTPException(status_code=400, detail=f"Cannot run pipeline: missing required input '{pipeline_spec.requires_input}'")
    
    job_id = str(uuid.uuid4())
    conn = get_db()
    
    try:
        cursor = conn.cursor()
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute("SELECT id FROM JobExecutions WHERE project_id = ? AND pipeline_id = ? AND status IN ('pending', 'running')", 
                       (project_id, pipeline_id))
        active = cursor.fetchone()
        if active:
            conn.rollback()
            raise HTTPException(status_code=409, detail=f"Job {active['id']} is already running for pipeline {pipeline_id}.")
            
        cursor.execute(
            "INSERT INTO JobExecutions (id, project_id, pipeline_id, name, requester, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (job_id, project_id, pipeline_id, pipeline_spec.name, "User", "pending", datetime.now().isoformat())
        )
        conn.commit()
    finally:
        conn.close()
    
    log_activity(project_id, f"Started Pipeline: {pipeline_spec.name}", "User", f"Triggered {pipeline_id} via dashboard")
    
    # Use project runs directory for logs
    runs_dir = spec.get_runs_dir()
    os.makedirs(runs_dir, exist_ok=True)
    log_path = os.path.join(runs_dir, f"{job_id}.log")
    
    # Removed asyncio.create_task to rely on standalone worker.
    return {"status": "ok", "message": "Job queued", "job_id": job_id}

@app.get("/api/projects/{project_id}/review-requests")
def get_review_requests(project_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ReviewDecisions WHERE project_id = ?", (project_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/api/projects/{project_id}/jobs")
def get_jobs(project_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM JobExecutions WHERE project_id = ? ORDER BY created_at DESC", (project_id,))
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        d = dict(r)
        if d.get('artifact_manifest'):
            try:
                d['artifact_manifest'] = json.loads(d['artifact_manifest'])
            except Exception:
                d['artifact_manifest'] = []
        else:
            d['artifact_manifest'] = []
        results.append(d)
    return results

@app.get("/api/projects/{project_id}/jobs/{job_id}")
def get_job(project_id: str, job_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM JobExecutions WHERE project_id = ? AND id = ?", (project_id, job_id))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
        
    d = dict(row)
    if d.get('artifact_manifest'):
        try:
            d['artifact_manifest'] = json.loads(d['artifact_manifest'])
        except Exception:
            d['artifact_manifest'] = []
    else:
        d['artifact_manifest'] = []
    return d
