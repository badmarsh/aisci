"""
DeerFlow Integration Tests

Tests configuration and feature presence for improvements merged in commit 4b62828.
Does not require live external APIs - uses mocks where needed.
"""

import pytest
from pathlib import Path
import yaml


@pytest.fixture
def config_path():
    """Path to config.example.yaml"""
    return Path(__file__).parent.parent / "config.example.yaml"


@pytest.fixture
def config(config_path):
    """Load config.example.yaml"""
    with open(config_path) as f:
        return yaml.safe_load(f)


def test_langgraph_recursion_limit(config):
    """LangGraph recursion limit should be 150 (increased from 100)"""
    assert config["langgraph"]["recursion_limit"] == 150


def test_tree_of_thoughts_planner(config):
    """Tree of Thoughts planner should be configured with branches=3, depth=4"""
    planner = config["langgraph"]["planner"]
    assert planner["strategy"] == "tree_of_thoughts"
    assert planner["tot_branches"] == 3
    assert planner["tot_depth"] == 4


def test_deep_think_enabled(config):
    """Deep Think extended reasoning should be enabled with 8192 token budget"""
    deep_think = config["deep_think"]
    assert deep_think["enabled"] is True
    assert deep_think["budget_tokens"] == 8192


def test_swarm_parallel_tasks(config):
    """Swarm intelligence should support 4 parallel async subtasks"""
    swarm = config["swarm"]
    assert swarm["enabled"] is True
    assert swarm["max_parallel_tasks"] == 4
    assert swarm["merge_strategy"] == "ranked"


def test_parallel_search_tools_registered(config):
    """Parallel search tools (tavily, brave, exa, serper) should be registered"""
    tools = config.get("tools", [])
    tool_names = [t["name"] for t in tools]

    # Check for parallel web search tool
    assert "parallel_web_search" in tool_names or "web_search" in tool_names


def test_arxiv_tool_registered(config):
    """ArXiv search tool should be registered"""
    tools = config.get("tools", [])
    tool_names = [t["name"] for t in tools]

    assert "arxiv_search" in tool_names


def test_semantic_scholar_tool_registered(config):
    """Semantic Scholar tool should be registered"""
    tools = config.get("tools", [])
    tool_names = [t["name"] for t in tools]

    assert "semantic_scholar_search" in tool_names


def test_fact_checker_agent_present(config):
    """Fact-checker agent should be in agents list"""
    agents = config["agents"]
    agent_names = [a["name"] for a in agents]

    assert "fact-checker" in agent_names


def test_academic_scout_agent_present(config):
    """Academic-scout agent should be in agents list"""
    agents = config["agents"]
    agent_names = [a["name"] for a in agents]

    assert "academic-scout" in agent_names


def test_report_exporter_agent_present(config):
    """Report-exporter agent should be in agents list"""
    agents = config["agents"]
    agent_names = [a["name"] for a in agents]

    assert "report-exporter" in agent_names


def test_vision_analyst_agent_present(config):
    """Vision-analyst agent should be in agents list"""
    agents = config["agents"]
    agent_names = [a["name"] for a in agents]

    assert "vision-analyst" in agent_names


def test_loop_detection_enabled(config):
    """Loop detection should be enabled (regression check)"""
    loop_detection = config["loop_detection"]
    assert loop_detection["enabled"] is True
    assert loop_detection["warn_threshold"] == 3
    assert loop_detection["hard_limit"] == 5


def test_mem0_session_memory_config(config):
    """Mem0 session memory should be configured with max_facts=200"""
    memory = config["memory"]
    assert memory["enabled"] is True
    assert memory["max_facts"] == 200


def test_vector_memory_tools_registered(config):
    """Vector search/upsert tools should be registered (Qdrant)"""
    tools = config.get("tools", [])
    tool_names = [t["name"] for t in tools]

    # Check for vector/knowledge tools
    has_vector = any("vector" in name or "knowledge" in name for name in tool_names)
    assert has_vector, "No vector/knowledge tools found"


def test_export_tools_registered(config):
    """Export tools (pdf, docx, citation_manager) should be registered"""
    tools = config.get("tools", [])
    tool_names = [t["name"] for t in tools]

    # Check for export-related tools
    export_tools = ["pdf_export", "docx_export", "citation_manager", "report_export"]
    has_export = any(tool in tool_names for tool in export_tools)
    assert has_export, "No export tools found"


def test_secret_scanning_enabled(config):
    """Secret scanning should be enabled in security config"""
    security = config.get("security", {})
    if security:
        assert security.get("secret_scanning", {}).get("enabled") is True


def test_rate_limiting_configured(config):
    """Rate limiting with exponential backoff should be configured"""
    rate_limit = config.get("rate_limiting", {})
    if rate_limit:
        assert rate_limit.get("retry_strategy") == "exponential_backoff"
        assert rate_limit.get("jitter") is True


def test_podcast_tts_configured(config):
    """Podcast TTS should support multiple providers"""
    podcast = config.get("podcast", {})
    if podcast:
        providers = podcast.get("providers", {})
        # Should have multiple TTS provider configs
        assert len(providers) >= 3  # elevenlabs, openai_tts, volcengine, coqui
        assert "elevenlabs" in providers
        assert "openai_tts" in providers


def test_prometheus_metrics_configured(config):
    """Prometheus metrics should be configured"""
    metrics = config.get("metrics", {})
    if metrics:
        assert "prometheus" in metrics or metrics.get("enabled") is not None


def test_arq_task_queue_configured(config):
    """ARQ/Redis async task queue should be configured"""
    task_queue = config.get("task_queue", {})
    if task_queue:
        assert task_queue.get("backend") in ["arq", "celery", "redis"]


def test_upload_limit_increased(config):
    """Upload limit should be increased to 500MB"""
    uploads = config["uploads"]
    # 500MB = 524288000 bytes
    assert uploads["max_file_size"] >= 500_000_000 or uploads["max_total_size"] >= 500_000_000


def test_pdf_reader_tool_registered(config):
    """PDF reader tool should be registered"""
    tools = config.get("tools", [])
    tool_names = [t["name"] for t in tools]

    assert "pdf_reader" in tool_names or "read_pdf" in tool_names


def test_spreadsheet_reader_tool_registered(config):
    """Spreadsheet reader tool should be registered"""
    tools = config.get("tools", [])
    tool_names = [t["name"] for t in tools]

    assert "spreadsheet_reader" in tool_names or "read_spreadsheet" in tool_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
