import os

# Derive repository root
default_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
REPO_ROOT = os.environ.get("AISCI_REPO_ROOT", default_repo_root)

# Base Paths
DASHBOARD_ROOT = os.path.join(REPO_ROOT, 'deployment', 'aisci-dashboard')
DATA_DIR = os.path.join(DASHBOARD_ROOT, 'data')
DB_PATH = os.path.join(DATA_DIR, 'evidence_graph.db')

# Canonical Research Paths
RESEARCH_ROOT = os.path.join(REPO_ROOT, 'research', 'robert')
EVIDENCE_FILE = os.path.join(RESEARCH_ROOT, 'evidence-ledger.md')
TASKS_FILE = os.path.join(RESEARCH_ROOT, 'next-actions.md')
RUNS_BASE = os.path.join(RESEARCH_ROOT, 'runs')

# Other Config
AUTH_TOKEN = os.environ.get("AISCI_DASHBOARD_TOKEN", "")

def validate_paths():
    """Validates that the required canonical paths exist."""
    required = [RESEARCH_ROOT, EVIDENCE_FILE, TASKS_FILE, RUNS_BASE]
    missing = [p for p in required if not os.path.exists(p)]
    if missing:
        raise RuntimeError(f"Missing required canonical paths: {missing}")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)
