import os
import sys
import hashlib
from database import insert_paper, insert_claim

papers = [
    {
        "id": "1905.07208",
        "title": "Charged-particle production as a function of multiplicity and transverse spherocity in pp collisions at √s = 5.02 and 13 TeV",
        "abstract": "ALICE HEPData ins1735345 source",
        "published_date": "2019",
        "url": "https://arxiv.org/abs/1905.07208",
        "category": "hep-ex",
        "claims": [{"text": "Measures d²N_ch/(dpT dη)", "confidence": "HIGH"}]
    },
    {
        "id": "nucl-th/9307020",
        "title": "Thermalized cylinder: an exploding quark-gluon plasma",
        "abstract": "Schnedermann, Sollfrank, Heinz (SSH) — BGBW original",
        "published_date": "1993",
        "url": "https://arxiv.org/abs/nucl-th/9307020",
        "category": "nucl-th",
        "claims": [{"text": "Canonical BGBW model used in all blast-wave baselines", "confidence": "HIGH"}]
    },
    {
        "id": "1110.5526",
        "title": "Thermodynamic consistency of the Tsallis distribution in relativistic high energy quantum distributions",
        "abstract": "Cleymans, Worku — Tsallis in pp at LHC",
        "published_date": "2012",
        "url": "https://arxiv.org/abs/1110.5526",
        "category": "hep-ph",
        "claims": [{"text": "Thermodynamic consistency of the Tsallis distribution", "confidence": "HIGH"}]
    },
    {
        "id": "1808.02383",
        "title": "Radial flow and freeze-out in pp collisions",
        "abstract": "Khuntia, Sharma, Tiwari, Sahoo — Radial flow pp",
        "published_date": "2019",
        "url": "https://arxiv.org/abs/1808.02383",
        "category": "hep-ph",
        "claims": [{"text": "BGBW vs multiplicity, pp √s=7 TeV, pions/kaons/protons", "confidence": "HIGH"}]
    },
    {
        "id": "1908.04208",
        "title": "Freeze-out parameters as a function of multiplicity in pp, p-Pb and Pb-Pb collisions",
        "abstract": "Rath, Sahoo",
        "published_date": "2020",
        "url": "https://arxiv.org/abs/1908.04208",
        "category": "hep-ph",
        "claims": [{"text": "T_kin, β vs multiplicity pp/pA/AA", "confidence": "HIGH"}]
    },
    {
        "id": "1407.4087",
        "title": "Two-component spectra",
        "abstract": "Bylinkin, Rostovtsev",
        "published_date": "2014",
        "url": "https://arxiv.org/abs/1407.4087",
        "category": "hep-ph",
        "claims": [{"text": "Thermal + power law decomposition", "confidence": "HIGH"}]
    },
    {
        "id": "2406.12029",
        "title": "Relativistic Tsallis transformations",
        "abstract": "Parvan",
        "published_date": "2025",
        "url": "https://arxiv.org/abs/2406.12029",
        "category": "hep-ph",
        "claims": [{"text": "Boltzmann-Gibbs vs Tsallis Lorentz transform properties", "confidence": "HIGH"}]
    },
    {
        "id": "1611.08391v4",
        "title": "Improved Tsallis distribution",
        "abstract": "Lao, Liu, Lacey",
        "published_date": "2016",
        "url": "https://arxiv.org/abs/1611.08391v4",
        "category": "hep-ph",
        "claims": [{"text": "Uses a Taylor expansion up to first order in (q-1) to approximate Tsallis distribution with radial flow", "confidence": "HIGH"}]
    },
    {
        "id": "2407.09207v3",
        "title": "Quantification of pion excess",
        "abstract": "Lu et al.",
        "published_date": "2024",
        "url": "https://arxiv.org/abs/2407.09207v3",
        "category": "nucl-th",
        "claims": [{"text": "Uses Bayesian inference to quantify model-to-data differences in heavy-ion collisions", "confidence": "HIGH"}]
    },
    {
        "id": "2508.00989v3",
        "title": "Angular Coefficients",
        "abstract": "Bendavid et al.",
        "published_date": "2025",
        "url": "https://arxiv.org/abs/2508.00989v3",
        "category": "hep-ex",
        "claims": [{"text": "Uses Symbolic Regression to derive analytical expressions for kinematic observables", "confidence": "HIGH"}]
    }
]

def load_legacy():
    project_id = "robert-boson-manuscript"
    for p in papers:
        content = p["id"] + p["title"] + p["abstract"]
        source_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        provenance = "Legacy manual ingest (load_legacy_papers.py)"
        
        insert_paper(
            paper_id=p["id"],
            project_id=project_id,
            title=p["title"],
            abstract=p["abstract"],
            published_date=p["published_date"],
            url=p["url"],
            category=p["category"],
            provenance=provenance,
            source_hash=source_hash
        )
        for c in p.get("claims", []):
            insert_claim(
                project_id=project_id,
                paper_id=p["id"],
                claim_text=c["text"],
                confidence=c["confidence"],
                type="Supporting"
            )
            
    # Also look for any literature_*.md files in research/robert/
    robert_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../research/robert"))
    if os.path.exists(robert_dir):
        for f in os.listdir(robert_dir):
            if f.startswith("literature_") and f.endswith(".md"):
                path = os.path.join(robert_dir, f)
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read()
                    doc_id = f.replace("literature_", "").replace(".md", "")
                    title = f"Local Literature: {doc_id}"
                    source_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
                    provenance = f"Legacy local file: {f}"
                    insert_paper(
                        paper_id=doc_id,
                        project_id=project_id,
                        title=title,
                        abstract=content[:200] + "...",
                        published_date="Unknown",
                        url=f"file://{path}",
                        category="local-notes",
                        provenance=provenance,
                        source_hash=source_hash
                    )
                    
    print("Legacy papers loaded successfully.")

if __name__ == "__main__":
    load_legacy()
