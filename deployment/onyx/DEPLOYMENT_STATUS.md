# Onyx Deployment Status

## Current State
The Onyx system was running but had to be stopped for reorganization. However, there are issues with the docker-compose system in this environment that prevent restarting it using standard commands.

## Known Issues
- `docker-compose` command results in bus errors
- Docker Compose plugin is reporting "failed to fetch metadata" errors
- Cannot start the system using `docker compose up -d`

## Manual Deployment Required
Due to the environment limitations, a manual deployment approach would be needed:

1. Use individual `docker run` commands for each service based on the docker-compose.yml file
2. Or fix the docker-compose installation in the environment

## Services That Need to Start
Based on the docker-compose.yml file, the following services are required:
- api_server (backend)
- background (background tasks)
- web_server (frontend)
- inference_model_server (ML models)
- indexing_model_server (indexing models)
- relational_db (PostgreSQL)
- index (Vespa search)
- opensearch (search engine)
- nginx (web proxy)
- cache (Redis)
- minio (file storage)
- code-interpreter (code execution)
- ollama (local LLMs)
- unstructured (document parsing)
- litellm (LLM router)
- mcp_proxy (MCP proxy)

## Deployment Directory Structure
All Onyx deployment files are now properly organized in:
- `/home/ubuntu/onyx_data/deployment/onyx/`

This includes:
- `docker-compose.yml` - Main deployment configuration
- `nginx_mcp_proxy.conf` - MCP service proxy configuration
- `.env`, `env.template` - Environment configuration
- `litellm_config.yaml` - LiteLLM configuration
- `Dockerfile.backend` - Backend Dockerfile
- `nginx_configs/` - Nginx configuration files
- `openapi.json` - API specification
- `trigger_reindex.py` - Reindexing script

## Next Steps
To fully restart the Onyx system, you would need to either:
1. Fix the docker-compose installation in the environment
2. Manually deploy each service using individual docker commands
3. Use an alternative orchestration method
