#!/usr/bin/env python3
from __future__ import annotations
import subprocess
from pathlib import Path

PDF_PATH = Path("/home/ubuntu/aisci/research/robert/manuscript/boson-probability-function-moving-system.pdf")
OUT_TXT = Path("/home/ubuntu/aisci/research/robert/scratch/manuscript_text.txt")

def main():
    OUT_TXT.parent.mkdir(parents=True, exist_ok=True)
    print(f"Extracting text from {PDF_PATH} using pdftotext...")
    cmd = ["pdftotext", str(PDF_PATH), str(OUT_TXT)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and OUT_TXT.exists():
        print(f"Successfully extracted text to {OUT_TXT}")
        text = OUT_TXT.read_text()
        lines = text.splitlines()
        print(f"Total lines extracted: {len(lines)}")
        
        # Search for formulas or references to boson probability or Juttner
        print("\n=== Searching for formula-related keywords ===")
        keywords = ["exp(", "distribution", "boson", "Juttner", "Boltzmann", "formula", "equation", "Table 1"]
        for idx, line in enumerate(lines):
            for kw in keywords:
                if kw.lower() in line.lower():
                    # Print line with context (line number)
                    print(f"Line {idx+1}: {line.strip()}")
                    break
    else:
        print(f"Failed to extract text. Return code: {res.returncode}")
        print(f"Stderr: {res.stderr}")

if __name__ == "__main__":
    main()
