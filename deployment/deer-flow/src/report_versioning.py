"""
Report Versioning
=================
Saves, lists, diffs, and restores prior report drafts.
One JSON file per version under REPORT_VERSIONS_DIR.

Usage:
    from src.report_versioning import ReportVersionStore
    store = ReportVersionStore()
    vid = store.save(run_id="abc123", report_text="# My Report\n...")
    versions = store.list_versions(run_id="abc123")
    old_text = store.load(version_id=vid)
    diff = store.diff(vid_a=versions[0]["id"], vid_b=versions[-1]["id"])
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any


class ReportVersionStore:
    """Filesystem-backed versioned report store."""

    def __init__(self, storage_dir: str | None = None) -> None:
        default = ".deer-flow/report_versions"
        self.dir = Path(storage_dir or os.getenv("REPORT_VERSIONS_DIR", default))
        self.dir.mkdir(parents=True, exist_ok=True)
        self.max_versions = int(os.getenv("REPORT_MAX_VERSIONS", "20"))

    def save(
        self,
        run_id: str,
        report_text: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Persist a version and return its version_id."""
        ts = int(time.time())
        content_hash = hashlib.sha256(report_text.encode()).hexdigest()[:12]
        version_id = f"{run_id}__{ts}__{content_hash}"
        record = {
            "version_id": version_id,
            "run_id": run_id,
            "saved_at": ts,
            "char_count": len(report_text),
            "metadata": metadata or {},
            "report": report_text,
        }
        path = self.dir / f"{version_id}.json"
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        self._prune(run_id)
        return version_id

    def list_versions(self, run_id: str) -> list[dict[str, Any]]:
        """Return version records newest-first (report text excluded)."""
        records = []
        for p in self.dir.glob(f"{run_id}__*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                records.append({k: v for k, v in data.items() if k != "report"})
            except (json.JSONDecodeError, OSError):
                continue
        return sorted(records, key=lambda r: r["saved_at"], reverse=True)

    def load(self, version_id: str) -> str:
        """Return the report text for a given version_id."""
        path = self.dir / f"{version_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Version not found: {version_id}")
        data = json.loads(path.read_text(encoding="utf-8"))
        return data["report"]

    def diff(self, vid_a: str, vid_b: str) -> str:
        """Return a unified diff between two versions."""
        import difflib
        text_a = self.load(vid_a).splitlines(keepends=True)
        text_b = self.load(vid_b).splitlines(keepends=True)
        return "".join(difflib.unified_diff(text_a, text_b, fromfile=vid_a, tofile=vid_b, lineterm=""))

    def _prune(self, run_id: str) -> None:
        for old in self.list_versions(run_id)[self.max_versions:]:
            try:
                (self.dir / f"{old['version_id']}.json").unlink(missing_ok=True)
            except OSError:
                pass
