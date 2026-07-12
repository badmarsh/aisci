import os
import json
import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import StreamingResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import asyncio
import sys
import time
import uuid
sys.path.insert(0, os.path.dirname(__file__))
import sync_markdown
from datetime import datetime

from database import init_db
from config import AUTH_TOKEN, ENVIRONMENT, ALLOWED_ORIGINS
import fit_parser
from validation_policy import default_policy
from project_registry import registry, ProjectSpec
from pipelines import registry as pipeline_registry
from idea_generator import IdeaGenerator

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
    for p in registry.list_projects():
        init_db(p.id)
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
    candidates.sort(key=lambda d: os.path.getmtime(os.path.join(runs_base, d)))
    return os.path.join(runs_base, candidates[-1])

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
    candidates.sort(key=lambda d: os.path.getmtime(os.path.join(runs_base, d)), reverse=True)
    return candidates

def get_db(project_id: str):
    return get_connection(project_id)

def log_activity(project_id: str, action: str, user: str, details: str):
    conn = get_db(project_id)
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
    review_status: str = "Proposed"
    status_history: List[Dict[str, Any]] = []

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
    provider: Optional[str] = None

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
    
    result = []
    for p in pipelines:
        res = p.dry_run()
        result.append({
            "id": res["id"],
            "name": res["name"],
            "status": res["status"],
            "requires_input": res["requires_input"],
            "available": res["available"],
            "checks": res["checks"]
        })
    return result

PHYSICS_BRIDGE_CATEGORIES = {"nucl-ex", "nucl-th", "hep-ph", "hep-ex", "cs.AI+nucl", "quant-ph"}

@app.get("/api/projects/{project_id}/literature", response_model=List[Paper])
def get_literature(project_id: str):
    spec = registry.get_project(project_id)
    conn = get_db(project_id)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Papers WHERE project_id = ?", (project_id,))
    papers_rows = cursor.fetchall()
    
    result = []
    for p in papers_rows:
        cursor.execute("SELECT claim_text, confidence FROM Claims WHERE paper_id = ?", (p['id'],))
        claims_rows = cursor.fetchall()
        
        claim_list = [{"text": c["claim_text"], "confidence": c["confidence"]} for c in claims_rows]
        
        source = p['provenance'] or ("OpenAlex" if p['id'].startswith("W") else "arXiv")
        bridge = p['category'] in PHYSICS_BRIDGE_CATEGORIES
        
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
    spec = registry.get_project(project_id)
    from database import insert_paper, insert_claim, insert_dataset
    inserted = insert_paper(req.id, project_id, req.title, req.abstract, req.published, req.url, req.category, req.provenance, req.source_hash)
    if not inserted:
        log_activity(project_id, "Duplicate Skipped", "System", f"Skipped duplicate paper: {req.title}")
        return {"status": "skipped", "message": "Duplicate paper skipped", "id": req.id}
    if req.claims:
        for claim in req.claims:
            insert_claim(project_id, req.id, claim.text, claim.confidence, claim.type)
    if req.datasets:
        for dataset in req.datasets:
            insert_dataset(project_id, req.id, dataset)
    log_activity(project_id, "Ingested Literature", "System", f"Ingested paper: {req.title}")
    return {"status": "success", "id": req.id}

@app.get("/api/projects/{project_id}/evidence", response_model=List[EvidenceRow])
def get_evidence(project_id: str):
    spec = registry.get_project(project_id)
    conn = get_db(project_id)
    cursor = conn.cursor()
    query = """
        SELECT e.*, 
               COALESCE(
                   (SELECT status 
                    FROM ReviewDecisions rd 
                    WHERE rd.target_id = CAST(e.id AS TEXT) 
                      AND rd.project_id = e.project_id 
                    ORDER BY created_at DESC LIMIT 1), 
                   'Proposed'
               ) as review_status
        FROM Evidence e
        WHERE e.project_id = ?
    """
    cursor.execute(query, (project_id,))
    rows = cursor.fetchall()
    
    evidence_list = []
    for r in rows:
        row_dict = dict(r)
        # Fetch history
        cursor.execute("""
            SELECT requested_state as to_state, reviewer, created_at as timestamp 
            FROM ReviewDecisions 
            WHERE target_id = ? AND project_id = ? 
            ORDER BY created_at ASC
        """, (str(row_dict['id']), project_id))
        history_rows = cursor.fetchall()
        history = [{"to": hr["to_state"], "reviewer": hr["reviewer"], "timestamp": hr["timestamp"]} for hr in history_rows]
        
        # We can simulate a 'from' state by looking at the previous row
        for i, h in enumerate(history):
            h["from"] = "Proposed" if i == 0 else history[i-1]["to"]
            
        row_dict["status_history"] = history
        evidence_list.append(row_dict)
        
    conn.close()
    return evidence_list

