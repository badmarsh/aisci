# Troubleshooting Guide

## Common Issues and Solutions

### 1. MCP Services Not Responding
**Issue:** Consensus or Scite MCP services return 502 or connection errors
**Solution:**
- Check the MCP proxy container status: `docker ps | grep mcp_proxy`
- Restart the container: `docker restart onyx-mcp_proxy-1`
- Verify the configuration: `/home/ubuntu/onyx_data/config/nginx_mcp_proxy.conf`

### 2. Physics Validation Mode Not Available
**Issue:** Physics Validation Mode persona doesn't appear in Onyx UI
**Solution:**
- Verify the persona was created: Check database or run the creation script again
- Restart Onyx services: `cd /home/ubuntu/onyx_data/deployment && docker-compose restart`

### 3. GPU Not Detected
**Issue:** GPU acceleration not working for document processing
**Solution:**
- Check NVIDIA drivers: `nvidia-smi`
- Verify Docker is configured for GPU access: `docker run --rm --gpus all nvidia/cuda:11.0-base-ubuntu20.04 nvidia-smi`
- Check Ollama container: `docker exec onyx-ollama-1 nvidia-smi`

### 4. API Connection Issues
**Issue:** Cannot connect to Onyx API
**Solution:**
- Verify API server is running: `docker ps | grep api_server`
- Check the API key is correctly set in environment
- Verify network connectivity between containers

### 5. Volume Mapping Problems
**Issue:** Files created by Onyx not appearing in expected locations
**Solution:**
- Verify volume configuration in `docker-compose.yml`
- Check permissions on mounted directories
- Ensure the directories exist on the host system

## Diagnostic Commands

### Check all Onyx containers:
```bash
docker ps | grep onyx
```

### Check MCP services:
```bash
curl -s http://localhost:8095/consensus/health
curl -s http://localhost:8095/scite/health
```

### Verify Physics Validation persona:
```bash
curl -s -H "Authorization: Bearer $ONYX_API_KEY" http://localhost:3000/api/admin/persona
```

### Check GPU status:
```bash
nvidia-smi
docker exec onyx-ollama-1 nvidia-smi
```

## When to Reset

If multiple issues persist:
1. Stop all Onyx services: `cd /home/ubuntu/onyx_data/deployment && docker-compose down`
2. Clear Docker system: `docker system prune -f`
3. Restart: `cd /home/ubuntu/onyx_data/deployment && docker-compose up -d`
4. Re-create the Physics Validation persona if needed