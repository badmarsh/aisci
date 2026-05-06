#!/usr/bin/env python3
"""Patch Onyx background process monitoring for the current worker layout."""

from __future__ import annotations

from pathlib import Path
import re


TARGET = Path("/app/onyx/background/celery/tasks/monitoring/tasks.py")

PROCESS_TYPE_MAPPING = '''process_type_mapping = {
            "--hostname=primary": "primary",
            "--hostname=light": "light",
            "--hostname=heavy": "heavy",
            "--hostname=docprocessing": "docprocessing",
            "--hostname=docfetching": "docfetching",
            "--hostname=monitoring": "monitoring",
            "--hostname=user_file_processing": "user_file_processing",
            "celery.versioned_apps.beat": "beat",
            "slack/listener.py": "slack",
        }'''


def main() -> None:
    text = TARGET.read_text()
    text = re.sub(
        r"process_type_mapping = \{.*?\n        \}",
        PROCESS_TYPE_MAPPING,
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = text.replace(
        'f"Missing processes: {set(process_type_mapping.keys()).symmetric_difference(supervisor_processes.values())}"',
        'f"Missing processes: {set(process_type_mapping.values()) - set(supervisor_processes.values())}"',
    )
    TARGET.write_text(text)


if __name__ == "__main__":
    main()
