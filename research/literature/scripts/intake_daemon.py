#!/usr/bin/env python3
import os
import sys
import time
import sqlite3
import requests
from datetime import datetime

# Local imports
from llm_extractor import extract_paper_claims
from ledger_updater import update_evidence_ledger

DB_PATH = "/home/ubuntu/aisci/research/literature/literature.db"
LOG_PATH = "/home/ubuntu/aisci/research/literature/ingestion_log.md"
KILL_SWITCH = "/home/ubuntu/aisci/research/literature/.kill_intake"
POLL_INTERVAL_SEC = 3600 * 6  # 6 hours

KEYWORDS = [
    "Tsallis distribution pp collisions",
    "Blast-Wave model 13 TeV",
    "high-multiplicity pp collisions"
]

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS papers 
                 (doi TEXT PRIMARY KEY, title TEXT, score TEXT, ingested_at TIMESTAMP)''')
    conn.commit()
    return conn

def log_action(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"- **[{timestamp}]** {message}\n"
    print(log_entry.strip())
    
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, 'w', encoding='utf-8') as f:
            f.write("# Literature Ingestion Log\n\n")
            
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def is_seen(conn, doi: str) -> bool:
    c = conn.cursor()
    c.execute("SELECT 1 FROM papers WHERE doi = ?", (doi,))
    return c.fetchone() is not None

def mark_seen(conn, doi: str, title: str, score: str):
    c = conn.cursor()
    c.execute("INSERT INTO papers (doi, title, score, ingested_at) VALUES (?, ?, ?, ?)",
              (doi, title, score, datetime.now()))
    conn.commit()

def fetch_recent_papers():
    papers = []
    for keyword in KEYWORDS:
        # We search OpenAlex by keyword, sorted by publication date descending
        url = f"https://api.openalex.org/works?search={keyword}&sort=publication_date:desc&per-page=5"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            for work in data.get("results", []):
                doi_raw = work.get("doi")
                doi = doi_raw.replace("https://doi.org/", "") if doi_raw else ""
                title = work.get("title") or ""
                abstract_inverted = work.get("abstract_inverted_index", {})
                
                # Reconstruct abstract from inverted index (crude but functional for LLM)
                abstract_words = {}
                for word, positions in abstract_inverted.items():
                    for pos in positions:
                        abstract_words[pos] = word
                abstract = " ".join([abstract_words[k] for k in sorted(abstract_words.keys())]) if abstract_words else ""
                
                if doi and title:
                    papers.append({
                        "doi": doi,
                        "title": title,
                        "abstract": abstract
                    })
        except Exception as e:
            log_action(f"Failed to fetch papers for keyword '{keyword}': {e}")
        time.sleep(1) # Rate limiting
    return papers

def run_intake_cycle():
    if os.path.exists(KILL_SWITCH):
        log_action("Kill switch detected. Aborting intake cycle.")
        return

    log_action("Starting literature intake cycle.")
    conn = init_db()
    papers = fetch_recent_papers()
    
    new_count = 0
    for p in papers:
        if os.path.exists(KILL_SWITCH):
            break
            
        if not is_seen(conn, p["doi"]):
            log_action(f"Processing new paper: {p['title']} (DOI: {p['doi']})")
            
            # Extract and score
            extraction = extract_paper_claims(p["title"], p["abstract"], p["doi"])
            
            score_category = extraction.get("score_category", "Unknown")
            log_action(f"Scored as: {score_category}. Reason: {extraction.get('score_reason', '')}")
            
            # Update Evidence Ledger
            update_evidence_ledger(p, extraction)
            
            # Mark as seen
            mark_seen(conn, p["doi"], p["title"], score_category)
            new_count += 1
            
            # Rate limiting for LLM extraction
            time.sleep(2)
            
    log_action(f"Cycle complete. Ingested {new_count} new papers.")
    conn.close()

def daemon_mode():
    log_action(f"Daemon started. Polling every {POLL_INTERVAL_SEC} seconds.")
    while True:
        if os.path.exists(KILL_SWITCH):
            log_action("Kill switch active. Exiting daemon.")
            sys.exit(0)
            
        run_intake_cycle()
        time.sleep(POLL_INTERVAL_SEC)

if __name__ == "__main__":
    if "--run-once" in sys.argv:
        run_intake_cycle()
    else:
        daemon_mode()
