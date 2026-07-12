import os
import sys
import time
import subprocess
import json
import hashlib
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from database import get_connection
from project_registry import registry
from pipelines import registry as pipeline_registry

def get_db():
    return get_connection()

def get_git_commit(cwd):
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=cwd).decode('utf-8').strip()
    except Exception:
        return ""

def hash_file(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def compute_artifacts(runs_dir, job_start_time):
    manifest = []
    for root, _, files in os.walk(runs_dir):
        for f in files:
            path = os.path.join(root, f)
            try:
                mtime = os.path.getmtime(path)
                if mtime >= job_start_time:
                    manifest.append({
                        "path": os.path.relpath(path, runs_dir),
                        "sha256": hash_file(path),
                        "size": os.path.getsize(path)
                    })
            except Exception:
                pass
    return json.dumps(manifest)

def startup_recovery(project_id: str):
    conn = get_connection(project_id)
    cursor = conn.cursor()
    timeout_mins = int(os.environ.get("AISCI_WORKER_RECOVERY_MINUTES", "30"))
    cursor.execute('''
        UPDATE JobExecutions
        SET status = 'failed', error = 'Worker restart recovery: job was abandoned', updated_at = ?
        WHERE status = 'running' AND datetime(updated_at) < datetime('now', ?)
    ''', (datetime.now().isoformat(), f'-{timeout_mins} minutes'))
    conn.commit()
    conn.close()

def poll_and_run():
    for p in registry.list_projects():
        startup_recovery(p.id)
    print("Worker started. Polling for jobs...")
    timeout_secs = int(os.environ.get("AISCI_PIPELINE_TIMEOUT_SECONDS", "3600"))
    while True:
        job_id = None
        project_id = None
        pipeline_id = None

        # Poll each project
        for p in registry.list_projects():
            try:
                conn = get_connection(p.id)
                cursor = conn.cursor()
                cursor.execute("BEGIN IMMEDIATE")
                cursor.execute("SELECT id, project_id, pipeline_id FROM JobExecutions WHERE status = 'pending' ORDER BY created_at ASC LIMIT 1")
                job = cursor.fetchone()

                if job:
                    job_id = job['id']
                    project_id = job['project_id']
                    pipeline_id = job['pipeline_id']

                    spec = registry.get_project(project_id)
                    runs_dir = spec.get_runs_dir()
                    os.makedirs(runs_dir, exist_ok=True)
                    log_path = os.path.join(runs_dir, f"{job_id}.log")

                    cursor.execute("UPDATE JobExecutions SET status = 'running', log_path = ?, updated_at = ? WHERE id = ?",
                                   (log_path, datetime.now().isoformat(), job_id))
                    conn.commit()
                    conn.close()
                    break
                else:
                    conn.commit()
                    conn.close()
            except Exception:
                pass

        if not job_id:
            time.sleep(2)
            continue

        print(f"Picked up job {job_id} for pipeline {pipeline_id} in {project_id}")

        pipeline_spec = pipeline_registry.get_pipeline(spec, pipeline_id)

        job_start_time = time.time()
        process = None
        error_msg = None
        exit_code = None
        status = 'failed'

        with open(log_path, 'w') as f:
            try:
                process = subprocess.Popen(
                    pipeline_spec.command,
                    cwd=pipeline_spec.working_dir,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    preexec_fn=os.setsid
                )

                start_wait = time.time()
                while True:
                    retcode = process.poll()
                    if retcode is not None:
                        exit_code = retcode
                        status = 'completed' if exit_code == 0 else 'failed'
                        break

                    if time.time() - start_wait > timeout_secs:
                        import signal
                        try:
                            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                        except ProcessLookupError:
                            pass
                        process.wait()
                        error_msg = f"Job timed out after {timeout_secs} seconds"
                        exit_code = 124
                        status = 'failed'
                        break

                    try:
                        conn_check = get_connection(project_id)
                        cursor_check = conn_check.cursor()
                        cursor_check.execute("SELECT status FROM JobExecutions WHERE id = ?", (job_id,))
                        curr_status = cursor_check.fetchone()
                        conn_check.close()
                        if curr_status and curr_status['status'] == 'cancelled':
                            import signal
                            try:
                                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                            except ProcessLookupError:
                                pass
                            process.wait()
                            status = 'cancelled'
                            error_msg = "Job cancelled by user"
                            exit_code = 130
                            break
                    except Exception as e:
                        pass

                    time.sleep(2)
            except Exception as e:
                error_msg = f"Execution error: {str(e)}"
                exit_code = 1
                status = 'failed'

        try:
            conn = get_connection(project_id)
            cursor = conn.cursor()

            if status == 'completed':
                git_commit = get_git_commit(pipeline_spec.working_dir)
                artifact_manifest = compute_artifacts(runs_dir, job_start_time)
                cursor.execute('''
                    UPDATE JobExecutions
                    SET status = ?, exit_code = ?, updated_at = ?, git_commit = ?, artifact_manifest = ?
                    WHERE id = ?''',
                    (status, exit_code, datetime.now().isoformat(), git_commit, artifact_manifest, job_id))
            else:
                cursor.execute('''
                    UPDATE JobExecutions
                    SET status = ?, exit_code = ?, error = ?, updated_at = ?
                    WHERE id = ?''',
                    (status, exit_code, error_msg, datetime.now().isoformat(), job_id))

            conn.commit()
            conn.close()
            print(f"Job {job_id} {status}")
        except Exception as e:
            print(f"Worker db update error: {e}")
            if job_id:
                try:
                    conn = get_connection(project_id)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE JobExecutions SET status = 'failed', error = ?, updated_at = ? WHERE id = ?",
                                   (f"Worker crash: {str(e)}", datetime.now().isoformat(), job_id))
                    conn.commit()
                    conn.close()
                except Exception:
                    pass
            time.sleep(5)

if __name__ == "__main__":
    poll_and_run()
