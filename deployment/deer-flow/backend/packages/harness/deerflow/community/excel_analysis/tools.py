"""Excel/CSV Analysis Tool — read and analyze CSV/Excel files using pandas."""

import json
import logging
import os

from langchain.tools import tool

logger = logging.getLogger(__name__)


def _read_file(file_path: str) -> "pd.DataFrame":
    """Read a CSV or Excel file into a pandas DataFrame."""
    import pandas as pd

    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(file_path)
    elif ext in (".xlsx", ".xls"):
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Use .csv, .xlsx, or .xls")


@tool("analyze_file", parse_docstring=True)
def excel_analyze_tool(
    file_path: str,
    analysis: str = "summary",
    column: str | None = None,
    query: str | None = None,
) -> str:
    """Analyze a CSV or Excel file.

    Args:
        file_path: Path to the CSV or Excel file.
        analysis: Type of analysis. Options: summary, head, column_stats, filter, value_counts.
        column: Column name for column-specific analyses.
        query: Pandas query expression for filtering.
    """
    try:
        import pandas as pd
    except ImportError:
        return json.dumps({"error": "pandas not installed. Run: pip install pandas openpyxl"}, ensure_ascii=False)

    if not os.path.exists(file_path):
        return json.dumps({"error": f"File not found: {file_path}", "file_path": file_path}, ensure_ascii=False)

    try:
        df = _read_file(file_path)
        output = {"file_path": file_path, "shape": list(df.shape), "columns": list(df.columns)}

        if analysis == "summary":
            output["dtypes"] = {k: str(v) for k, v in df.dtypes.items()}
            output["describe"] = json.loads(df.describe(include="all").to_json(orient="columns", default_handler=str))
            output["null_counts"] = df.isnull().sum().to_dict()
        elif analysis == "head":
            output["head"] = json.loads(df.head(10).to_json(orient="records", default_handler=str))
        elif analysis == "column_stats":
            if not column or column not in df.columns:
                return json.dumps({"error": f"Column '{column}' not found. Available: {list(df.columns)}"}, ensure_ascii=False)
            output["column"] = column
            output["dtype"] = str(df[column].dtype)
            output["describe"] = json.loads(df[column].describe().to_json(default_handler=str))
            output["null_count"] = int(df[column].isnull().sum())
            output["unique_count"] = int(df[column].nunique())
        elif analysis == "filter":
            if not query:
                return json.dumps({"error": "query parameter required for filter analysis"}, ensure_ascii=False)
            filtered = df.query(query)
            output["query"] = query
            output["matched_rows"] = len(filtered)
            output["head"] = json.loads(filtered.head(10).to_json(orient="records", default_handler=str))
        elif analysis == "value_counts":
            if not column or column not in df.columns:
                return json.dumps({"error": f"Column '{column}' not found. Available: {list(df.columns)}"}, ensure_ascii=False)
            vc = df[column].value_counts().head(20)
            output["column"] = column
            output["value_counts"] = {str(k): int(v) for k, v in vc.items()}
        else:
            return json.dumps({"error": f"Unknown analysis type: {analysis}. Options: summary, head, column_stats, filter, value_counts"}, ensure_ascii=False)

        return json.dumps(output, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Excel/CSV analysis failed: {e}")
        return json.dumps({"error": str(e), "file_path": file_path}, ensure_ascii=False)
