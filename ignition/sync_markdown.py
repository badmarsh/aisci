import os
import re
import sqlite3
import threading
from marko.ext.gfm import gfm

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

def _extract_text(node):
    if hasattr(node, 'children') and isinstance(node.children, list):
        return "".join(_extract_text(c) for c in node.children)
    elif hasattr(node, 'children') and isinstance(node.children, str):
        return node.children
    return ""

def sync_evidence_to_db():
    if not os.path.exists(EVIDENCE_FILE):
        return

    with open(EVIDENCE_FILE, 'r') as f:
        content = f.read()

    doc = gfm.parse(content)
    rows = []
    row_id = 1
    
    for child in doc.children:
        if child.__class__.__name__ == "Table":
            # first row is header
            for i, row in enumerate(child.children):
                if i == 0: continue # skip header
                cells = [_extract_text(cell) for cell in row.children]
                if len(cells) >= 5:
                    claim_text = cells[0].strip()
                    current_evidence = cells[2].strip()
                    status_clean = cells[3].strip()
                    next_gate = cells[4].strip()
                    
                    narrative_clean = re.sub(r'<br\s*/?>', ' | ', current_evidence)
                    rows.append({
                        "id": row_id,
                        "claim": claim_text,
                        "status": status_clean,
                        "nextGate": next_gate,
                        "run": "",
                        "narrative": narrative_clean[:2000],
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

    doc = gfm.parse(content)
    tasks = []
    
    current_task = None
    
    for child in doc.children:
        node_type = child.__class__.__name__
        
        if node_type == "Heading" and getattr(child, 'level', 0) == 3:
            heading_text = _extract_text(child).strip()
            # Expecting "### [TASK-ID] Title"
            m = re.match(r'^\[([A-Z0-9-]+)\](.*)', heading_text)
            if m:
                if current_task:
                    tasks.append(current_task)
                current_task = {
                    "id": m.group(1).strip(),
                    "title": m.group(2).strip(),
                    "description": "",
                    "priority": "HIGH",
                    "assignee": "AI",
                    "date": "2026-07-09",
                    "citation": "",
                    "status": "proposed"
                }
        elif current_task:
            text = _extract_text(child).strip()
            if text.startswith("**Status:**"):
                status_line = text.upper()
                if "BLOCKED" in status_line:
                    current_task["status"] = "blocked"
                elif "ACTIVE" in status_line:
                    current_task["status"] = "active"
                else:
                    current_task["status"] = "proposed"
            elif text.startswith("**Context:**"):
                current_task["description"] = text.replace("**Context:**", "").strip()
        
        if node_type == "Table":
            # Looking for Completed tasks table
            header = [_extract_text(c).strip() for c in child.children[0].children] if child.children else []
            if len(header) >= 3 and header[0] == "Item" and header[1] == "Completed":
                for i, row in enumerate(child.children):
                    if i == 0: continue
                    cells = [_extract_text(cell) for cell in row.children]
                    if len(cells) >= 3:
                        title_str = cells[0].strip()
                        date_str = cells[1].strip()
                        notes_str = cells[2].strip()
                        
                        m = re.match(r'^\[(.*?)\]\s*(.*)', title_str)
                        if m:
                            t_id = m.group(1).strip()
                            t_title = m.group(2).strip()
                        else:
                            t_id = "c-" + title_str[:10].replace(" ", "-")
                            t_title = title_str
                            
                        tasks.append({
                            "id": t_id,
                            "title": t_title,
                            "description": notes_str,
                            "priority": "LOW",
                            "assignee": "RB",
                            "date": date_str,
                            "citation": "",
                            "status": "done"
                        })

    if current_task:
        tasks.append(current_task)
                    
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
    print("Markdown synced to DB using AST parsing.")
