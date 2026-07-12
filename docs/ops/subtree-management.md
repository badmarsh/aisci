# Historical Vendored-Subtree Management Record

> Historical record only — not active operational guidance.

> **Historical record.** The listed vendored deployments are not present in
> the current checkout. Do not use these commands as current maintenance steps.

The `aisci` repository previously used Git submodules for external dependencies (`deer-flow`, `multica`, `open-computer-use`, `onyx-mcp-server`, `ppt-master`). 
To simplify the VS Code experience and track local modifications easily, these have been converted into **Git Subtrees** (vendored code).

## What This Means
- You **do not** need to manage separate `.git` histories for these folders.
- You **do not** need to `cd` into them to commit changes.
- You simply edit files anywhere in the repo and commit them to `aisci` just like any other project file.

## Fetching Upstream Updates
When the official upstream repository releases an update, you can fetch and merge it directly into your `aisci` repository without losing your local tweaks.

Run the appropriate `git subtree pull` command from the root of the `aisci` repository:

### 1. DeerFlow
```bash
git subtree pull --prefix deployment/deer-flow https://github.com/bytedance/deer-flow.git main --squash
```

### 2. Multica
```bash
git subtree pull --prefix deployment/multica https://github.com/multica-ai/multica.git main --squash
```

### 3. Open Computer Use
```bash
git subtree pull --prefix deployment/open-computer-use https://github.com/open-computer-use/open-computer-use.git main --squash
```

### 4. Onyx MCP Server
```bash
git subtree pull --prefix deployment/onyx/onyx-mcp-server https://github.com/onyx-dot-app/onyx-mcp-server.git main --squash
```

### 5. PPT Master
```bash
git subtree pull --prefix ppt-master https://github.com/hugohe3/ppt-master.git main --squash
```

> **Note:** The `--squash` flag is recommended. It prevents importing thousands of granular upstream commits into your `aisci` commit history, and instead merges the updates as a single incoming commit.
