import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)) + '/aisci-dashboard')
from ignition.database import insert_paper, insert_claim, get_connection

STALE_DB = os.path.join(os.path.dirname(__file__), '../aisci-dashboard/ignition/evidence_graph.db')

def migrate_stale_db():
    if not os.path.exists(STALE_DB):
        print(f"Stale DB {STALE_DB} not found. Nothing to do.")
        return

    stale_conn = sqlite3.connect(STALE_DB)
    stale_conn.row_factory = sqlite3.Row
    cursor = stale_conn.cursor()

    print("Migrating Papers...")
    try:
        cursor.execute("SELECT * FROM Papers")
        papers = cursor.fetchall()
        for p in papers:
            insert_paper(p['id'], p['title'], p['abstract'], p['published_date'], p['url'], p['category'])
            print(f"Inserted paper {p['id']}")
    except sqlite3.OperationalError:
        pass

    print("Migrating Claims...")
    try:
        cursor.execute("SELECT * FROM Claims")
        claims = cursor.fetchall()
        
        active_conn = get_connection()
        active_cursor = active_conn.cursor()
        
        for c in claims:
            active_cursor.execute("SELECT id FROM Claims WHERE paper_id=? AND claim_text=?", (c['paper_id'], c['claim_text']))
            if not active_cursor.fetchone():
                insert_claim(c['paper_id'], c['claim_text'], c['confidence'], c['type'])
                print(f"Inserted claim for {c['paper_id']}")
        active_conn.close()
    except sqlite3.OperationalError:
        pass

    stale_conn.close()

    archive_path = STALE_DB + ".archive"
    os.rename(STALE_DB, archive_path)
    print(f"Migrated stale data and archived to {archive_path}")

if __name__ == '__main__':
    migrate_stale_db()
