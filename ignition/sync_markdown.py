import os
import re
import sqlite3
import threading

try:
    import fcntl
except ImportError:
    class fcntl:
        LOCK_EX = 0
        LOCK_UN = 0
        @staticmethod
        def flock(fd, op):
            pass

_file_lock = threading.RLock()

def _atomic_write(path: str, lines: list[str]) -> None:
    """Write lines to path with exclusive fcntl lock + threading lock."""
    with _file_lock:
        with open(path, 'r+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                f.seek(0)
                f.writelines(lines)
                f.truncate()
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

def get_db():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'evidence_graph.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

EVIDENCE_FILE = os.path.join(os.path.dirname(__file__), '..', 'research', 'robert', 'evidence-ledger.md')
TASKS_FILE = os.path.join(os.path.dirname(__file__), '..', 'research', 'robert', 'next-actions.md')

def sync_evidence_to_db():
    if not os.path.exists(EVIDENCE_FILE):
        return

    with open(EVIDENCE_FILE, 'r') as f:
        content = f.read()

    table_matches = re.finditer(
        r'\|\s*Claim\s*\|.*?\n\|[-| ]+\|\n((?:\|.*\|\n?)+)',
        content,
        re.DOTALL
    )
    
    rows = []
    row_id = 1
    for table_match in table_matches:
        for line in table_match.group(1).split('\n'):
            line = line.strip()
            if not line.startswith('|') or line.startswith('|---'):
                continue
            # Split on pipe, strip whitespace, drop first and last empty elements
            parts = [p.strip() for p in line.split('|')][1:-1]
            if len(parts) >= 5:
                # Columns: Claim | Evidence Required | Current Evidence | Status | Next Gate
                claim_text = parts[0]
                current_evidence = parts[2]  # narrative
                status = parts[3]
                next_gate = parts[4]
                # Normalise status — strip whitespace and handle case variants
                status_clean = status.strip()
                # Collapse <br> tags in narrative for DB storage
                narrative_clean = re.sub(r'<br\s*/?>', ' | ', current_evidence)
                rows.append({
                    "id": row_id,
                    "claim": claim_text,
                    "status": status_clean,
                    "nextGate": next_gate,
                    "run": "",
                    "narrative": narrative_clean[:2000],  # cap at 2000 chars for DB
                })
                row_id += 1

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Evidence")
    for r in rows:
        cursor.execute(
            "INSERT INTO Evidence (claim, status, nextGate, run, narrative) VALUES (?, ?, ?, ?, ?)",
            (r['claim'], r['status'], r['nextGate'], r['run'], r['narrative'])
        )
    conn.commit()
    conn.close()

def sync_db_to_evidence(evidence_id, new_status):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT claim FROM Evidence WHERE id = ?", (evidence_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return
    
    target_claim = row['claim'].strip()
    
    with open(EVIDENCE_FILE, 'r') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        if line.strip().startswith('|') and target_claim in line:
            parts = line.split('|')
            if len(parts) >= 6:
                parts[4] = f" {new_status} "
                lines[i] = "|".join(parts)
            break
            
    with _file_lock:
        _atomic_write(EVIDENCE_FILE, lines)
        sync_evidence_to_db()

def sync_tasks_to_db():
    if not os.path.exists(TASKS_FILE):
        return
        
    with open(TASKS_FILE, 'r') as f:
        content = f.read()
        
    tasks = []
    blocks = re.finditer(r'### \[([A-Z0-9-]+)\](.*?)\n\*\*Status:\*\* (.*?)\n(.*?)(?=\n### \[|\Z)', content, re.DOTALL)
    
    for match in blocks:
        task_id = match.group(1).strip()
        title = match.group(2).strip()
        status_line = match.group(3).strip()
        body = match.group(4).strip()
        
        desc_match = re.search(r'\*\*Context:\*\* (.*?)\n', body)
        description = desc_match.group(1).strip() if desc_match else title
        
        status_line_upper = status_line.upper()
        if "BLOCKED" in status_line_upper:
            status = "blocked"
        elif "ACTIVE" in status_line_upper:
            status = "active"
        else:
            status = "proposed"
            
        tasks.append({
            "id": task_id,
            "title": title,
            "description": description,
            "priority": "HIGH",
            "assignee": "AI",
            "date": "2026-07-09",
            "citation": "",
            "status": status
        })
        
    table_match = re.search(r'## ✅ Completed.*?\n\| Item \| Completed \| Notes \|\n\|---\|---\|---\|\n(.*?)(?=\n\n|\Z)', content, re.DOTALL)
    if table_match:
        for line in table_match.group(1).split('\n'):
            if line.strip().startswith('|'):
                parts = [p.strip() for p in line.split('|')][1:-1]
                if len(parts) >= 3:
                    title_match = re.search(r'\[(.*?)\] (.*)', parts[0])
                    if title_match:
                        task_id = title_match.group(1).strip()
                        title = title_match.group(2).strip()
                    else:
                        task_id = "c-" + parts[0][:10].replace(" ", "-")
                        title = parts[0]
                        
                    tasks.append({
                        "id": task_id,
                        "title": title,
                        "description": parts[2],
                        "priority": "LOW",
                        "assignee": "RB",
                        "date": parts[1],
                        "citation": "",
                        "status": "done"
                    })
                    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Tasks")
    for t in tasks:
        cursor.execute("INSERT INTO Tasks (id, title, description, priority, assignee, date, citation, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (t['id'], t['title'], t['description'], t['priority'], t['assignee'], t['date'], t['citation'], t['status']))
    conn.commit()
    conn.close()

def sync_db_to_tasks(task_id, new_status):
    with open(TASKS_FILE, 'r') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        if line.strip().startswith(f"### [{task_id}]"):
            if i + 1 < len(lines) and "**Status:**" in lines[i+1]:
                status_str = "Active" if new_status == "active" else "BLOCKED" if new_status == "blocked" else new_status.capitalize()
                lines[i+1] = f"**Status:** {status_str}\n"
            break
            
    with _file_lock:
        _atomic_write(TASKS_FILE, lines)
        sync_tasks_to_db()

if __name__ == '__main__':
    sync_evidence_to_db()
    sync_tasks_to_db()
    print("Markdown synced to DB.")
