# OpenFang — dezinfo project

Anti-disinformation OSINT platform using Qwen free-tier endpoints.

## Structure

```
openfang-dezinfo/
├── setup.sh                     ← Single-command install & configure
├── config.toml                  ← Copied to ~/.openfang/config.toml
├── agents/
│   ├── watchdog.toml            ← qwen3.5-flash        | feed triage, runs every 15 min
│   ├── inquisitor.toml          ← qwen3.5-122b-a10b    | deep verification & verdicts
│   ├── visual-analyst.toml      ← qwen3-vl-235b-a22b-thinking | memes, screenshots, OCR
│   ├── impact-comms.toml        ← qwen-plus-latest     | drafts debunks & notices (SK+EN)
│   └── archivist.toml           ← qwen2.5-14b-instruct-1m | knowledge graph & archive audit
└── workflows/
    ├── osint-dezinformacia-monitor.json   ← continuous monitoring pipeline
    ├── coordinated-debunk-engine.json     ← deep per-claim investigation
    ├── meme-deepfake-triage.json          ← visual disinformation pipeline
    └── social-impact-accountability.json  ← advertiser/regulator notification pipeline
```

## Quick Start

```bash
export DASHSCOPE_API_KEY="sk-..."       # DashScope key
export BRAVE_API_KEY="BSA..."           # Brave Search API key (recommended)
bash setup.sh
```

## Agent Model Map

| Agent           | Primary Model                  | Fallback          | Role                          |
|-----------------|-------------------------------|-------------------|-------------------------------|
| watchdog        | qwen3.5-flash                 | —                 | High-freq feed triage (15 min)|
| inquisitor      | qwen3.5-122b-a10b             | qwq-plus          | Deep reasoning & verdicts     |
| visual-analyst  | qwen3-vl-235b-a22b-thinking   | qwen-vl-ocr       | Image/video/OCR analysis      |
| impact-comms    | qwen-plus-latest              | —                 | Bilingual SK/EN comms drafts  |
| archivist       | qwen2.5-14b-instruct-1m       | qwen2.5-7b-1m     | KG + 1M-ctx archive audit     |

## Manual Workflow Triggers

```bash
# Trigger full monitoring cycle
openfang workflow run osint-dezinformacia-monitor "monitor"

# Deep-investigate a specific claim
openfang workflow run coordinated-debunk-engine "Claim: ..."

# Analyse a meme or screenshot
openfang workflow run meme-deepfake-triage "https://example.com/image.jpg"

# Prepare accountability communications
openfang workflow run social-impact-accountability "verdict_id:abc123"
```

## Dashboard

```bash
openfang dashboard
# → http://127.0.0.1:4200/
```

## Diagnostics

```bash
openfang doctor
openfang agent list
openfang workflow list
```
