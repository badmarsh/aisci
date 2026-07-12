import pytest
from fastapi.testclient import TestClient
import json
from api import app
from database import get_connection

client = TestClient(app)

def test_evidence_review_flow(tmp_path):
    project_id = "robert-boson-manuscript"
    conn = get_connection(project_id)

    # 1. Clear database
    conn.execute("DELETE FROM Evidence WHERE project_id = ?", (project_id,))
    conn.commit()

    # 2. Insert initial evidence
    conn.execute(
        "INSERT INTO Evidence (project_id, claim, status, nextGate, run, narrative) VALUES (?, ?, ?, ?, ?, ?)",
        (project_id, "Test claim", "Proposed", "None", "—", "Test Narrative")
    )
    conn.commit()

    cursor = conn.cursor()
    cursor.execute("SELECT id FROM Evidence WHERE claim = 'Test claim'")
    ev_id = cursor.fetchone()["id"]

    # 3. Request review
    resp = client.patch(f"/api/projects/{project_id}/evidence/{ev_id}", json={"status": "Sanity checked"})
    assert resp.status_code == 200
    req_id = resp.json()["requestId"]

    # 4. Approve review
    resp = client.post(f"/api/projects/{project_id}/review-requests/{req_id}/approve")
    assert resp.status_code == 200

    # 5. Check history
    cursor.execute("SELECT status_history FROM Evidence WHERE id = ?", (ev_id,))
    history_str = cursor.fetchone()["status_history"]
    history = json.loads(history_str)

    assert len(history) == 1
    assert history[0]["from"] == "Proposed"
    assert history[0]["to"] == "Sanity checked"

    conn.close()
