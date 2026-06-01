# GitHub App Setup for Multica Integration

This guide walks through connecting a self-hosted Multica instance to GitHub via a GitHub App. The integration enables webhook-based automation (PR status, commit checks, issue events) from GitHub into Multica.

---

## Overview

Multica's GitHub integration needs two environment variables:

- `GITHUB_APP_SLUG` — the URL-safe name of your GitHub App (e.g. `multica-ai` becomes `https://github.com/apps/multica-ai`)
- `GITHUB_WEBHOOK_SECRET` — a shared secret used to verify that incoming webhooks genuinely came from GitHub

These are set in `/tmp/multica/.env` at lines 189–191 (commented out by default).

---

## Prerequisites: expose the backend with a tunnel

GitHub's servers cannot reach `localhost`. Before creating the GitHub App, expose the Multica backend on a public URL using Cloudflare Tunnel (`cloudflared`).

### 1a. Start a quick tunnel (trycloudflare)

```bash
cloudflared tunnel --url http://localhost:8100
```

This prints a URL like:

```
https://<random>.trycloudflare.com
```

That URL proxies all traffic to `localhost:8100`. Keep the process running — closing it kills the tunnel. Test it:

```bash
curl https://<random>.trycloudflare.com/healthz
# → {"status":"ok","checks":{"db":"ok","migrations":"ok"}}
```

The webhook endpoint will be:

```
https://<random>.trycloudflare.com/api/webhooks/github
```

> **Quick tunnels are ephemeral and unauthenticated (trycloudflare).** Anyone with the URL can reach your backend. For production, create a named tunnel with an authenticated origin certificate.

### 1b. Persistent named tunnel (production)

```bash
# Login (opens browser — authenticate with your Cloudflare account)
cloudflared tunnel login

# Create the tunnel
cloudflared tunnel create multica

# Configure it
cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: multica
credentials-file: /root/.cloudflared/multica.json
ingress:
  - hostname: webhook.yourdomain.com
    service: http://localhost:8100
  - service: http_status:404
EOF

# Create DNS record
cloudflared tunnel route dns multica webhook.yourdomain.com

# Install as a system service
cloudflared service install

# Start
systemctl start cloudflared
```

Then use `https://webhook.yourdomain.com/api/webhooks/github` as the webhook URL.

---

## Step-by-step

### 2. Create a GitHub App

Navigate to the GitHub App creation page:

**https://github.com/settings/apps/new**

To save time, open this pre-filled URL — it sets the name, permissions, webhook URL, and events to match the expected config below. You only need to paste the webhook secret into the **Webhook secret** field:

```
https://github.com/settings/apps/new?name=multica-ai&url=http://localhost:3000&webhook_active=true&webhook_url=https://<random>.trycloudflare.com/api/webhooks/github&setup_url=https://<random>.trycloudflare.com/api/github/setup&setup_on_update=true&public=false&pull_requests=read&metadata=read&events[]=pull_request
```

If you prefer to set it up manually, follow these fields:

- **GitHub App name**: `Multica AI` (slug: `multica-ai` — use this slug in `.env`)
- **Homepage URL**: `http://localhost:3000`
- **Webhook active**: ✅ checked
- **Webhook URL**: `https://<random>.trycloudflare.com/api/webhooks/github`
  (or your persistent tunnel domain)
- **Webhook secret**: (paste the secret from `.env` — see step 4)
- **Permissions**:
  - Pull requests: **Read-only**
  - Metadata: **Read-only**
- **Subscribe to events**:
  - [x] Pull request
- **Where can this App be installed?**: **Only on this account**
- **Setup URL** (optional): `https://<random>.trycloudflare.com/api/github/setup`
- **Redirect on update**: ✅ checked

Click **Create GitHub App**.

### Required permissions

| Permission     | Level      | Why                                     |
|----------------|------------|-----------------------------------------|
| Pull requests  | Read-only  | Receive PR open/close/sync webhooks     |
| Metadata       | Read-only  | Read repo metadata for webhook delivery |

These are the minimum permissions needed. Do not grant write access unless a future feature requires it.

### 3. Webhook configuration

- **URL**: `https://<random>.trycloudflare.com/api/webhooks/github`
  (or your persistent tunnel domain)
