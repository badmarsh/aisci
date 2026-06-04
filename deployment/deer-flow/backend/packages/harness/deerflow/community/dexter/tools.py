"""Dexter - AI financial research agent as DeerFlow tools.

Wraps the Dexter TypeScript agent (https://github.com/virattt/dexter) as
callable tools for DeerFlow agents.

Prerequisites:
  - Dexter cloned into <deerflow-root>/dexter/
  - bun runtime installed
  - Required API keys set (OPENAI_API_KEY via Onyx LiteLLM)
"""

import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path

from langchain.tools import tool

logger = logging.getLogger(__name__)

# Resolve Dexter root: <deerflow-backend-root>/dexter/
DEXTER_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent / "dexter"
DEXTER_ENTRY = DEXTER_ROOT / "src" / "index.tsx"


def _ensure_dexter_setup() -> bool:
    """Verify Dexter is cloned and bun is available."""
    if not DEXTER_ROOT.exists():
        logger.warning("Dexter not found at %s — skip tool registration", DEXTER_ROOT)
        return False
    if not DEXTER_ENTRY.exists():
        logger.warning("Dexter entry point not found at %s", DEXTER_ENTRY)
        return False
    return True


def _build_env() -> dict[str, str]:
    """Build environment for Dexter with DeerFlow's API keys."""
    env = os.environ.copy()

    # Dexter uses OpenRouter directly (Onyx LiteLLM not reachable from gateway container)
    openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")
    openrouter_base = os.environ.get("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
    if openrouter_key:
        env["OPENAI_API_KEY"] = openrouter_key
        env["OPENAI_API_BASE"] = openrouter_base

    # Fallback: try Onyx if available
    if not env.get("OPENAI_API_KEY"):
        onyx_api_key = os.environ.get("ONYX_API_KEY", "")
        onyx_litellm = os.environ.get("ONYX_LITELLM_API_BASE", "")
        if onyx_api_key:
            env["OPENAI_API_KEY"] = onyx_api_key
        if onyx_litellm:
            env["OPENAI_API_BASE"] = onyx_litellm

    return env


def _run_dexter_query(query: str, timeout: int = 300) -> str:
    """Run a Dexter research query via bun subprocess.

    Creates a temp script that imports Dexter's Agent and runs a single query.
    Uses reduced iterations (8) and a fast model for tool-use context.
    """
    if not _ensure_dexter_setup():
        return "Dexter is not installed. Financial research tool unavailable."

    env = _build_env()

    # Disable web search tools in Dexter (no API keys configured)
    # to prevent retries and timeouts. Dexter will use reasoning only.
    env["EXASEARCH_API_KEY"] = ""
    env["TAVILY_API_KEY"] = ""
    env["PERPLEXITY_API_KEY"] = ""
    env["FINANCIAL_DATASETS_API_KEY"] = ""

    # Use absolute path for imports since script runs from /tmp
    dexter_src = str(DEXTER_ROOT / "src")
    script = f"""
import {{ Agent }} from '{dexter_src}/agent/index.js';
import {{ config }} from 'dotenv';
config({{ quiet: true }});

async function main() {{
    // Use a lightweight model and limit iterations for tool-use context
    const agent = await Agent.create({{
        maxIterations: 8,
        model: 'anthropic/claude-sonnet-4-20250514',
    }});

    let answer = '';
    for await (const event of agent.run({json.dumps(query)})) {{
        if (event.type === 'done') {{
            answer = event.answer;
        }}
    }}
    console.log(JSON.stringify({{ answer, success: !!answer }}));
}}

main().catch(err => {{
    console.error(JSON.stringify({{ answer: `Error: ${{err.message}}`, success: false }}));
    process.exit(1);
}});
"""

    tmp_dir = Path(tempfile.gettempdir()) / "dexter-deerflow"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_script = tmp_dir / "deerflow_query.ts"
    tmp_script.write_text(script)

    try:
        result = subprocess.run(
            ["bun", "run", str(tmp_script)],
            cwd=str(DEXTER_ROOT),
            env={**env, "BUN_IMPORT_MAP_PATH": str(DEXTER_ROOT / "bun.lock"),
                 "NODE_PATH": str(DEXTER_ROOT / "node_modules")},
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        output = result.stdout.strip().split("\n")[-1]  # last line is JSON
        try:
            data = json.loads(output)
            return data.get("answer", "No answer returned by Dexter.")
        except json.JSONDecodeError:
            if result.stderr:
                return f"Dexter error: {result.stderr[-2000:]}"
            return f"Dexter output: {result.stdout[-2000:]}"

    except subprocess.TimeoutExpired:
        return f"Dexter timed out after {timeout}s. The research query is still running or stalled."
    except Exception as e:
        return f"Dexter failed: {e}"


# ── LangChain Tools ─────────────────────────────────────────────────────────


@tool("dexter_financial_research", parse_docstring=True)
def dexter_financial_research_tool(query: str) -> str:
    """Deep financial research via Dexter AI agent.

    Use this tool for complex financial questions that require multi-step
    research planning, real-time market data gathering, self-validation,
    and data-backed analysis. Examples: income statements, revenue trends,
    profitability analysis, market position.

    Args:
        query: The financial research question.
            e.g. "Analyze Tesla's revenue growth and profitability over the past 5 years"
    """
    return _run_dexter_query(query)


@tool("dexter_market_analysis", parse_docstring=True)
def dexter_market_analysis_tool(company: str, topic: str = "financial performance") -> str:
    """Focused market analysis via Dexter AI agent.

    Provides comprehensive analysis of a company including financial metrics,
    market position, and key trends.

    Args:
        company: The company or asset to analyze.
        topic: The analysis focus. Default is "financial performance".
    """
    query = f"Provide a comprehensive {topic} analysis of {company}. Include relevant financial metrics, market position, and key trends."
    return _run_dexter_query(query)
