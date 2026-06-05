#!/usr/bin/env python3
import sys
from pathlib import Path

def main():
    config_path = Path("deployment/deer-flow/config.example.yaml")
    if not config_path.exists():
        print(f"Error: {config_path} does not exist", file=sys.stderr)
        return 1

    content = config_path.read_text()

    # A. Add new agents after research-coordinator
    rc_block = """  - name: research-coordinator
    type: assistant
    capacity: 100"""
    
    new_agents = """  - name: fact-checker
    type: specialist
    capacity: 80
  - name: report-exporter
    type: operations
    capacity: 60
  - name: academic-scout
    type: specialist
    capacity: 80
  - name: vision-analyst
    type: specialist
    capacity: 60"""

    target_rc = rc_block
    replacement_rc = rc_block + "\n" + new_agents
    if target_rc in content:
        content = content.replace(target_rc, replacement_rc)
        print("Updated agents section.")
    else:
        print("Warning: research-coordinator block not found!")

    # B. Replace langgraph section
    target_langgraph = """langgraph:
  recursion_limit: 100
  thinking_enabled: true
  subagent_enabled: true
  context_management:
    max_turns: 50
    summary_threshold: 5
  memory:
    type: persistent
    storage: ./memory
    max_entries: 10000"""

    new_langgraph = """langgraph:
  recursion_limit: 150
  thinking_enabled: true
  subagent_enabled: true
  planner:
    strategy: tree_of_thoughts
    tot_branches: 3
    tot_depth: 4
    tot_evaluation_model: null
  context_management:
    max_turns: 50
    summary_threshold: 5
  memory:
    type: persistent
    storage: ./memory
    max_entries: 10000"""

    if target_langgraph in content:
        content = content.replace(target_langgraph, new_langgraph)
        print("Updated langgraph section.")
    else:
        # Try finding it with flexible spacing
        print("Warning: langgraph section not found exactly as expected!")

    # C & D. Add deep_think and swarm sections after langgraph, before models
    target_models_header = "# ============================================================================\n# Models Configuration\n# ============================================================================"
    
    deep_think_swarm = """# ============================================================================
# Deep Thinking
# ============================================================================
# When enabled, the coordinator runs an extended chain-of-thought reasoning
# block before producing the research plan. Controlled per-session via the
# UI lightbulb toggle or the API field `deep_think: true`.
deep_think:
  enabled: true
  model_name: null
  budget_tokens: 8192

# ============================================================================
# Swarm / Parallel Sub-task Execution
# ============================================================================
# Decomposes complex research queries into parallel async subtasks executed
# by independent researcher instances, then merges results.
swarm:
  enabled: true
  max_parallel_tasks: 4
  timeout_seconds: 600
  merge_strategy: ranked

"""
    if target_models_header in content:
        content = content.replace(target_models_header, deep_think_swarm + target_models_header)
        print("Added deep_think and swarm sections.")
    else:
        print("Warning: models header not found!")

    # E. Replace tool_groups
    target_tool_groups = """tool_groups:
  - name: web
  - name: file:read
  - name: file:write
  - name: bash
  - name: knowledge"""

    new_tool_groups = """tool_groups:
  - name: web
  - name: web:academic
  - name: file:read
  - name: file:write
  - name: bash
  - name: knowledge
  - name: memory
  - name: export"""

    if target_tool_groups in content:
        content = content.replace(target_tool_groups, new_tool_groups)
        print("Updated tool groups.")
    else:
        print("Warning: tool_groups not found!")

    # F. Add tools

    # 1. after web_search
    target_web_search = """  - name: web_search
    group: web
    use: deerflow.community.ddg_search.tools:web_search_tool
    max_results: 5"""

    web_search_additions = """

  - name: tavily_search
    group: web
    use: deerflow.community.tavily.tools:tavily_search_tool
    api_key: $TAVILY_API_KEY
    max_results: 5
    search_depth: advanced

  - name: brave_search
    group: web
    use: deerflow.community.brave_search.tools:brave_search_tool
    api_key: $BRAVE_API_KEY
    max_results: 5

  - name: exa_search
    group: web
    use: deerflow.community.exa.tools:exa_search_tool
    api_key: $EXA_API_KEY
    max_results: 5
    use_autoprompt: true
    type: neural

  - name: serper_search
    group: web
    use: deerflow.community.serper.tools:serper_search_tool
    api_key: $SERPER_API_KEY
    max_results: 5

  - name: parallel_web_search
    group: web
    use: deerflow.community.multi_search.tools:parallel_search_tool
    engines:
      - tavily
      - brave_search
      - ddg
    max_results_per_engine: 3
    dedup_threshold: 0.85"""

    if target_web_search in content:
        content = content.replace(target_web_search, target_web_search + web_search_additions)
        print("Added web search tools.")
    else:
        print("Warning: web_search not found!")

    # 2. after web_fetch
    target_web_fetch = """  - name: web_fetch
    group: web
    use: deerflow.community.jina_ai.tools:web_fetch_tool
    timeout: 10"""

    web_fetch_additions = """

  - name: firecrawl_fetch
    group: web
    use: deerflow.community.firecrawl.tools:firecrawl_fetch_tool
    api_key: $FIRECRAWL_API_KEY
    formats:
      - markdown
      - links
    timeout: 20"""

    if target_web_fetch in content:
        content = content.replace(target_web_fetch, target_web_fetch + web_fetch_additions)
        print("Added firecrawl_fetch tool.")
    else:
        print("Warning: web_fetch not found!")

    # 3. after image_search
    target_image_search = """  - name: image_search
    group: web
    use: deerflow.community.image_search.tools:image_search_tool
    max_results: 5"""

    academic_tools = """

  # --- Academic search ---
  - name: arxiv_search
    group: web:academic
    use: deerflow.community.arxiv.tools:arxiv_search_tool
    max_results: 10
    sort_by: relevance

  - name: semantic_scholar_search
    group: web:academic
    use: deerflow.community.semantic_scholar.tools:semantic_scholar_search_tool
    max_results: 10
    fields:
      - title
      - abstract
      - authors
      - year
      - citationCount
      - externalIds"""

    if target_image_search in content:
        content = content.replace(target_image_search, target_image_search + academic_tools)
        print("Added academic search tools.")
    else:
        print("Warning: image_search not found!")

    # 4. after grep
    target_grep = """  - name: grep
    group: file:read
    use: deerflow.sandbox.tools:grep_tool
    max_results: 100"""

    file_reader_additions = """

  - name: pdf_reader
    group: file:read
    use: deerflow.community.pdf.tools:pdf_reader_tool
    extract_images: false
    max_pages: 100

  - name: spreadsheet_reader
    group: file:read
    use: deerflow.community.spreadsheet.tools:spreadsheet_reader_tool
    max_rows: 5000"""

    if target_grep in content:
        content = content.replace(target_grep, target_grep + file_reader_additions)
        print("Added file readers.")
    else:
        print("Warning: grep not found!")

    # 5. after onyx_search
    target_onyx_search = """  - name: onyx_search
    group: knowledge
    use: deerflow.community.onyx.tools:onyx_search_tool
    num_hits: 5"""

    knowledge_memory_export_additions = """

  - name: vector_search
    group: knowledge
    use: deerflow.community.qdrant.tools:qdrant_search_tool
    url: ${QDRANT_URL:-http://localhost:6333}
    api_key: $QDRANT_API_KEY
    collection: deerflow-research
    top_k: 8
    score_threshold: 0.6

  - name: vector_upsert
    group: knowledge
    use: deerflow.community.qdrant.tools:qdrant_upsert_tool
    url: ${QDRANT_URL:-http://localhost:6333}
    api_key: $QDRANT_API_KEY
    collection: deerflow-research
    auto_embed: true
    embedding_model: sentence-transformers/all-MiniLM-L6-v2

  # --- Memory ---
  - name: session_memory_read
    group: memory
    use: deerflow.community.mem0.tools:mem0_read_tool
    api_key: $MEM0_API_KEY
    top_k: 5

  - name: session_memory_write
    group: memory
    use: deerflow.community.mem0.tools:mem0_write_tool
    api_key: $MEM0_API_KEY

  # --- Export ---
  - name: export_pdf
    group: export
    use: deerflow.community.export.tools:export_pdf_tool
    engine: playwright
    output_dir: .deer-flow/exports

  - name: export_docx
    group: export
    use: deerflow.community.export.tools:export_docx_tool
    output_dir: .deer-flow/exports

  - name: export_notion
    group: export
    use: deerflow.community.export.tools:export_notion_tool
    api_key: $NOTION_API_KEY
    parent_page_id: null

  - name: citation_manager
    group: export
    use: deerflow.community.citations.tools:citation_manager_tool
    default_style: apa

  - name: mermaid_diagram
    group: export
    use: deerflow.community.mermaid.tools:mermaid_diagram_tool
    theme: default"""

    if target_onyx_search in content:
        content = content.replace(target_onyx_search, target_onyx_search + knowledge_memory_export_additions)
        print("Added vector, memory, and export tools.")
    else:
        print("Warning: onyx_search not found!")

    # G. Add fact_checking section after tool_search
    target_tool_search = """tool_search:
  enabled: true"""

    fact_checking_block = """

# ============================================================================
# Fact-Checking
# ============================================================================
# Post-processing agent that cross-checks key claims in the final report
# against a second search pass before output is delivered to the user.
fact_checking:
  enabled: true
  model_name: null
  max_claims_to_check: 10
  search_engine: tavily"""

    if target_tool_search in content:
        content = content.replace(target_tool_search, target_tool_search + fact_checking_block)
        print("Added fact-checking section.")
    else:
        print("Warning: tool_search not found!")

    # H. Replace uploads section
    target_uploads = """uploads:
  max_files: 10
  max_file_size: 52428800
  max_total_size: 104857600
  auto_convert_documents: false
  pdf_converter: auto"""

    new_uploads = """uploads:
  max_files: 20
  max_file_size: 104857600
  max_total_size: 524288000
  auto_convert_documents: true
  pdf_converter: auto
  supported_extensions:
    - .pdf
    - .docx
    - .txt
    - .md
    - .csv
    - .xlsx
    - .xls
    - .json
    - .png
    - .jpg
    - .jpeg
    - .webp"""

    if target_uploads in content:
        content = content.replace(target_uploads, new_uploads)
        print("Updated uploads section.")
    else:
        print("Warning: uploads section not found!")

    # J. Add e2b_fallback inside sandbox
    target_sandbox_idle = "  idle_timeout: 1800"
    e2b_fallback = """
  # E2B cloud sandbox fallback (used when local AIO sandbox is unavailable)
  e2b_fallback:
    enabled: false
    api_key: $E2B_API_KEY
    template: python3"""

    if target_sandbox_idle in content:
        content = content.replace(target_sandbox_idle, target_sandbox_idle + e2b_fallback)
        print("Added e2b_fallback block inside sandbox configuration.")
    else:
        print("Warning: sandbox idle_timeout not found!")

    # K. Add subagent entries for new agents
    target_bash_subagent = """    bash:
      timeout_seconds: 300
      max_turns: 80"""

    new_subagents = """
    academic-scout:
      timeout_seconds: 600
      max_turns: 60
    fact-checker:
      timeout_seconds: 300
      max_turns: 40"""

    if target_bash_subagent in content:
        content = content.replace(target_bash_subagent, target_bash_subagent + new_subagents)
        print("Added subagent configurations.")
    else:
        print("Warning: bash subagent config not found!")

    # L. Memory section updates
    target_memory = """memory:
  enabled: true
  storage_path: memory.json
  debounce_seconds: 30
  model_name: null
  max_facts: 100
  fact_confidence_threshold: 0.7
  injection_enabled: true
  max_injection_tokens: 2000"""

    new_memory = """memory:
  enabled: true
  storage_path: memory.json
  debounce_seconds: 30
  model_name: null
  max_facts: 200
  fact_confidence_threshold: 0.7
  injection_enabled: true
  max_injection_tokens: 2000

# ============================================================================
# Vector Memory (Qdrant-backed cross-session research recall)
# ============================================================================
vector_memory:
  enabled: false
  backend: qdrant
  url: ${QDRANT_URL:-http://localhost:6333}
  api_key: $QDRANT_API_KEY
  collection: deerflow-research
  embedding_model: sentence-transformers/all-MiniLM-L6-v2
  auto_index_reports: true
  auto_index_tool_results: false
  top_k: 8
  score_threshold: 0.6

# ============================================================================
# Async Task Queue
# ============================================================================
# Background worker queue so long research tasks survive browser disconnects.
# When enabled, research jobs are enqueued in Redis and processed by ARQ workers.
task_queue:
  enabled: false
  backend: arq
  redis_url: ${REDIS_URL:-redis://localhost:6379/0}
  max_jobs: 20
  job_timeout: 3600
  result_ttl: 86400
  retry_on_failure: true
  max_retries: 3

# ============================================================================
# SSE Resilience
# ============================================================================
# Reconnect buffer backed by Redis so clients can resume streaming after
# network drops without losing intermediate research events.
sse:
  reconnect_buffer:
    enabled: false
    backend: redis
    redis_url: ${REDIS_URL:-redis://localhost:6379/0}
    buffer_ttl: 300"""

    if target_memory in content:
        content = content.replace(target_memory, new_memory)
        print("Updated memory and added vector_memory, task_queue, sse blocks.")
    else:
        print("Warning: memory block not found!")

    # P, Q, R, S, T. Add podcast, report_export, metrics, security, rate_limiting blocks
    # We add them right before "database:" block
    target_database_comment = "# ============================================================================\n# Database"
    
    infra_obs_blocks = """# ============================================================================
# TTS / Podcast
# ============================================================================
podcast:
  enabled: true
  provider: auto
  providers:
    elevenlabs:
      api_key: $ELEVENLABS_API_KEY
      voice_host: pNInz6obpgDQGcFmaJgB
      voice_guest: EXAVITQu4vr4xnSDxMaL
    openai_tts:
      api_key: $OPENAI_TTS_API_KEY
      voice_host: alloy
      voice_guest: nova
    volcengine:
      api_key: $VOLCENGINE_API_KEY
    coqui:
      enabled: false
      model: tts_models/multilingual/multi-dataset/xtts_v2
  format: multi-voice

# ============================================================================
# Report Export
# ============================================================================
report_export:
  formats:
    - markdown
    - pdf
    - docx
    - json
  versioning:
    enabled: true
    max_versions: 10
    storage: .deer-flow/report-versions
  citation_style: apa
  auto_generate_diagrams: true
  include_confidence_scores: true

# ============================================================================
# Observability / Metrics
# ============================================================================
metrics:
  prometheus:
    enabled: false
    port: 9090
    path: /metrics
  track:
    - research_duration_seconds
    - tool_call_count
    - llm_token_usage
    - error_rate
    - search_results_quality

# ============================================================================
# Security
# ============================================================================
security:
  secret_scanning:
    enabled: true
    block_on_detection: true
  input_guardrails:
    enabled: false
    provider: nemo
  output_guardrails:
    enabled: false

# ============================================================================
# Rate Limit Handling
# ============================================================================
rate_limiting:
  retry_strategy: exponential_backoff
  max_retries: 5
  base_delay_seconds: 1.0
  max_delay_seconds: 60.0
  jitter: true

# ============================================================================
# Database
"""

    if target_database_comment in content:
        content = content.replace(target_database_comment, infra_obs_blocks)
        print("Added podcast, report_export, metrics, security, rate_limiting sections.")
    else:
        print("Warning: database comment not found!")

    # Write the modified content back
    config_path.write_text(content)
    print("Done. config.example.yaml updated successfully.")

if __name__ == "__main__":
    sys.exit(main())
