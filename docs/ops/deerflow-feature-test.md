# DeerFlow Comprehensive Feature Test Prompt

**Purpose:** Test all major DeerFlow capabilities in a single research task

---

## The Prompt

```
I need you to conduct a comprehensive test of your capabilities by completing this multi-step research task:

TASK: "Analyze the current state of the AiSci physics validation project and create a status report"

Please complete ALL of the following steps in order:

1. KNOWLEDGE RETRIEVAL (Onyx MCP):
   - Query Onyx for: "What is the current status of claim O-03 in the evidence ledger?"
   - Query Onyx for: "What are the top 3 blockers in the platform backlog?"
   - Summarize what you found

2. FILE SYSTEM READ (Mounted Disk):
   - Read the file: /workspace/aisci/research/robert/evidence-ledger.md
   - Count how many claims have status "Confirmed"
   - List the claim IDs

3. WEB SEARCH (Parallel Search):
   - Search for: "Tsallis distribution heavy ion collisions 2024"
   - Find the top 3 most recent papers
   - Extract: title, authors, arXiv ID for each

4. LITERATURE VALIDATION (Scite/Consensus MCP):
   - For the paper "Khuntia 2019" (arXiv:1808.02383)
   - Check Scite: How many citations does it have?
   - Check Consensus: What is the consensus rating?

5. DATA ANALYSIS (Python/Bash):
   - List all files in: /workspace/aisci/physics/src/
   - Count how many Python files exist
   - Show the file sizes

6. FILE SYSTEM WRITE (Mounted Disk):
   - Create a new file: /workspace/aisci/test-report-$(date +%Y%m%d).md
   - Write a summary report containing:
     * Evidence ledger status (from step 1-2)
     * Recent literature findings (from step 3-4)
     * Codebase statistics (from step 5)
     * Timestamp of this test

7. VERIFICATION:
   - Read back the file you just created
   - Confirm it contains all required sections

8. FINAL SUMMARY:
   - Create a bullet-point list of which capabilities worked
   - Flag any capabilities that failed
   - Suggest fixes for any failures

IMPORTANT:
- Use Tree-of-Thoughts planning to organize your approach
- Use parallel search when querying multiple sources
- Use fact-checking to validate any numerical claims
- Document each step clearly in your response
```

---

## Expected Capabilities Tested

| Capability | Test Step | Success Criteria |
|------------|-----------|------------------|
| **Onyx MCP** | Step 1 | Returns evidence ledger status |
| **File Read** | Step 2 | Reads evidence-ledger.md, counts claims |
| **Parallel Search** | Step 3 | Finds 3 papers with metadata |
| **Scite MCP** | Step 4 | Returns citation count |
| **Consensus MCP** | Step 4 | Returns consensus rating |
| **Bash Execution** | Step 5 | Lists files, counts, shows sizes |
| **File Write** | Step 6 | Creates new markdown file |
| **File Verification** | Step 7 | Reads back created file |
| **ToT Planning** | All | Shows planning structure |
| **Fact Checking** | Step 8 | Validates claims made |

---

## How to Run

### Option 1: DeerFlow UI
1. Open http://localhost:2026
2. Create new research task
3. Select model: **Claude Opus 4.7 (FreeModel)**
4. Paste the prompt above
5. Click "Start"
6. Monitor progress in real-time

### Option 2: DeerFlow API (Programmatic)
```bash
# Create task
curl -X POST http://localhost:2026/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "<paste prompt here>",
    "model": "claude-freemodel",
    "config": {
      "use_tot": true,
      "use_parallel_search": true,
      "use_fact_checker": true
    }
  }'

# Get task ID from response, then poll status
curl http://localhost:2026/api/tasks/<task-id>
```

---

## Expected Output Structure

