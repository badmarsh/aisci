import pytest
from fastapi.testclient import TestClient
import uuid
import sqlite3
import os
from api import app
from database import get_connection

client = TestClient(app)

def test_retry_failed_job(tmp_path):
    project_id = "robert-boson-manuscript"
    conn = get_connection(project_id)

    # Insert a failed job
    job_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO JobExecutions (id, project_id, pipeline_id, name, requester, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (job_id, project_id, "fit-validation", "Fit Pipeline", "Test", "failed", "2026-07-01T00:00:00", "2026-07-01T00:00:00")
    )
    conn.commit()
    conn.close()

    # Hit the retry endpoint
    response = client.post(f"/api/projects/{project_id}/jobs/{job_id}/retry")
    assert response.status_code == 200
    data = response.json()
    new_job_id = data["id"]

    # Verify new job
    conn = get_connection(project_id)
    cursor = conn.cursor()
    cursor.execute("SELECT status, retry_of_job_id FROM JobExecutions WHERE id=?", (new_job_id,))
    row = cursor.fetchone()
    conn.close()

    assert row["status"] == "pending"
    assert row["retry_of_job_id"] == job_id

def test_retry_pending_job_fails():
    project_id = "robert-boson-manuscript"
    conn = get_connection(project_id)

    # Insert a pending job
    job_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO JobExecutions (id, project_id, pipeline_id, name, requester, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (job_id, project_id, "fit-validation", "Fit Pipeline", "Test", "pending", "2026-07-01T00:00:00", "2026-07-01T00:00:00")
    )
    conn.commit()
    conn.close()

    # Hit the retry endpoint
    response = client.post(f"/api/projects/{project_id}/jobs/{job_id}/retry")
    assert response.status_code == 400
    assert "Only failed jobs can be retried" in response.json()["detail"]
