import sqlite3
import os
import hashlib
from project_registry import registry

def get_connection(project_id: str):
    spec = registry.get_project(project_id)
    runs_dir = spec.get_runs_dir()
    os.makedirs(runs_dir, exist_ok=True)
    db_path = os.path.join(runs_dir, ".aisci.db")

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    return conn

def init_db(project_id: str):
    conn = get_connection(project_id)
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
            category TEXT,
            provenance TEXT,
            source_hash TEXT
        )
    ''')
    try:
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_papers_source_hash ON Papers (project_id, source_hash)")
    except Exception:
        pass

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
            run_id TEXT REFERENCES JobExecutions(id),
            narrative TEXT,
            status_history TEXT NOT NULL DEFAULT '[]',
            canonical_hash TEXT UNIQUE
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
            updated_at TEXT,
            retry_of_job_id TEXT REFERENCES JobExecutions(id)
        )
    ''')

    # ReviewDecisions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ReviewDecisions (
            id TEXT PRIMARY KEY,
            project_id TEXT,
            target_id TEXT,
            target_kind TEXT DEFAULT 'unknown',
            expected_hash TEXT,
            requested_state TEXT,
            reviewer TEXT,
            rationale TEXT,
            status TEXT,
            created_at TEXT
        )
    ''')

    # SciteCache table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SciteCache (
            doi TEXT PRIMARY KEY,
            project_id TEXT,
            tallies_json TEXT,
            updated_at TEXT,
            status TEXT
        )
    ''')

    # SchemaVersion table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SchemaVersion (
            version INTEGER
        )
    ''')
    cursor.execute("SELECT version FROM SchemaVersion")
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO SchemaVersion (version) VALUES (0)")
        version = 0
    else:
        version = row['version']

    # Migration 1: Test isolation migration
    if version < 1:
        # We can add an isolation_test_column to prove it works
        try:
            cursor.execute("ALTER TABLE ActivityLogs ADD COLUMN isolation_test_column TEXT")
        except sqlite3.OperationalError:
            pass
        cursor.execute("UPDATE SchemaVersion SET version = 1")

    # Migration 2: Evidence audit history and run_id
    if version < 2:
        try:
            cursor.execute("ALTER TABLE Evidence ADD COLUMN run_id TEXT")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE Evidence ADD COLUMN status_history TEXT")
        except sqlite3.OperationalError:
            pass
        cursor.execute("UPDATE SchemaVersion SET version = 2")

    # Migration 3: Proper Evidence history, job retry fk, review targets, scite cache
    if version < 3:
        try:
            cursor.execute("ALTER TABLE JobExecutions ADD COLUMN retry_of_job_id TEXT REFERENCES JobExecutions(id)")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("ALTER TABLE ReviewDecisions ADD COLUMN target_kind TEXT DEFAULT 'unknown'")
            cursor.execute("UPDATE ReviewDecisions SET target_kind = 'evidence'")
        except sqlite3.OperationalError:
            pass

        # Migrate Evidence table for foreign keys and unique canonical_hash
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Evidence_old'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE Evidence RENAME TO Evidence_old")
            cursor.execute('''
                CREATE TABLE Evidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT,
                    claim TEXT,
                    status TEXT,
                    nextGate TEXT,
                    run TEXT,
                    run_id TEXT REFERENCES JobExecutions(id),
                    narrative TEXT,
                    status_history TEXT NOT NULL DEFAULT '[]',
                    canonical_hash TEXT UNIQUE
                )
            ''')
            cursor.execute("SELECT * FROM Evidence_old")
            old_rows = cursor.fetchall()
            for row in old_rows:
                row_dict = dict(row)
                chash = hashlib.md5((row_dict['project_id'] + ":" + row_dict['claim']).encode()).hexdigest()
                status_hist = row_dict.get('status_history')
                if not status_hist:
                    status_hist = '[]'
                r_id = row_dict.get('run_id')
                cursor.execute('''
                    INSERT INTO Evidence (id, project_id, claim, status, nextGate, run, run_id, narrative, status_history, canonical_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (row_dict['id'], row_dict['project_id'], row_dict['claim'], row_dict['status'], row_dict['nextGate'], row_dict['run'], r_id, row_dict['narrative'], status_hist, chash))
            cursor.execute("DROP TABLE Evidence_old")

        cursor.execute("UPDATE SchemaVersion SET version = 3")

    conn.commit()
    conn.close()

def insert_paper(paper_id, project_id, title, abstract, published_date, url, category, provenance=None, source_hash=None):
    conn = get_connection(project_id)
    cursor = conn.cursor()

    # Check if paper already exists by ID
    cursor.execute("SELECT 1 FROM Papers WHERE id = ?", (paper_id,))
    if cursor.fetchone():
        conn.close()
        return False

    # Check if paper already exists by project_id and source_hash
    if source_hash:
        cursor.execute("SELECT 1 FROM Papers WHERE project_id = ? AND source_hash = ?", (project_id, source_hash))
        if cursor.fetchone():
            conn.close()
            return False

    cursor.execute('''
        INSERT OR IGNORE INTO Papers (id, project_id, title, abstract, published_date, url, category, provenance, source_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (paper_id, project_id, title, abstract, published_date, url, category, provenance, source_hash))
    inserted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return inserted


def insert_claim(project_id, paper_id, claim_text, confidence, type):
    conn = get_connection(project_id)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Claims (paper_id, claim_text, confidence, type)
        VALUES (?, ?, ?, ?)
    ''', (paper_id, claim_text, confidence, type))
    conn.commit()
    conn.close()

def insert_dataset(project_id, paper_id, dataset_name):
    conn = get_connection(project_id)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Datasets (paper_id, dataset_name)
        VALUES (?, ?)
    ''', (paper_id, dataset_name))
    conn.commit()
    conn.close()

def get_stats(project_id):
    conn = get_connection(project_id)
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
    for p_id in registry.list_projects():
        init_db(p_id)
        print(f"Database initialized for {p_id}")
