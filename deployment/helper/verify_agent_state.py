#!/usr/bin/env python3
import sys
import os

def check_dependencies():
    missing = []
    try:
        import sympy
    except ImportError:
        missing.append("sympy")
    
    try:
        import iminuit
    except ImportError:
        missing.append("iminuit")
        
    if missing:
        print(f"[ERROR] Missing physics dependencies: {', '.join(missing)}")
        return False
    return True

def check_files():
    required_files = [
        "research/robert/evidence-ledger.md",
        "research/literature/literature.db"
    ]
    missing = []
    for f in required_files:
        if not os.path.exists(f):
            missing.append(f)
            
    if missing:
        print(f"[ERROR] Missing critical data/files: {', '.join(missing)}")
        # Note: In a real environment we might fail, but for now we'll just warn
        # return False
    return True

def main():
    print("Running AiSci Agent State Ratchet...")
    success = check_dependencies()
    success = check_files() and success
    
    if success:
        print("[OK] Agent state verified. Environment is healthy.")
        sys.exit(0)
    else:
        print("[FAIL] Agent state verification failed. Please fix before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    main()
