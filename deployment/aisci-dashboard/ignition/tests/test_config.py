import os
import pytest
from config import validate_paths, REPO_ROOT, EVIDENCE_FILE

def test_repo_root_is_absolute():
    assert os.path.isabs(REPO_ROOT)
    assert os.path.basename(REPO_ROOT) == "aisci"

def test_evidence_file_path():
    assert os.path.isabs(EVIDENCE_FILE)
    assert "evidence-ledger.md" in EVIDENCE_FILE

def test_validate_paths_no_error(monkeypatch):
    # Mock os.path.exists to always return True
    monkeypatch.setattr(os.path, "exists", lambda path: True)
    # Should not raise
    validate_paths()

def test_validate_paths_raises(monkeypatch):
    # Mock os.path.exists to always return False
    monkeypatch.setattr(os.path, "exists", lambda path: False)
    with pytest.raises(RuntimeError, match="Missing required canonical paths"):
        validate_paths()