@app.patch("/api/projects/{project_id}/evidence/{evidence_id}")
def update_evidence(project_id: str, evidence_id: int, body: StatusUpdate, _: None = Depends(verify_token)):
    spec = registry.get_project(project_id)
    req_id = str(uuid.uuid4())
    conn = get_db(project_id)
    conn.execute(
        "INSERT INTO ReviewDecisions (id, project_id, target_id, requested_state, reviewer, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (req_id, project_id, str(evidence_id), body.status, "User", "Approved", datetime.now().isoformat())
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
        
        ndf_val = row.get('ndf')
        if pd.isna(ndf_val) or ndf_val is None:
            # Estimate NDF if not directly in the CSV
            model_raw = row['model_name']
            bin_label = row['group_label']
            k = 3
            if not parsed["params_df"].empty:
                k = len(parsed["params_df"][(parsed["params_df"]['group_label'] == bin_label) & (parsed["params_df"]['model_name'] == model_raw)])
                if k == 0:
                    k = 6 if "2c" in model_raw else (4 if "bgbw" in model_raw else 3)
            else:
                k = 6 if "2c" in model_raw else (4 if "bgbw" in model_raw else 3)
            ndf_val = 47 - k
            
        sev, msg = default_policy.validate_chi2(chi2_val, ndf=int(ndf_val))
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
        m_nice = fit_parser.parse_model_name(row['model_name'])
        
        # Check for T-q degeneracy specifically
        deg_sev, deg_msg = default_policy.validate_t_q_degeneracy(rho, row['model_name'], row['parameter_left'], row['parameter_right'])
        if deg_sev != "ok":
            anomalies.append(AnomalyItem(
                bin=row['group_label'], model=m_nice, type="degeneracy", severity=deg_sev,
                message=deg_msg, value=abs(rho)
            ))
            continue
            
        sev, msg = default_policy.validate_correlation(rho, row['parameter_left'], row['parameter_right'])
        if sev != "ok":
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
        elif pname in ['temperature_1', 'T_kin', 'T_stat']:
            feed_down_corrected = "fd" in row['model_name'].lower() or "feed_down" in row['model_name'].lower()
            sev, msg = default_policy.validate_temperature(val, feed_down_corrected=feed_down_corrected)
            if sev != "ok":
                anomalies.append(AnomalyItem(
                    bin=row['group_label'], model=m_nice, type="boundary", severity=sev,
                    message=msg, value=val
                ))

    return anomalies

@app.get("/api/projects/{project_id}/export/summary")
def get_export_summary(project_id: str):
    """Generates a text summary of the current project state for GitHub Issues/Logs."""
    spec = registry.get_project(project_id)
    conn = get_db(project_id)
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

@app.get("/api/projects/{project_id}/export/bibtex", response_class=PlainTextResponse)
def export_bibtex(project_id: str):
    conn = get_db(project_id)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Papers WHERE project_id = ?", (project_id,))
    papers = cursor.fetchall()
    conn.close()
    
    bibtex_entries = []
    for i, p in enumerate(papers):
        year = p["published_date"][:4] if p["published_date"] else "unknown"
        first_word = p["title"].split()[0].lower() if p["title"] else "unknown"
        first_word = "".join(c for c in first_word if c.isalnum())
        cite_key = f"{first_word}{year}{i}"
        
        bibtex = f"@article{{{cite_key},\n"
        bibtex += f"  title = {{{p['title']}}},\n"
        bibtex += f"  year = {{{year}}},\n"
        if p['url']:
            bibtex += f"  url = {{{p['url']}}},\n"
        bibtex += f"  note = {{Source: {p['provenance'] or p['id']}}}\n"
        bibtex += "}\n"
        bibtex_entries.append(bibtex)
        
    return "\n".join(bibtex_entries)

@app.get("/api/projects/{project_id}/overview")
def get_project_overview(project_id: str):
    spec = registry.get_project(project_id)
    conn = get_db(project_id)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM Papers WHERE project_id=?", (project_id,))
    lit_count = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM Evidence WHERE project_id=?", (project_id,))
    claims_count = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM Tasks WHERE status != 'closed' AND project_id=?", (project_id,))
    open_tasks = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM JobExecutions WHERE status IN ('pending', 'running') AND project_id=?", (project_id,))
    active_jobs = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM JobExecutions WHERE status = 'completed' AND project_id=?", (project_id,))
    completed_jobs = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM JobExecutions WHERE status = 'failed' AND project_id=?", (project_id,))
    failed_jobs = cursor.fetchone()[0]
    
    # Check worker health: if there are running jobs with no update in 5 mins, maybe sick?
    # Actually, if there is a running worker process. We'll just set it to True for now, or check JobExecutions.
    worker_health = True
    
    conn.close()
    
    active_fits_count = 0
    anomalies_count = 0
    try:
        run_path = get_latest_run_path(project_id)
        if run_path:
            qual = pd.read_csv(os.path.join(run_path, "fit_quality.csv"))
            active_fits_count = len(qual)
            
            anomalies = get_anomalies(project_id)
            anomalies_count = len(anomalies)
    except Exception:
        pass
        
    return {
        "literature_count": lit_count,
        "claims_count": claims_count,
        "open_tasks": open_tasks,
        "active_fits": active_fits_count,
        "active_jobs": active_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "anomalies_count": anomalies_count,
        "worker_health": worker_health
    }

@app.get("/api/projects/{project_id}/health")
def get_project_health(project_id: str):
    try:
        spec = registry.get_project(project_id)
        runs_base = spec.get_runs_dir()
        
        conn = get_db(project_id)
        cursor = conn.cursor()
        
        # Check for stalled jobs (e.g. running for > 1 hour)
        cursor.execute('''
            SELECT COUNT(*) FROM JobExecutions 
            WHERE project_id = ? AND status = 'running' 
            AND CAST((julianday('now') - julianday(updated_at)) * 24 * 60 AS INTEGER) > 60
        ''', (project_id,))
        stalled_jobs = cursor.fetchone()[0]
        conn.close()
        
        worker_health = stalled_jobs == 0
        
        return {
            "status": "ok", 
            "runs_dir_exists": os.path.exists(runs_base),
            "worker_health": worker_health,
            "stalled_jobs": stalled_jobs
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/projects/{project_id}/jobs/{job_id}/logs")
def stream_job_logs(project_id: str, job_id: str):
    spec = registry.get_project(project_id)
    conn = get_db(project_id)
    cursor = conn.cursor()
    cursor.execute("SELECT log_path FROM JobExecutions WHERE project_id = ? AND id = ?", (project_id, job_id))
    row = cursor.fetchone()
    conn.close()
    if not row or not row["log_path"]:
        return StreamingResponse(iter([f'data: {{"line": "No logs found for job {job_id}.\\n"}}\n\n']), media_type="text/event-stream")
    return stream_log_file(row["log_path"])

@app.get("/api/projects/{project_id}/tasks", response_model=List[TaskModel])
def get_tasks(project_id: str, exclude_done: bool = False):
    spec = registry.get_project(project_id)
    conn = get_db(project_id)
    cursor = conn.cursor()
    if exclude_done:
        cursor.execute("SELECT * FROM Tasks WHERE project_id = ? AND status != 'done'", (project_id,))
    else:
        cursor.execute("SELECT * FROM Tasks WHERE project_id = ?", (project_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.patch("/api/projects/{project_id}/tasks/{task_id}")
def update_task(project_id: str, task_id: str, body: StatusUpdate, _: None = Depends(verify_token)):
    spec = registry.get_project(project_id)
    req_id = str(uuid.uuid4())
    conn = get_db(project_id)
    conn.execute(
        "INSERT INTO ReviewDecisions (id, project_id, target_id, requested_state, reviewer, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (req_id, project_id, task_id, body.status, "User", "Approved", datetime.now().isoformat())
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
                while True:
                    line = f.readline()
                    if line:
                        yield f"data: {json.dumps({'line': line.rstrip()})}\n\n"
                    else:
                        yield f": keep-alive\n\n"
                        time.sleep(1.0)
        except FileNotFoundError:
            yield f"data: {json.dumps({'error': 'Log file not found: ' + filepath})}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@app.get("/api/projects/{project_id}/logs/{pipeline_id}")
def stream_pipeline_log(project_id: str, pipeline_id: str):
    spec = registry.get_project(project_id)
    conn = get_db(project_id)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT log_path FROM JobExecutions WHERE project_id = ? AND pipeline_id = ? ORDER BY created_at DESC LIMIT 1",
        (project_id, pipeline_id)
    )
    row = cursor.fetchone()
    conn.close()
    if not row or not row["log_path"]:
        return StreamingResponse(iter([f'data: {{"line": "No logs found for {pipeline_id}.\\n"}}\n\n']), media_type="text/event-stream")
    return stream_log_file(row["log_path"])

class ActivityModel(BaseModel):
    id: int
    timestamp: str
    action: str
    user: str
    details: str

@app.get("/api/projects/{project_id}/activity", response_model=List[ActivityModel])
def get_activity(project_id: str):
    conn = get_db(project_id)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ActivityLogs WHERE project_id = ? ORDER BY id DESC LIMIT 50", (project_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/api/projects/{project_id}/agents", response_model=List[AgentModel])
def get_agents(project_id: str):
    conn = get_db(project_id)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT pipeline_id, status, updated_at, log_path FROM JobExecutions WHERE project_id = ? ORDER BY updated_at DESC LIMIT 20",
        (project_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    pipelines_status = {}
    for r in rows:
        pid = r['pipeline_id']
        if pid not in pipelines_status:
            pipelines_status[pid] = r

    log_dir = os.path.join(os.path.dirname(__file__), '..')
    backend_log = os.path.join(log_dir, 'backend.log')
    
    agents = [{
        "name": "FastAPI Backend",
        "status": "ACTIVE",
        "last": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "summary": "Main API server process",
        "log": tail_log(backend_log),
        "provider": "System"
    }]

    ingest_job = pipelines_status.get("ingest-pipeline")
    if ingest_job:
        agents.append({
            "name": "Ingest Pipeline",
            "status": ingest_job["status"].upper(),
            "last": ingest_job["updated_at"],
            "summary": "Literature fetch and LLM extraction",
            "log": tail_log(ingest_job["log_path"]) if ingest_job["log_path"] else ["[No log]"],
            "provider": "Gemini Pro"
        })
    else:
        agents.append({
            "name": "Ingest Pipeline",
            "status": "IDLE",
            "last": "Never",
            "summary": "Literature fetch and LLM extraction",
            "log": ["[No log]"],
            "provider": "Gemini Pro"
        })

    fit_job = pipelines_status.get("fit-pipeline")
    if fit_job:
        agents.append({
            "name": "Fit Pipeline",
            "status": fit_job["status"].upper(),
            "last": fit_job["updated_at"],
            "summary": "Minuit physics fitting and validation",
            "log": tail_log(fit_job["log_path"]) if fit_job["log_path"] else ["[No log]"],
            "provider": "Minuit"
        })
    else:
        agents.append({
            "name": "Fit Pipeline",
            "status": "IDLE",
            "last": "Never",
            "summary": "Minuit physics fitting and validation",
            "log": ["[No log]"],
            "provider": "Minuit"
        })

    return agents

@app.post("/api/projects/{project_id}/sync")
async def manual_sync(project_id: str, _: None = Depends(verify_token)):
    """Force a re-sync from canonical Markdown files. Call after external agent writes."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: sync_markdown.sync_evidence_to_db(project_id, force=True))
    await loop.run_in_executor(None, lambda: sync_markdown.sync_tasks_to_db(project_id, force=True))
    log_activity(project_id, "Manual Sync", "User", f"Re-synced Evidence and Tasks for project {project_id}.")
    return {"status": "ok", "message": "Synced from evidence-ledger.md and next-actions.md"}

@app.post("/api/projects/{project_id}/review-requests/{decision_id}/approve")
def approve_review_decision(project_id: str, decision_id: str, _: None = Depends(verify_token)):
    conn = get_db(project_id)
    conn.execute("UPDATE ReviewDecisions SET status = 'Approved' WHERE id = ? AND project_id = ?", (decision_id, project_id))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.post("/api/projects/{project_id}/review-requests/{decision_id}/reject")
def reject_review_decision(project_id: str, decision_id: str, _: None = Depends(verify_token)):
    conn = get_db(project_id)
    conn.execute("UPDATE ReviewDecisions SET status = 'Rejected' WHERE id = ? AND project_id = ?", (decision_id, project_id))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.post("/api/projects/{project_id}/materialize")
async def materialize_decisions(project_id: str, _: None = Depends(verify_token)):
    """Apply all 'Approved' review decisions to the canonical Markdown files safely."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, sync_markdown.materialize_approved_decisions, project_id)
    return {"status": "ok", "message": "Materialized approved decisions to canonical files."}


@app.post("/api/projects/{project_id}/pipelines/{pipeline_id}/dry-run")
async def dry_run_pipeline(project_id: str, pipeline_id: str, _: None = Depends(verify_token)):
    spec = registry.get_project(project_id)
    try:
        pipeline_spec = pipeline_registry.get_pipeline(spec, pipeline_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    try:
        res = pipeline_spec.dry_run()
        return {"status": "ok", "dry_run": res}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/projects/{project_id}/ideas")
def get_ideas(project_id: str):
    generator = IdeaGenerator()
    return generator.brainstorm()

@app.post("/api/projects/{project_id}/pipelines/{pipeline_id}/run")
async def trigger_pipeline(project_id: str, pipeline_id: str, _: None = Depends(verify_token)):
    spec = registry.get_project(project_id)
    try:
        pipeline_spec = pipeline_registry.get_pipeline(spec, pipeline_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    res = pipeline_spec.dry_run()
    if not res["available"]:
        failed_checks = [c["name"] for c in res["checks"] if not c["passed"]]
        raise HTTPException(status_code=400, detail=f"Cannot run pipeline: failed dry run checks: {', '.join(failed_checks)}")
    
    job_id = str(uuid.uuid4())
    conn = get_db(project_id)
    
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
    spec = registry.get_project(project_id)
    conn = get_db(project_id)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ReviewDecisions WHERE project_id = ?", (project_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/api/projects/{project_id}/jobs")
def get_jobs(project_id: str):
    spec = registry.get_project(project_id)
    conn = get_db(project_id)
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
    spec = registry.get_project(project_id)
    conn = get_db(project_id)
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

@app.post("/api/projects/{project_id}/jobs/{job_id}/retry")
def retry_job(project_id: str, job_id: str, _: None = Depends(verify_token)):
    conn = get_db(project_id)
    cursor = conn.cursor()
    cursor.execute("SELECT pipeline_id FROM JobExecutions WHERE id = ? AND project_id = ?", (job_id, project_id))
    job = cursor.fetchone()
    if not job:
        conn.close()
        raise HTTPException(status_code=404, detail="Job not found")
        
    cursor.execute("UPDATE JobExecutions SET status = 'pending', error = NULL, log_path = NULL, exit_code = NULL, artifact_manifest = NULL, updated_at = ? WHERE id = ?", (datetime.now().isoformat(), job_id))
    conn.commit()
    conn.close()
    return {"status": "retrying", "id": job_id}

@app.post("/api/projects/{project_id}/jobs/{job_id}/cancel")
def cancel_job(project_id: str, job_id: str, _: None = Depends(verify_token)):
    conn = get_db(project_id)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM JobExecutions WHERE id = ? AND project_id = ?", (job_id, project_id))
    job = cursor.fetchone()
    if not job:
        conn.close()
        raise HTTPException(status_code=404, detail="Job not found")
        
    if job['status'] in ('completed', 'failed', 'cancelled'):
        conn.close()
        raise HTTPException(status_code=400, detail="Cannot cancel a finished job")
        
    cursor.execute("UPDATE JobExecutions SET status = 'cancelled', updated_at = ? WHERE id = ?", (datetime.now().isoformat(), job_id))
    conn.commit()
    conn.close()
    return {"status": "cancelled", "id": job_id}
