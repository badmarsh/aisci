#!/usr/bin/env python3
"""
Literature Citation Fetcher

Recursively fetches papers citing the core Tsallis, Juttner, and Blast-Wave baseline papers
in high-multiplicity pp collisions using the OpenAlex API to build a 50+ source corpus.
"""

import json
import argparse
import requests
from pathlib import Path
from time import sleep

# Seed DOIs from the Robert ledger
SEED_DOIS = [
    "10.1088/1361-6471/ab783b", # Rath 2020 (BGBW)
    "10.1140/epja/i2019-12669-6", # Khuntia 2019 (BGBW)
    "10.3390/universe9020111", # Gupta 2023 (Boltzmann approximation)
    "10.48550/arxiv.2510.09692" # Biro/Paic/Serkin (Soft/Hard)
]

def fetch_openalex_work(doi: str) -> dict:
    url = f"https://api.openalex.org/works/https://doi.org/{doi}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Failed to fetch {doi}: {e}")
        return None

def fetch_citing_works(openalex_id: str, max_results: int = 50) -> list:
    # Get works that cite the given openalex_id
    url = f"https://api.openalex.org/works?filter=cites:{openalex_id}&per-page={max_results}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get("results", [])
    except Exception as e:
        print(f"Failed to fetch citations for {openalex_id}: {e}")
        return []

def format_bibtex(work: dict) -> str:
    """Very basic bibtex formatter for OpenAlex works."""
    doi = work.get("doi", "").replace("https://doi.org/", "")
    title = work.get("title", "Unknown Title")
    year = work.get("publication_year", "Unknown")
    authors = " and ".join([a.get("author", {}).get("display_name", "") for a in work.get("authorships", [])])
    
    bibtex_id = title.split()[0].lower() + str(year)
    if not doi:
        bibtex_id += "_nodoi"
        
    return f"""@article{{{bibtex_id},
  title={{{title}}},
  author={{{authors}}},
  year={{{year}}},
  doi={{{doi}}}
}}"""

def main(output_file: Path):
    corpus_works = []
    seen_ids = set()
    
    print("Fetching seed papers...")
    for doi in SEED_DOIS:
        work = fetch_openalex_work(doi)
        if work and work["id"] not in seen_ids:
            corpus_works.append(work)
            seen_ids.add(work["id"])
        sleep(1) # Be nice to the API
        
    print(f"Seed papers collected: {len(corpus_works)}. Fetching citations...")
    
    # Breadth-first citation fetching
    new_works = []
    for seed_work in corpus_works:
        print(f"Fetching citations for {seed_work.get('title')[:30]}...")
        citations = fetch_citing_works(seed_work["id"])
        for cit in citations:
            if cit["id"] not in seen_ids:
                new_works.append(cit)
                seen_ids.add(cit["id"])
                if len(seen_ids) >= 55: # Hard cap for 50+ target
                    break
        sleep(1)
        if len(seen_ids) >= 55:
            break
            
    corpus_works.extend(new_works)
    print(f"Total papers in corpus: {len(corpus_works)}")
    
    # Generate BibTeX
    print(f"Writing to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for work in corpus_works:
            f.write(format_bibtex(work) + "\n\n")
            
    print("Done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("literature/references.bib"))
    args = parser.parse_args()
    main(args.output)
