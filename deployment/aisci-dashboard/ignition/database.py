import sqlite3
import os
from config import DB_PATH

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Papers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Papers (
            id TEXT PRIMARY KEY,
            project_id TEXT,
            title TEXT,
            abstract TEXT,
            published_date TEXT,
            url TEXT,
            category TEXT
        )
    ''')
    
    # Claims Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_id TEXT,
            claim_text TEXT,
            confidence TEXT,
            type TEXT,
            FOREIGN KEY (paper_id) REFERENCES Papers (id)
        )
    ''')
    
    # Datasets Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_id TEXT,
            dataset_name TEXT,
            FOREIGN KEY (paper_id) REFERENCES Papers (id)
        )
    ''')
    
    # Contradictions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Contradictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id INTEGER,
            counter_claim_id INTEGER,
            rationale TEXT,
            FOREIGN KEY (claim_id) REFERENCES Claims (id),
            FOREIGN KEY (counter_claim_id) REFERENCES Claims (id)
        )
    ''')
    
    # Evidence table (canonical status from evidence-ledger.md)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT,
            claim TEXT,
            status TEXT,
            nextGate TEXT,
            run TEXT,
            narrative TEXT
        )
    ''')

    # Tasks table (canonical queue from next-actions.md)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tasks (
            id TEXT PRIMARY KEY,
            project_id TEXT,
            title TEXT,
            description TEXT,
            priority TEXT,
            assignee TEXT,
            date TEXT,
            citation TEXT,
            status TEXT
        )
    ''')

    # ActivityLogs table (UI event audit trail)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ActivityLogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT,
            timestamp TEXT,
            action TEXT,
            user TEXT,
            details TEXT
        )
    ''')
    
    # JobExecutions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS JobExecutions (
            id TEXT PRIMARY KEY,
            project_id TEXT,
            pipeline_id TEXT,
            name TEXT,
            requester TEXT,
            status TEXT,
            error TEXT,
            exit_code INTEGER,
            log_path TEXT,
            artifact_manifest TEXT,
            git_commit TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')

    # ReviewDecisions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ReviewDecisions (
            id TEXT PRIMARY KEY,
            project_id TEXT,
            target_id TEXT,
            expected_hash TEXT,
            requested_state TEXT,
            reviewer TEXT,
            rationale TEXT,
            status TEXT,
            created_at TEXT
        )
    ''')
    
    # Schema Migrations
    try:
        cursor.execute("ALTER TABLE Papers ADD COLUMN project_id TEXT DEFAULT 'robert-boson-manuscript'")
    except sqlite3.OperationalError:
        pass # Column exists

    try:
        cursor.execute("ALTER TABLE Evidence ADD COLUMN project_id TEXT DEFAULT 'robert-boson-manuscript'")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE Tasks ADD COLUMN project_id TEXT DEFAULT 'robert-boson-manuscript'")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE JobExecutions ADD COLUMN project_id TEXT")
        cursor.execute("ALTER TABLE JobExecutions ADD COLUMN pipeline_id TEXT")
        cursor.execute("ALTER TABLE JobExecutions ADD COLUMN requester TEXT")
        cursor.execute("ALTER TABLE JobExecutions ADD COLUMN exit_code INTEGER")
        cursor.execute("ALTER TABLE JobExecutions ADD COLUMN git_commit TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE ReviewDecisions ADD COLUMN project_id TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE ActivityLogs ADD COLUMN project_id TEXT")
    except sqlite3.OperationalError:
        pass
        
    # Update default project_id for old records
    cursor.execute("UPDATE Papers SET project_id = 'robert-boson-manuscript' WHERE project_id IS NULL")
    cursor.execute("UPDATE Evidence SET project_id = 'robert-boson-manuscript' WHERE project_id IS NULL")
    cursor.execute("UPDATE Tasks SET project_id = 'robert-boson-manuscript' WHERE project_id IS NULL")
    
    conn.commit()
    conn.close()

def insert_paper(paper_id, project_id, title, abstract, published_date, url, category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO Papers (id, project_id, title, abstract, published_date, url, category)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (paper_id, project_id, title, abstract, published_date, url, category))
    conn.commit()
    conn.close()

def insert_claim(paper_id, claim_text, confidence, type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Claims (paper_id, claim_text, confidence, type)
        VALUES (?, ?, ?, ?)
    ''', (paper_id, claim_text, confidence, type))
    conn.commit()
    conn.close()

def insert_dataset(paper_id, dataset_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Datasets (paper_id, dataset_name)
        VALUES (?, ?)
    ''', (paper_id, dataset_name))
    conn.commit()
    conn.close()

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM Papers')
    papers_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM Claims')
    claims_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM Contradictions')
    contradictions_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'papers': papers_count,
        'claims': claims_count,
        'contradictions': contradictions_count
    }

if __name__ == '__main__':
    init_db()
    print(f"Database initialized at {DB_PATH}")
