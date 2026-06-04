---
name: deploy-web-app
description: Deploy a GitHub repository or ZIP file attachment as a live web application inside the sandbox and show it in the artifact browser. Clone or extract, install dependencies, build/start the server, and generate an HTML preview artifact that embeds the running app.
---

## Overview

When a user provides a GitHub repository URL, uploads a ZIP file, or asks to deploy/run a web app, use this skill to:

1. **Source the code**: Clone a git repo OR extract a ZIP file attachment
2. Detect the project type (Node.js, Python, Go, etc.)
3. Install dependencies and build/start the development server
4. Discover the sandbox URL via helper scripts or the `/api/sandbox/info` endpoint
5. Generate an HTML preview artifact that embeds the running app in the chat artifact browser

## Input Sources

### Option A: GitHub Repository URL

When the user provides a URL like `https://github.com/user/app`:

```bash
cd /tmp && git clone --depth 1 <REPO_URL> app && cd app
```

### Option B: ZIP File Attachment

When the user uploads a `.zip` file attachment:

1. **Find and extract the ZIP** using the bundled helper script:

```bash
# Auto-find the most recent uploaded ZIP and extract it:
python3 /mnt/skills/public/deploy-web-app/scripts/extract_zip.py --auto --output-dir /tmp/app

# Or list available ZIPs first:
python3 /mnt/skills/public/deploy-web-app/scripts/extract_zip.py --list

# Or extract a specific file:
python3 /mnt/skills/public/deploy-web-app/scripts/extract_zip.py /mnt/user-data/uploads/my-app.zip --output-dir /tmp/app
```

2. **Manual extraction** (if the helper script fails):

```bash
mkdir -p /tmp/app && cd /tmp/app
unzip -q /mnt/user-data/uploads/<filename>.zip
# If the ZIP extracts into a subdirectory, flatten it:
if [ $(ls -1 | wc -l) -eq 1 ] && [ -d "$(ls -1)" ]; then
    mv $(ls -1)/* . 2>/dev/null; mv $(ls -1)/.* . 2>/dev/null; rmdir $(ls -1) 2>/dev/null
fi
```

3. Proceed to Step 2 (Detect Project Type) as normal.

## Helper Scripts

Three helper scripts are bundled with this skill at `/mnt/skills/public/deploy-web-app/scripts/`:

- **`extract_zip.py`** — Find and extract ZIP file attachments. Use `--auto` to auto-detect, `--list` to see available ZIPs
- **`discover_sandbox_url.py`** — Queries the gateway to find the sandbox URL for the current thread
- **`generate_preview.py --sandbox-url <URL>`** — Creates an HTML iframe artifact at `/mnt/user-data/outputs/preview/index.html`

Use these scripts instead of manual extraction/curl/HTML creation when available.

## Workflow

### Step 1: Get the Source Code

**From GitHub:**

```bash
cd /tmp && git clone --depth 1 <REPO_URL> app && cd app
```

**From ZIP attachment:**

```bash
python3 /mnt/skills/public/deploy-web-app/scripts/extract_zip.py --auto --output-dir /tmp/app && cd /tmp/app
```

### Step 2: Detect Project Type

Examine the root directory for clues:

| File present        | Project type | Install command                          | Start command                                    |
|---------------------|--------------|------------------------------------------|--------------------------------------------------|
| `package.json`      | Node.js      | `npm install` (or `pnpm install`)         | `npm run dev` or `npm start` (check `scripts`)   |
| `requirements.txt`  | Python       | `pip install -r requirements.txt`        | `python app.py` or `flask run` or `uvicorn ...` |
| `pyproject.toml`    | Python       | `pip install .` or `pip install -e .`    | Look in pyproject for entry point               |
| `go.mod`            | Go           | `go mod download`                        | `go run .` or `go run cmd/...`                   |
| `Cargo.toml`        | Rust         | `cargo build`                            | `cargo run`                                      |
| `Makefile`          | Any          | `make` or `make install`                 | `make run` or `make serve`                       |
| `CMakeLists.txt`    | C/C++        | `cmake -B build && cmake --build build` | `./build/<binary>`                               |

