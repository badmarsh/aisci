import os

# Derive repository root
default_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
REPO_ROOT = os.environ.get("AISCI_REPO_ROOT", default_repo_root)

# Base Paths
DASHBOARD_ROOT = os.path.join(REPO_ROOT, 'deployment', 'aisci-dashboard')
DATA_DIR = os.path.join(DASHBOARD_ROOT, 'data')
DB_PATH = os.path.join(DATA_DIR, 'evidence_graph.db')

# Other Config
AUTH_TOKEN = os.environ.get("AISCI_DASHBOARD_TOKEN", "")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

