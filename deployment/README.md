# Onyx Deployment Directory

This directory contains all deployment-related files for the Onyx system, organized by platform.

## Directory Structure:
- `/onyx/` - Onyx-specific deployment files:
  - `docker-compose.yml` - Main Docker Compose configuration for Onyx services
  - `nginx_mcp_proxy.conf` - Configuration for the Model Context Protocol (MCP) proxy
  - `.env` - Environment variables for the deployment
  - `env.template` - Template for environment variables
  - `nginx_configs/` - Nginx configuration files
  - `litellm_config.yaml` - Configuration for LiteLLM service
  - `Dockerfile.backend` - Dockerfile for the backend service
  - `openapi.json` - OpenAPI specification
  - `trigger_reindex.py` - Script to trigger reindexing
  - `DEPLOYMENT_STATUS.md` - Current status of deployment

- `/deer-flow/` - Deer-Flow-specific deployment files (future)

## Purpose:
This directory contains all necessary files to deploy and run the Onyx system with the physics validation features.