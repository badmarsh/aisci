import os
import pytest
import shutil
import tempfile
import time
from database import init_db, get_connection, insert_paper, insert_claim
from project_registry import registry
from sync_markdown import sync_evidence_to_db, sync_tasks_to_db

def test_insert_paper_idempotence():
    project_id = "phd-audit"
    init_db(project_id)

    conn = get_connection(project_id)
    try:
        # Delete Claims first to satisfy foreign key constraint
        conn.execute("DELETE FROM Claims WHERE paper_id IN (SELECT id FROM Papers WHERE project_id = ?)", (project_id,))
        conn.execute("DELETE FROM Papers WHERE project_id = ?", (project_id,))
        conn.commit()
    finally:
        conn.close()

    # First insert
    res1 = insert_paper(
        paper_id="test-paper-123",
        project_id=project_id,
        title="Test Title",
        abstract="Test Abstract",
        published_date="2026",
        url="http://example.com",
        category="hep-ph",
        provenance="Test Ingestion",
        source_hash="hash-123"
    )
    assert res1 is True

    # Second insert of the same ID (should be ignored and return False)
    res2 = insert_paper(
        paper_id="test-paper-123",
        project_id=project_id,
        title="Test Title",
        abstract="Test Abstract",
        published_date="2026",
        url="http://example.com",
        category="hep-ph",
        provenance="Test Ingestion",
        source_hash="hash-123"
    )
    assert res2 is False

    # Insert with same source_hash but different ID (should be ignored and return False)
    res3 = insert_paper(
        paper_id="test-paper-456",
        project_id=project_id,
        title="Test Title",
        abstract="Test Abstract",
        published_date="2026",
        url="http://example.com",
        category="hep-ph",
        provenance="Test Ingestion",
        source_hash="hash-123"
    )
    assert res3 is False

def test_insert_claim_signature():
    project_id = "phd-audit"
    paper_id = "test-paper-123"

    conn = get_connection(project_id)
    try:
        conn.execute("DELETE FROM Claims WHERE paper_id = ?", (paper_id,))
        conn.commit()
    finally:
        conn.close()

    # Call with 5 parameters
    insert_claim(project_id, paper_id, "This is a claim", "HIGH", "Supporting")

    # Verify insert
    conn = get_connection(project_id)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT claim_text, confidence FROM Claims WHERE paper_id = ?", (paper_id,))
        row = cursor.fetchone()
        assert row is not None
        assert row["claim_text"] == "This is a claim"
        assert row["confidence"] == "HIGH"
    finally:
        conn.close()

def test_bridge_categories():
    from api import PHYSICS_BRIDGE_CATEGORIES
    assert "nucl-ex" in PHYSICS_BRIDGE_CATEGORIES
    assert "nucl-th" in PHYSICS_BRIDGE_CATEGORIES
    assert "hep-ph" in PHYSICS_BRIDGE_CATEGORIES
    assert "hep-ex" in PHYSICS_BRIDGE_CATEGORIES
    assert "cs.AI+nucl" in PHYSICS_BRIDGE_CATEGORIES
    assert "quant-ph" in PHYSICS_BRIDGE_CATEGORIES
    assert "cs.CL" not in PHYSICS_BRIDGE_CATEGORIES
    assert "cs.AI" not in PHYSICS_BRIDGE_CATEGORIES

def test_run_sorting_by_mtime(tmp_path):
    # Mock runs_base and check sorted order
    run1 = tmp_path / "2026-07-01-run"
    run2 = tmp_path / "2026-07-02-run"

    run1.mkdir()
    run2.mkdir()

    (run1 / "fit_quality.csv").write_text("dummy")
    (run2 / "fit_quality.csv").write_text("dummy")

    # Set modification times: run1 is newer than run2
    now = time.time()
    os.utime(run1, (now, now))
    os.utime(run2, (now - 100, now - 100))

    # Sort candidates
    candidates = ["2026-07-02-run", "2026-07-01-run"]
    candidates.sort(key=lambda d: os.path.getmtime(os.path.join(tmp_path, d)))

    # Newest should be last in sorted list
    assert candidates[-1] == "2026-07-01-run"

def test_hash_caching_skips_sync():
    project_id = "robert-boson-manuscript"
    init_db(project_id)

    # 1. Clear database
    conn = get_connection(project_id)
    try:
        conn.execute("DELETE FROM Evidence WHERE project_id = ?", (project_id,))
        conn.commit()
    finally:
        conn.close()

    # 2. Clear cache file
    spec = registry.get_project(project_id)
    runs_dir = spec.get_runs_dir()
    cache_path = os.path.join(runs_dir, ".sync_cache")
    if os.path.exists(cache_path):
        os.remove(cache_path)

    # 3. Call sync_evidence_to_db (first time, parses and populates cache)
    sync_evidence_to_db(project_id)

    # 4. Insert a custom row directly into SQLite
    conn = get_connection(project_id)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Evidence (project_id, claim, status, nextGate, run, narrative) VALUES (?, ?, ?, ?, ?, ?)",
            (project_id, "Custom Temporary Claim", "Proposed", "None", "—", "Custom Narrative")
        )
        conn.commit()
    finally:
        conn.close()

    # 5. Call sync_evidence_to_db again with force=False (should hit cache and skip)
    sync_evidence_to_db(project_id, force=False)

    # Verify the custom row is still there
    conn = get_connection(project_id)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM Evidence WHERE claim = ?", ("Custom Temporary Claim",))
        assert cursor.fetchone() is not None, "Expected sync to be skipped and custom claim preserved"
    finally:
        conn.close()

    # 6. Call sync_evidence_to_db with force=True (should bypass cache and delete the custom row)
    sync_evidence_to_db(project_id, force=True)
    conn = get_connection(project_id)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM Evidence WHERE claim = ?", ("Custom Temporary Claim",))
        assert cursor.fetchone() is None, "Expected sync to run and delete custom claim"
    finally:
        conn.close()
