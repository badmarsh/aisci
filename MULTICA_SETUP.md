# Multica Setup Complete

## What's Been Done

1. ✅ Installed Multica CLI v0.3.12
2. ✅ Self-hosted Multica server running with Docker
3. ✅ Configured to avoid port conflicts with Onyx

## Services Running

- **Frontend**: http://localhost:3100
- **Backend**: http://localhost:8100
- **Database**: PostgreSQL (internal)

## Configuration

- Location: `/tmp/multica/`
- Dev verification code: `888888` (for local testing)
- No email configured (codes print to backend logs)

## Next Steps

### 1. Configure the CLI

Run this command to connect the CLI to your self-hosted instance:

```bash
cd /tmp/multica
multica setup self-host --server-url http://localhost:8100 --app-url http://localhost:3100
```

This will:
- Open your browser to http://localhost:3100
- Prompt you to log in with your email (marekjurk@proton.me)
- Use verification code: `888888`
- Store the auth token in `~/.multica/config.json`
- Start the daemon automatically

### 2. Verify the Daemon

After setup, check the daemon status:

```bash
multica daemon status
```

Should show: `online`

### 3. Create Your First Agent

In the web UI (http://localhost:3100):
- Go to **Settings → Agents**
- Click **New Agent**
- Name: e.g., "Physics Agent"
- Provider: Select "Kiro CLI" (auto-detected)
- Instructions: Add any specific guidance for the agent

Or via CLI:

```bash
multica agent create --name "Physics Agent" --provider kiro --instructions "Expert in physics simulations and data analysis"
```

### 4. Assign Your First Task

Create an issue and assign it to your agent:

```bash
multica issue create --title "Analyze physics simulation results" --assignee "Physics Agent"
```

Or use the web UI to create and assign issues.

## Troubleshooting

### Check Backend Logs
```bash
cd /tmp/multica
docker compose -f docker-compose.selfhost.yml logs backend -f
```

### Check Frontend Logs
```bash
cd /tmp/multica
docker compose -f docker-compose.selfhost.yml logs frontend -f
```

### Restart Services
```bash
cd /tmp/multica
FRONTEND_PORT=3100 BACKEND_PORT=8100 docker compose -f docker-compose.selfhost.yml restart
```

### Stop Services
```bash
cd /tmp/multica
docker compose -f docker-compose.selfhost.yml down
```

## Integration with aisci Project

Once agents are configured, you can:
1. Create issues for physics analysis tasks
2. Assign them to AI agents
3. Agents will work on the `/home/ubuntu/aisci` codebase
4. Track progress in real-time via the Multica dashboard

## Documentation

- Multica Docs: https://multica.ai/docs
- Self-hosting Guide: https://multica.ai/docs/self-host-quickstart
- GitHub: https://github.com/multica-ai/multica
