import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'evidence_graph.db')

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Papers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Papers (
            id TEXT PRIMARY KEY,
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
            timestamp TEXT,
            action TEXT,
            user TEXT,
            details TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def insert_paper(paper_id, title, abstract, published_date, url, category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO Papers (id, title, abstract, published_date, url, category)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (paper_id, title, abstract, published_date, url, category))
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
