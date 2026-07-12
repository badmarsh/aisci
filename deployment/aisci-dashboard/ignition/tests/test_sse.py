import pytest
from fastapi.testclient import TestClient
import uuid
import os
import json
from api import app
from database import get_connection

client = TestClient(app)

def test_sse_termination_on_job_completion(tmp_path):
    project_id = "robert-boson-manuscript"
    job_id = str(uuid.uuid4())
    log_file = tmp_path / "test_job.log"
    log_file.write_text("Log line 1\n")

    conn = get_connection(project_id)
    conn.execute(
        "INSERT INTO JobExecutions (id, project_id, pipeline_id, name, requester, status, log_path, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (job_id, project_id, "test-pipeline", "Test", "User", "running", str(log_file), "2026-07-01", "2026-07-01")
    )
    conn.commit()
    conn.close()

    # We will simulate the job finishing after the first yield
    # Because stream_log_file reads line by line, if we change the status, it should exit.

    def simulate_job_finish():
        conn = get_connection(project_id)
        conn.execute("UPDATE JobExecutions SET status = 'completed' WHERE id = ?", (job_id,))
        conn.commit()
        conn.close()

    # The test client will block until the stream completes.
    import threading
    timer = threading.Timer(0.5, simulate_job_finish)
    timer.start()

    response = client.get(f"/api/projects/{project_id}/jobs/{job_id}/logs")
    assert response.status_code == 200

    lines = list(response.iter_lines())

    # The stream should terminate, and the last event should be done: True
    # response.iter_lines() gives us chunks.
    found_done = False
    for line in lines:
        if "data:" in line:
            data_str = line.split("data: ")[1]
            try:
                data = json.loads(data_str)
                if data.get("done") is True:
                    found_done = True
            except:
                pass

    assert found_done is True
