"""
DeerFlow community tool: data_preprocessing

Provides tools for the `data-cleaner` agent to sanitize and profile datasets.
"""
import json
import os
import subprocess
from pathlib import Path
from langchain_core.tools import tool

# ─── constants ────────────────────────────────────────────────────────────────

HOST_AISCI = "/home/ubuntu/aisci"
CONTAINER_AISCI = "/mnt/host/aisci"

def _to_host_path(container_path: str) -> str:
    """Convert a container path back to a user-visible host path."""
    return container_path.replace(CONTAINER_AISCI, HOST_AISCI)

# ─── tools ────────────────────────────────────────────────────────────────────

@tool
def data_profile(csv_path_container: str) -> str:
    """
    Runs a statistical profile on a CSV (missing values, types, basic stats).
    
    Args:
        csv_path_container: Absolute container path to the CSV file.
    
    Returns:
        JSON string containing basic profile statistics or error.
    """
    path = Path(csv_path_container)
    if not path.exists():
        return json.dumps({"success": False, "error": f"File not found: {csv_path_container}"})
        
    try:
        import pandas as pd
        df = pd.read_csv(path)
        profile = {
            "rows": len(df),
            "columns": len(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "dtypes": {k: str(v) for k, v in df.dtypes.items()},
        }
        return json.dumps({"success": True, "profile": profile})
    except ImportError:
        return json.dumps({"success": False, "error": "pandas is not installed in this environment."})
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})

@tool
def data_sanitize(csv_path_container: str, output_path_container: str, drop_na: bool = True) -> str:
    """
    Sanitizes the data by removing NaNs and saving to a new file.
    
    Args:
        csv_path_container: Absolute container path to the input CSV.
        output_path_container: Absolute container path for the sanitized CSV.
        drop_na: Whether to drop rows with NaN values.
        
    Returns:
        JSON string indicating success and output path.
    """
    path = Path(csv_path_container)
    out_path = Path(output_path_container)
    
    if not path.exists():
        return json.dumps({"success": False, "error": f"File not found: {csv_path_container}"})
        
    try:
        import pandas as pd
        df = pd.read_csv(path)
        if drop_na:
            df = df.dropna()
        
        out_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_path, index=False)
        
        return json.dumps({
            "success": True, 
            "original_rows": len(pd.read_csv(path)), 
            "final_rows": len(df),
            "output_path": _to_host_path(str(out_path))
        })
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})
