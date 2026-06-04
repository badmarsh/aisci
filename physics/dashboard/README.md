# Physics Pipeline Dashboard

Simple web dashboard for monitoring physics pipeline status, recent runs, agenda, and evidence ledger.

---

## Features

- **Status Overview** - Current pipeline state (blocked/ready/complete)
- **Recent Runs** - Last 10 runs with model comparison
- **Next Actions** - Agenda from `next-actions.md`
- **Evidence Ledger** - Summary of verified/pending/blocked claims
- **Available Models** - List of physics models

---

## Installation

### Requirements

```bash
pip install flask flask-cors
```

Or use the physics environment:

```bash
source physics/physics_env/bin/activate
pip install flask flask-cors
```

---

## Usage

### Start Dashboard

```bash
cd physics/dashboard
python3 backend.py
```

### Access Dashboard

Open browser to: **http://localhost:5050**

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Dashboard HTML |
| `GET /api/status` | Current pipeline status |
| `GET /api/runs` | Recent run history (last 10) |
| `GET /api/agenda` | Next actions from `next-actions.md` |
| `GET /api/evidence` | Evidence ledger summary |
| `GET /api/models` | Available physics models |
| `GET /api/health` | Health check |

---

## Data Sources

### Status
- Checks for `fit_input.csv` in run directories
- Counts total runs
- Determines overall status

### Recent Runs
- Parses `research/robert/runs/*/`
- Reads `fit_quality.csv` for model metrics
- Reads `model_comparison.csv` for best model

### Agenda
- Parses `research/robert/next-actions.md`
- Extracts checkbox items with status
- Identifies task IDs (e.g., [B-01])

### Evidence Ledger
- Parses `research/robert/evidence-ledger.md`
- Counts claims by status (✅/🟡/🔴)
- Extracts individual claims

---

## Architecture

```
physics/dashboard/
├── backend.py          # Flask server
├── collector.py        # Data collection logic
├── index.html          # Dashboard HTML
├── static/
│   ├── style.css       # Styling
│   └── app.js          # Frontend JavaScript
└── README.md           # This file
```

---

## Development

### Test Data Collector

```bash
python3 collector.py
```

### Test API Endpoints

```bash
# Status
curl http://localhost:5050/api/status

# Runs
curl http://localhost:5050/api/runs

# Agenda
curl http://localhost:5050/api/agenda

# Evidence
curl http://localhost:5050/api/evidence

# Models
curl http://localhost:5050/api/models
```

---

## Customization

### Change Port

Edit `backend.py`:

```python
app.run(host="0.0.0.0", port=5050, debug=True)
```

### Add New Endpoint

1. Add function to `collector.py`
2. Add route to `backend.py`
3. Update `app.js` to fetch and display

### Modify Styling

Edit `static/style.css` to customize colors, layout, etc.

---

## Troubleshooting

### Issue: Dashboard shows "Loading..."

**Cause:** Backend not running or API errors

**Solution:**
```bash
# Check backend logs
python3 backend.py

# Check API health
curl http://localhost:5050/api/health
```

---

### Issue: No runs displayed

**Cause:** No run directories in `research/robert/runs/`

**Solution:**
```bash
# Check for runs
ls research/robert/runs/

# Run fitting pipeline to generate data
cd physics
python src/fitting_pipeline.py
```

---

### Issue: Agenda/Evidence empty

**Cause:** Files don't exist or are empty

**Solution:**
```bash
# Check files exist
ls research/robert/next-actions.md
ls research/robert/evidence-ledger.md

# View contents
cat research/robert/next-actions.md
```

---

## Future Enhancements

- [ ] Real-time updates via WebSocket
- [ ] Interactive plots with Chart.js
- [ ] Parameter evolution charts
- [ ] Chi²/ndf trends across multiplicity
- [ ] Model comparison visualizations
- [ ] Export data as JSON/CSV
- [ ] Filter runs by date/model
- [ ] Search evidence ledger

---

## References

- [Physics Pipeline Workflow](../../docs/workflows/physics-pipeline-workflow.md)
- [Evidence Ledger](../../research/robert/evidence-ledger.md)
- [Next Actions](../../research/robert/next-actions.md)

---

**Last Updated:** 2026-05-31  
**Maintainer:** Platform Operations
