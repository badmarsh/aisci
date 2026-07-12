#!/usr/bin/env python3
"""
Bibliography Validator (bibliography-validator.py)

Cross-validates research/robert/bibliography.bib against the SQLite Papers table 
to find orphaned citations and uncited ingested papers.
"""

import os
import re
import sqlite3
from pathlib import Path

def parse_bib_ids(bib_path: Path):
    if not bib_path.exists():
        return set(), set()
    
    content = bib_path.read_text()
    
    # Simple regex to extract eprint (arxiv ID) and doi
    eprints = set(re.findall(r'eprint\s*=\s*"([^"]+)"', content))
    eprints.update(re.findall(r'eprint\s*=\s*\{([^}]+)\}', content))
    
    dois = set(re.findall(r'doi\s*=\s*"([^"]+)"', content))
    dois.update(re.findall(r'doi\s*=\s*\{([^}]+)\}', content))
    
    return eprints, dois

def validate_bibliography(project_id: str):
    db_path = Path(f"research/{project_id}/runs/.aisci.db")
    bib_path = Path(f"research/{project_id}/bibliography.bib")
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return
        
    eprints, dois = parse_bib_ids(bib_path)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, url FROM Papers WHERE project_id = ?", (project_id,))
    rows = cursor.fetchall()
    conn.close()
    
    db_arxiv_ids = set()
    db_dois = set()
    
    for row in rows:
        pid = row['id']
        url = row['url'] or ""
        
        if "arxiv" in pid.lower():
            db_arxiv_ids.add(pid.replace("arXiv:", "").replace("arxiv:", ""))
        elif "arxiv" in url.lower():
            match = re.search(r'arxiv\.org/abs/(.*)', url)
            if match:
                db_arxiv_ids.add(match.group(1))
                
        if "doi.org" in url:
            match = re.search(r'doi\.org/(.*)', url)
            if match:
                db_dois.add(match.group(1))
                
    # Find orphans in bib (not in db)
    orphaned_eprints = eprints - db_arxiv_ids
    orphaned_dois = dois - db_dois
    
    # Find uncited in db (not in bib)
    uncited_arxiv = db_arxiv_ids - eprints
    uncited_dois = db_dois - dois
    
    print(f"--- Bibliography Validation for {project_id} ---")
    print(f"Total Papers in BibTeX: {len(eprints) + len(dois)}")
    print(f"Total Papers in DB: {len(rows)}")
    print("\nORPHANED IN BIBTEX (Not in DB):")
    for ep in orphaned_eprints:
        print(f"  - arXiv:{ep}")
    for doi in orphaned_dois:
        print(f"  - DOI:{doi}")
    if not orphaned_eprints and not orphaned_dois:
        print("  None.")
        
    print("\nUNCITED IN DB (Not in BibTeX):")
    for ep in uncited_arxiv:
        print(f"  - arXiv:{ep}")
    for doi in uncited_dois:
        print(f"  - DOI:{doi}")
    if not uncited_arxiv and not uncited_dois:
        print("  None.")

if __name__ == "__main__":
    validate_bibliography("robert")
