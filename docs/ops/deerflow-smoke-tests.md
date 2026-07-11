# DeerFlow Smoke Tests

Minimal end-to-end verification that DeerFlow agents can reach Onyx and execute tools. Run after any DeerFlow rebuild, config change, or Onyx stack restart.

---

## 1. UI Smoke Test (manual)

**Goal:** Confirm the full UI→gateway→Onyx path works.

1. Open http://localhost:2026 and log in.
2. Start a new chat.
3. Send: `Search the Onyx knowledge base for "Tsallis statistics" and summarize what you find.`
4. **Expected:** The agent calls `onyx_search` (visible in the tool call stream), returns at least one result with a document title and content snippet, and does not error.
5. **Failure indicators:** "No documents found", tool call error, or the agent answers from training data without citing a source.

---

## 2. API Smoke Test (curl)

**Goal:** Confirm the gateway API is reachable and auth works.

```bash
# Get a JWT token (replace credentials)
TOKEN=$(curl -s -X POST http://localhost:2026/api/v1/auth/login/local \
  -H "Content-Type: application/json" \
  -d '{"email":"marekjurk@proton.me","password":"YOUR_PASSWORD"}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])")

# Create a thread
THREAD=$(curl -s -X POST http://localhost:2026/api/threads \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -c "import json,sys; print(json.load(sys.stdin)['thread_id'])")

echo "Thread: $THREAD"

# Run a search query
curl -s -X POST "http://localhost:2026/api/threads/$THREAD/runs/stream" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"input":{"messages":[{"role":"user","content":"Search Onyx for Tsallis statistics"}]},"stream_mode":["values"]}' \
  | grep -o '"content":"[^"]*"' | head -5
```

**Expected:** Non-empty content in the streamed response.

---

## 3. Python Client Smoke Test

**Goal:** Programmatically verify the agent touches Onyx (checks for `onyx` in tool results).

```python
#!/usr/bin/env python3
"""
DeerFlow smoke test — verifies agent calls onyx_search and gets results.
Run from the deer-flow backend directory with the venv active.
"""
import sys
sys.path.insert(0, "packages/harness")

from deerflow.client import DeerFlowClient

client = DeerFlowClient()

print("Starting smoke test...")
tool_calls_seen = []
onyx_results_found = False

for event in client.stream("Search the Onyx knowledge base for Tsallis statistics"):
    if event.type == "messages-tuple":
        msg = event.data
        # Check for tool calls
        if hasattr(msg, "tool_calls"):
            for tc in msg.tool_calls:
                tool_calls_seen.append(tc.get("name", ""))
                print(f"  Tool call: {tc.get('name')}")
        # Check tool results for onyx content
        if hasattr(msg, "content") and isinstance(msg.content, str):
            if "onyx" in msg.content.lower() or "document" in msg.content.lower():
                onyx_results_found = True

print(f"\nTool calls: {tool_calls_seen}")
print(f"Onyx results found: {onyx_results_found}")

assert "onyx_search" in tool_calls_seen, f"FAIL: onyx_search not called. Got: {tool_calls_seen}"
assert onyx_results_found, "FAIL: No Onyx document content in tool results"

print("\nSMOKE TEST PASSED")
```

**Run:**
```bash
cd deployment/deer-flow/backend
../.venv/bin/python /path/to/smoke_test.py
```

---

## 4. MCP Connectivity Check

**Goal:** Verify DeerFlow gateway can reach the Onyx MCP proxy.

```bash
# From inside the gateway container
docker exec deer-flow-gateway node -e "
fetch('http://onyx-mcp-proxy/onyx/sse')
  .then(r => console.log('MCP proxy status:', r.status))
  .catch(e => console.log('MCP proxy error:', e.message))
"
```

**Expected:** `MCP proxy status: 200`

---

## 5. Expected Tool Inventory

After MCP initialization, the gateway should load ~94 tools. Check with:

```bash
docker logs deer-flow-gateway 2>&1 | grep "MCP tools initialized"
# Expected: MCP tools initialized: 94 tool(s) loaded
```

If fewer tools load, check which MCP servers failed:
```bash
docker logs deer-flow-gateway 2>&1 | grep "Failed to load tools"
```

Known non-critical failures: `scite` and `consensus` fail with 401 until OAuth is completed (expected).

---

## Pass Criteria

| Check | Pass |
|---|---|
| UI chat returns Onyx-sourced content | Agent cites document title |
| API thread creation | HTTP 200, valid thread_id |
| Python client `onyx_search` called | Tool name in event stream |
| MCP proxy reachable | HTTP 200 on `/onyx/sse` |
| MCP tool count | >= 90 tools loaded |

---

## Related

- `deployment/deer-flow/README-local-patches.md` — patches required before running
- `deployment/deer-flow/apply_local_patches.sh` — verify patches are applied
- `docs/ops/troubleshooting.md` — failure mode runbook
- `GitHub Issues` — "end-to-end MCP/tool execution still needs verification"