- **Secret**: the value of `GITHUB_WEBHOOK_SECRET` from `.env` (see step 4)
- **Events**: `pull_request`

> **Note on reachability:** The tunnel URL must be used here — GitHub's servers cannot deliver webhooks to `localhost:8100`. The Cloudflare tunnel (step 1) proxies the public URL to your local backend.

### 4. Generate and set GITHUB_WEBHOOK_SECRET

If one is not already set, generate a secure random secret:

```bash
openssl rand -hex 32
```

Then add it to `/tmp/multica/.env`:

```bash
# At line 191, uncomment and set:
GITHUB_WEBHOOK_SECRET=<the generated hex string>
```

A secret is already pre-configured in `.env` (line 191) — you can reuse that value or regenerate.

### 5. Find GITHUB_APP_SLUG

The slug is the tail of the App's public URL:

```
https://github.com/apps/<slug>
```

For example, if your App is named `multica-ai`, the slug is `multica-ai`. The slug is also visible on the App's settings page at `https://github.com/settings/apps/<slug>`.

Set it in `.env`:

```bash
# At line 190, uncomment and set:
GITHUB_APP_SLUG=multica-ai
```

> The slug in `.env` **must** match the slug GitHub assigns (usually the name, lowercased, with special chars normalized). If they don't match, webhook verification will fail silently.

### 6. Set environment variables in /tmp/multica/.env

Open `/tmp/multica/.env` and ensure these lines are **uncommented** (no leading `#`) and set correctly:

```
GITHUB_APP_SLUG=multica-ai
GITHUB_WEBHOOK_SECRET=b46b7b59065ee8d1a38023525bdf9b6e6ee346ef6ebaecc03f185e4925e6107e
```

The exact line numbers are 189–191. The commented-out form looks like:

```
# GITHUB_APP_SLUG is the tail of https://github.com/apps/<slug>.
# GITHUB_APP_SLUG=multica-ai
# GITHUB_WEBHOOK_SECRET=...
```

Remove the `#` and the space after it.

### 7. Restart the Multica backend

Changes to `.env` take effect only after a restart.

**Docker Compose (self-hosted):**

```bash
docker compose -f /path/to/multica/docker-compose.selfhost.yml down
docker compose -f /path/to/multica/docker-compose.selfhost.yml up -d
```

Or using the Makefile:

```bash
make selfhost
```

**Kubernetes:**

```bash
kubectl -n multica rollout restart deploy/multica-backend
```

---

## Verification

After restarting, confirm the integration is active:

1. Check the backend health endpoint:
   ```bash
   curl http://localhost:8100/healthz
   ```
2. Open the Multica web UI at `http://localhost:3000` and navigate to **Settings → GitHub**. The "Connect GitHub" button should be enabled (not greyed out).
3. Trigger a test webhook (e.g. open a PR on a repo where the App is installed) and watch the backend logs:
   ```bash
   docker compose -f docker-compose.selfhost.yml logs --tail=50 multica-backend
   ```
   Look for `POST /api/webhooks/github` with a `200` response.

---

## Can this be automated further?

**Not fully.** GitHub requires a human to click **Create GitHub App** in a browser — there is no headless API to register a new App. However, the pre-filled URL above reduces the workflow to:

1. Open the pre-fill URL
2. Paste the webhook secret
3. Click **Create GitHub App**
4. No code changes needed — `.env` values already match

The integration does **not** use a personal access token or OAuth token, so `gh auth token` produces a credential the integration has no field for.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| "Connect GitHub" button greyed out | One or both env vars missing | Check `GITHUB_APP_SLUG` and `GITHUB_WEBHOOK_SECRET` are set and uncommented in `.env` |
| Webhooks return 404 | Slug mismatch | Verify `GITHUB_APP_SLUG` matches the App URL path at `https://github.com/settings/apps/<slug>` |
| Webhooks return 401 | Secret mismatch | Regenerate the webhook secret in GitHub App settings and update `.env` |
| No webhooks delivered | Tunnel not running or URL mismatch | Ensure `cloudflared` is running (step 1) and the webhook URL in the GitHub App settings matches the tunnel URL |
| `gh api /apps/<slug>` returns 404 | App was never created | Complete step 2 (Create GitHub App) — the App must exist before it can receive traffic |
