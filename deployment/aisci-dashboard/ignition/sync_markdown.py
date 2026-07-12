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

from database import get_connection
from project_registry import registry

def _extract_text(node):
    if hasattr(node, 'children') and isinstance(node.children, list):
        return "".join(_extract_text(c) for c in node.children)
    elif hasattr(node, 'children') and isinstance(node.children, str):
        return node.children
    return ""

def parse_evidence_markdown(filepath):
    """
    Parses evidence-ledger.md and returns a list of dictionaries.
    Looks for the Markdown table starting with '| Claim'.
    """
    evidence = []
    if not os.path.exists(filepath):
        return evidence
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    in_table = False
    for line in lines:
        if line.startswith('| Claim'):
            in_table = True
            continue
        if in_table and line.startswith('|-'):
            continue
        if in_table and line.startswith('|'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 6:
                claim = parts[1]
                evidence_req = parts[2]
                narrative = parts[3]
                status = parts[4]
                next_gate = parts[5]
                evidence.append({
                    "claim": claim,
                    "status": status,
                    "nextGate": next_gate,
                    "run": "—", # Parse this properly if needed
                    "narrative": narrative
                })
        if in_table and not line.strip():
            # End of table
            break
            
    return evidence

def sync_evidence_to_db(project_id: str):
    """Reads evidence-ledger.md and overwrites the Evidence table in SQLite."""
    spec = registry.get_project(project_id)
    filepath = spec.get_canonical_path("evidence-ledger.md")
    
    evidence_list = parse_evidence_markdown(filepath)
    if not evidence_list:
        return
        
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Evidence WHERE project_id=?", (project_id,))
    
    for ev in evidence_list:
        cursor.execute('''
            INSERT INTO Evidence (project_id, claim, status, nextGate, run, narrative)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (project_id, ev['claim'], ev['status'], ev['nextGate'], ev['run'], ev['narrative']))
        
    conn.commit()
    conn.close()

def _update_markdown_table_status(filepath: str, row_identifier: str, new_status: str, is_task: bool = False):
    """
    Finds a row in a Markdown table containing `row_identifier` and updates its status column.
    """
    if not os.path.exists(filepath):
        return

    with open(filepath, 'r') as f:
        lines = f.readlines()

    updated_lines = []
    in_table = False
    
    if not is_task:
        for line in lines:
            if line.startswith('| Claim'):
                in_table = True
                updated_lines.append(line)
                continue
            if in_table and line.startswith('|'):
                if row_identifier in line:
                    parts = line.split('|')
                    if len(parts) >= 6:
                        parts[4] = f" {new_status} "
                        line = '|'.join(parts)
            updated_lines.append(line)
            if in_table and not line.strip():
                in_table = False
    else:
        for line in lines:
            if row_identifier in line:
                if new_status.lower() in ['done', 'closed', 'completed']:
                    line = line.replace('[ ]', '[x]').replace('[/]', '[x]')
                elif new_status.lower() in ['active', 'in progress']:
                    line = line.replace('[ ]', '[/]').replace('[x]', '[/]')
            updated_lines.append(line)

    if lines != updated_lines:
        _atomic_write(filepath, updated_lines)

def materialize_approved_decisions(project_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, target_id, requested_state FROM ReviewDecisions WHERE status = 'Proposed' AND project_id = ?", (project_id,))
    decisions = cursor.fetchall()
    
    if not decisions:
        conn.close()
        return

    spec = registry.get_project(project_id)
    filepath = spec.get_canonical_path("evidence-ledger.md")

    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    changed = False
    for dec in decisions:
        evidence_id = dec['target_id']
        new_status = dec['requested_state']
        
        cursor.execute("SELECT claim FROM Evidence WHERE id = ? AND project_id = ?", (evidence_id, project_id))
        row = cursor.fetchone()
        if not row:
            continue
            
        target_claim = row['claim'].strip()
        for i, line in enumerate(lines):
            if line.strip().startswith('|') and target_claim in line:
                parts = line.split('|')
                if len(parts) >= 6:
                    parts[4] = f" {new_status} "
                    lines[i] = "|".join(parts)
                    changed = True
                break
                
        cursor.execute("UPDATE ReviewDecisions SET status = 'Applied' WHERE id = ?", (dec['id'],))
        
    if changed:
        with _file_lock:
            _atomic_write(filepath, lines)
            
    conn.commit()
    conn.close()
    
    if changed:
        sync_evidence_to_db(project_id)

def sync_tasks_to_db(project_id: str):
    spec = registry.get_project(project_id)
    filepath = spec.get_canonical_path("next-actions.md")
    if not os.path.exists(filepath):
        return
        
    with open(filepath, 'r') as f:
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
                    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Tasks WHERE project_id=?", (project_id,))
    for t in tasks:
        cursor.execute("INSERT INTO Tasks (id, project_id, title, description, priority, assignee, date, citation, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (t['id'], project_id, t['title'], t['description'], t['priority'], t['assignee'], t['date'], t['citation'], t['status']))
    conn.commit()
    conn.close()

def sync_db_to_tasks(project_id: str, task_id: str, new_status: str):
    spec = registry.get_project(project_id)
    filepath = spec.get_canonical_path("next-actions.md")

    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        if line.strip().startswith(f"### [{task_id}]"):
            if i + 1 < len(lines) and "**Status:**" in lines[i+1]:
                status_str = "Active" if new_status == "active" else "BLOCKED" if new_status == "blocked" else new_status.capitalize()
                lines[i+1] = f"**Status:** {status_str}\n"
            break
            
    with _file_lock:
        _atomic_write(filepath, lines)
        sync_tasks_to_db(project_id)

if __name__ == '__main__':
    sync_evidence_to_db("robert-boson-manuscript")
    sync_tasks_to_db("robert-boson-manuscript")
    print("Markdown synced to DB using AST parsing.")
