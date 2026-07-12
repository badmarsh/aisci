import os
import sys
import time
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from database import get_connection
from project_registry import registry
from pipelines import registry as pipeline_registry

def get_db():
    return get_connection()

def poll_and_run():
    print("Worker started. Polling for jobs...")
    while True:
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # Find a pending job
            cursor.execute("SELECT id, project_id, pipeline_id FROM JobExecutions WHERE status = 'pending' ORDER BY created_at ASC LIMIT 1")
            job = cursor.fetchone()
            
            if not job:
                conn.close()
                time.sleep(2)
                continue
                
            job_id = job['id']
            project_id = job['project_id']
            pipeline_id = job['pipeline_id']
            
            print(f"Picked up job {job_id} for pipeline {pipeline_id}")
            
            # Update status to running
            spec = registry.get_project(project_id)
            runs_dir = spec.get_runs_dir()
            os.makedirs(runs_dir, exist_ok=True)
            log_path = os.path.join(runs_dir, f"{job_id}.log")
            
            cursor.execute("UPDATE JobExecutions SET status = 'running', log_path = ?, updated_at = ? WHERE id = ?",
                           (log_path, datetime.now().isoformat(), job_id))
            conn.commit()
            
            # Retrieve pipeline spec
            pipeline_spec = pipeline_registry.get_pipeline(spec, pipeline_id)
            
            # Execute
            with open(log_path, 'w') as f:
                process = subprocess.run(
                    pipeline_spec.command,
                    cwd=pipeline_spec.working_dir,
                    stdout=f,
                    stderr=subprocess.STDOUT
                )
                
            status = 'completed' if process.returncode == 0 else 'failed'
            
            # Update status
            cursor.execute("UPDATE JobExecutions SET status = ?, exit_code = ?, updated_at = ? WHERE id = ?",
                           (status, process.returncode, datetime.now().isoformat(), job_id))
            conn.commit()
            conn.close()
            print(f"Job {job_id} {status}")
            
        except Exception as e:
            print(f"Worker error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    poll_and_run()
