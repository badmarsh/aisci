import sys
try:
    import importlib
    m = importlib.import_module("deerflow.models.gemini_cli_provider")
    print("SUCCESS", m)
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    if hasattr(e, "name"):
        print(f"Error name: {e.name}")