**Important**: Read `package.json` `scripts` field or Python entry points to find the correct dev/start command. Look for `dev`, `start`, `serve`, `preview` scripts.

### Step 3: Install Dependencies and Start Server

Install dependencies, then start the server **in the background** on a specific port:

```bash
# Node.js example
npm install
nohup npm run dev -- --port 39120 --host 0.0.0.0 > /tmp/server.log 2>&1 &
sleep 5

# Verify it's running
curl -s -o /dev/null -w "%{http_code}" http://localhost:39120
```

**Critical**: The server MUST bind to `0.0.0.0` (not `localhost` or `127.0.0.1`) and use port `39120` (the sandbox's default exposed port).

If the app uses a different port, you can still start it on any port, but you'll need to discover the actual host port mapping in Step 4.

### Step 4: Discover the Sandbox URL

**Preferred**: Use the bundled helper script:

```bash
python3 /mnt/skills/public/deploy-web-app/scripts/discover_sandbox_url.py
```

If that fails, fall back to the gateway API:

```bash
curl -s "http://localhost:2026/api/sandbox/info?thread_id=<THREAD_ID>" | python3 -c "import sys,json; print(json.load(sys.stdin)['sandbox_url'])"
```

Store the result in an environment variable for use in Step 5.

### Step 5: Generate the Preview Artifact

**Preferred**: Use the bundled helper script:

```bash
python3 /mnt/skills/public/deploy-web-app/scripts/generate_preview.py --sandbox-url "$SANDBOX_URL"
```

This creates `/mnt/user-data/outputs/preview/index.html` with an embedded iframe pointing to the running app.

**Manual fallback**: If the script is unavailable, create the HTML file yourself:

```bash
mkdir -p /mnt/user-data/outputs/preview
# Create HTML with iframe pointing to $SANDBOX_URL (see reference below)
```

### Step 6: Copy to Host-Visible Directory

By default the agent works in `/mnt/user-data/workspace/` which is buried in DeerFlow's internal thread data.
Copy the deployed project to a visible location on the host so the user can see it:

```bash
# Create a project directory visible on the host at /home/ubuntu/aisci/deployment/projects/
PROJECT_NAME=$(basename $(pwd) | sed 's/[^a-zA-Z0-9_-]//g' | head -c 50)
mkdir -p /mnt/host/aisci/deployment/projects/${PROJECT_NAME}
cp -r ./* /mnt/host/aisci/deployment/projects/${PROJECT_NAME}/ 2>/dev/null
cp -r .[!.]* /mnt/host/aisci/deployment/projects/${PROJECT_NAME}/ 2>/dev/null
echo "Project copied to: /mnt/host/aisci/deployment/projects/${PROJECT_NAME}/"
```

This ensures the user can find the deployed code in their project tree under `deployment/projects/`.

### Step 7: Confirm to the User

Tell the user:
- The app is deployed and running
- The URL they can access directly: `<SANDBOX_URL>`
- The artifact preview is available at: `preview/index.html` in the artifacts panel

## Error Handling

- **Port already in use**: Kill the existing process (`fuser -k 39120/tcp`) and restart
- **npm install fails**: Try `npm install --legacy-peer-deps` or `pnpm install`
- **Python import errors**: Check if a `Makefile`, `setup.py`, or `pyproject.toml` needs to be run first
- **Server won't start on 0.0.0.0**: Start on any port, then set the iframe URL to `http://localhost:<port>` and note the user must access from the host machine
- **Build step required** (e.g., Vite, Webpack, TypeScript): Run the build command first (`npm run build`), then serve the `dist/` or `build/` directory with `npx serve dist -l 39120`

## Notes

- The sandbox filesystem at `/mnt/user-data/outputs/` is mapped to the artifact browser. Any HTML file saved there can be previewed.
- For static-only sites (no server needed), just build the project and copy the output to `/mnt/user-data/outputs/preview/`, then create a simple `index.html` wrapper.
- For apps with API backends, start the backend first, then the frontend, and ensure the frontend's API base URL points to the correct internal address.
