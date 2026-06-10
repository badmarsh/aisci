"""PDF Reader Tool — extract text and tables from PDF files using PyMuPDF (fitz).

Execution model
---------------
This tool runs its PyMuPDF extraction **inside the active sandbox** (via
``sandbox.execute_command``), exactly like ``bash``/``read_file``/``grep``.

This matters: the gateway process that hosts community tools does **not** have
PyMuPDF installed and cannot see the sandbox upload mount (``/mnt/user-data``).
The sandbox image, on the other hand, ships PyMuPDF and is where uploaded files
actually live. Running the extraction in-process therefore failed twice over —
a spurious "PyMuPDF not installed" ImportError *and* a "File not found" for any
``/mnt/user-data/...`` path. Delegating to the sandbox fixes both and keeps the
path semantics consistent with every other file tool the agent uses.
"""

import base64
import json
import logging

from langchain.tools import tool

from deerflow.tools.types import Runtime

logger = logging.getLogger(__name__)

# Cap the extracted text so a large document (e.g. a full thesis) cannot blow
# up the model context. The agent can request specific ``pages`` for more.
_MAX_TEXT_CHARS = 120_000

# Runs inside the sandbox. Reads its arguments from the base64-encoded PDF_ARGS
# env var (avoids all shell-quoting issues) and prints a single JSON object to
# stdout. It always prints JSON — every failure path is caught and reported with
# a precise message instead of a misleading "not installed".
_SANDBOX_SCRIPT = r'''
import os, sys, json, base64

def emit(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False))
    sys.stdout.flush()

try:
    args = json.loads(base64.b64decode(os.environ["PDF_ARGS"]).decode("utf-8"))
except Exception as exc:  # pragma: no cover - defensive
    emit({"error": "Failed to decode PDF_ARGS: %s" % exc})
    sys.exit(0)

file_path = args["file_path"]
pages = args.get("pages")
extract_tables = bool(args.get("extract_tables", False))
max_chars = int(args.get("max_chars", 120000))

try:
    import fitz  # PyMuPDF
except Exception:
    try:
        import pymupdf as fitz  # newer PyMuPDF exposes the `pymupdf` name
    except Exception as exc:
        emit({
            "error": (
                "PyMuPDF could not be imported in the sandbox (%r). "
                "Install it in the sandbox with `pip install pymupdf`." % (exc,)
            ),
            "file_path": file_path,
        })
        sys.exit(0)

if not os.path.exists(file_path):
    emit({"error": "File not found: %s" % file_path, "file_path": file_path})
    sys.exit(0)

try:
    doc = fitz.open(file_path)
    total_pages = len(doc)

    if pages is not None:
        page_range = [p for p in pages if 0 <= p < total_pages]
    else:
        page_range = list(range(total_pages))

    text_parts = []
    tables = []
    used = 0
    truncated = False
    for page_num in page_range:
        page = doc[page_num]
        chunk = "--- Page %d ---\n%s" % (page_num + 1, page.get_text("text"))
        if used + len(chunk) > max_chars:
            text_parts.append(chunk[: max(0, max_chars - used)])
            truncated = True
            break
        text_parts.append(chunk)
        used += len(chunk)

        if extract_tables:
            try:
                for i, tab in enumerate(page.find_tables()):
                    tables.append({
                        "page": page_num + 1,
                        "table_index": i,
                        "headers": tab.header.names if tab.header else [],
                        "rows": tab.extract(),
                    })
            except Exception:
                pass

    output = {
        "file_path": file_path,
        "total_pages": total_pages,
        "extracted_pages": len(text_parts),
        "text": "\n\n".join(text_parts),
    }
    if truncated:
        output["truncated"] = True
        output["note"] = (
            "Output truncated at %d chars. Request specific `pages` for more." % max_chars
        )
    if tables:
        output["tables"] = tables
    doc.close()
    emit(output)
except Exception as exc:
    emit({"error": str(exc), "file_path": file_path})
'''


@tool("read_pdf", parse_docstring=True)
def pdf_reader_tool(
    runtime: Runtime,
    file_path: str,
    pages: list[int] | None = None,
    extract_tables: bool = False,
) -> str:
    """Extract text content from a PDF file. Use this to read research papers, reports, and documents.

    Args:
        file_path: Path to the PDF file (absolute path, e.g. under /mnt/user-data/uploads).
        pages: Optional list of page numbers (0-indexed) to extract. If None, extracts all pages.
        extract_tables: If True, also attempt to extract tables from the PDF.
    """
    # Import lazily to avoid any import-time coupling with the sandbox package.
    from deerflow.sandbox.exceptions import SandboxError
    from deerflow.sandbox.tools import ensure_sandbox_initialized

    try:
        sandbox = ensure_sandbox_initialized(runtime)
    except SandboxError as e:
        return json.dumps({"error": f"Sandbox unavailable: {e}", "file_path": file_path}, ensure_ascii=False)
    except Exception as e:  # pragma: no cover - defensive
        return json.dumps({"error": f"Sandbox initialization failed: {e}", "file_path": file_path}, ensure_ascii=False)

    payload = {
        "file_path": file_path,
        "pages": pages,
        "extract_tables": extract_tables,
        "max_chars": _MAX_TEXT_CHARS,
    }
    b64_args = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")
    b64_script = base64.b64encode(_SANDBOX_SCRIPT.encode("utf-8")).decode("ascii")

    # base64 only contains [A-Za-z0-9+/=] — safe to embed unquoted/in single
    # quotes, so the command needs no further shell escaping. stderr is dropped
    # because the script reports every failure as JSON on stdout itself.
    command = (
        f"PDF_ARGS={b64_args} python3 -c "
        f"\"import base64; exec(base64.b64decode('{b64_script}'))\" 2>/dev/null"
    )

    try:
        output = sandbox.execute_command(command)
    except SandboxError as e:
        return json.dumps({"error": f"Sandbox execution failed: {e}", "file_path": file_path}, ensure_ascii=False)
    except Exception as e:  # pragma: no cover - defensive
        logger.error(f"PDF reading failed: {e}")
        return json.dumps({"error": str(e), "file_path": file_path}, ensure_ascii=False)

    output = (output or "").strip()
    if not output:
        return json.dumps(
            {
                "error": "Sandbox produced no output while reading the PDF (python3 or PyMuPDF may be missing in the sandbox image).",
                "file_path": file_path,
            },
            ensure_ascii=False,
        )

    # The sandbox script returns a JSON object. Pretty-print it when it parses;
    # otherwise pass the raw output through so nothing is silently swallowed.
    try:
        return json.dumps(json.loads(output), indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        return output