```markdown
# AiSci Project Status Report
Generated: 2026-05-31

## 1. Evidence Ledger Status
- Total claims: 18
- Confirmed: 3
- Sanity checked: 8
- Blocked: 2
- Open: 5

Current O-03 status: [from Onyx query]

## 2. Platform Blockers
Top 3 from platform backlog:
1. [Blocker 1]
2. [Blocker 2]
3. [Blocker 3]

## 3. Recent Literature (2024)
1. **Title**: [Paper 1]
   - Authors: [Authors]
   - arXiv: [ID]

2. **Title**: [Paper 2]
   - Authors: [Authors]
   - arXiv: [ID]

3. **Title**: [Paper 3]
   - Authors: [Authors]
   - arXiv: [ID]

## 4. Literature Validation
Khuntia 2019 (arXiv:1808.02383):
- Scite citations: [N]
- Consensus rating: [rating]

## 5. Codebase Statistics
Physics source files:
- Total Python files: [N]
- Total size: [X MB]
- Key files:
  * fitting_pipeline.py ([size])
  * data_loader.py ([size])
  * [etc.]

## 6. Test Execution Summary
✅ Capabilities Working:
- [list]

❌ Capabilities Failed:
- [list with error messages]

🔧 Suggested Fixes:
- [recommendations]
```

---

## Troubleshooting

### If Onyx MCP Fails
**Error**: "MCP tools: 0" or "Cannot connect to Onyx"

**Fix**:
```bash
# Check MCP proxy is running
docker ps | grep onyx-mcp-proxy

# Check DeerFlow can reach it
docker exec deer-flow-gateway curl -s http://onyx-mcp-proxy:80/health

# Check MCP config
docker exec deer-flow-gateway cat /app/backend/extensions_config.json | grep onyx
```

### If Scite/Consensus MCP Fails
**Error**: "401 Unauthorized"

**Fix**: OAuth tokens not set. See `Multica Issues` for the Scite/Consensus OAuth task.

### If File Write Fails
**Error**: "Permission denied" or "Read-only file system"

**Fix**: Check sandbox mount in `config.yaml`:
```yaml
sandbox:
  provider: aio
  mounts:
    - host: /home/ubuntu/aisci
      container: /workspace/aisci
      mode: rw  # Must be 'rw' not 'ro'
```

### If Recursion Limit Hit Again
**Error**: "Recursion limit of 200 reached"

**Fix**: Increase further in `config.yaml`:
```yaml
langgraph:
  recursion_limit: 500
```

---

## Verification Checklist

After the task completes, verify:

- [ ] File created: `/home/ubuntu/aisci/test-report-YYYYMMDD.md`
- [ ] File contains all 6 sections
- [ ] Onyx queries returned real data (not "I cannot access")
- [ ] Web search found 3 papers with arXiv IDs
- [ ] Scite/Consensus returned numbers (or documented OAuth failure)
- [ ] File listing shows actual Python files from physics/src/
- [ ] No "I cannot" or "I don't have access" statements (unless MCP is broken)

---

## Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Completion Rate** | 100% | All 8 steps completed |
| **MCP Success** | 3/3 | Onyx, Scite, Consensus all work |
| **File Operations** | 2/2 | Read + Write both work |
| **Search Quality** | 3 papers | All have arXiv IDs |
| **Execution Time** | < 5 min | From start to file creation |
| **Error Rate** | 0% | No unhandled exceptions |

---

## Alternative: Minimal Test (Quick Validation)

If you just want to verify the model is working, use this shorter prompt:

```
Quick test: 
1. Query Onyx for "What is O-03?"
2. List files in /workspace/aisci/physics/src/
3. Create /workspace/aisci/test.txt with content "DeerFlow test successful"
4. Read it back and confirm
```

Expected time: < 1 minute

---

## Notes

- This test is designed to be **non-destructive** (only creates one test file)
- The test file can be safely deleted after verification
- If any step fails, the agent should continue and document the failure
- The final summary is the most important output (shows what works vs what's broken)
