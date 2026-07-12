import sys
from pathlib import Path

# Add the src directory to sys.path so tests can import from src
sys.path.insert(0, str(Path(__file__).parent / "src"))
