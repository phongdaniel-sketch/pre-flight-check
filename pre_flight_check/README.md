# Pre-flight Check Tool 🚀

A predictive scoring tool for TikTok Ads campaigns. It analyzes Safety compliance, Financial Benchmarks, and Creative Quality (using AI) to give a "Pre-flight" rating before you spend budget.

## Features
- **Predictive Scoring:** Combined DNA Score (Creative) + Benchmark Score (Finance).
- **Traffic Light System:** Green/Yellow/Red indicators.
- **Benchmarks:** Built-in industry CPA benchmarks for 2025.
- **Integration:** Connects with **n8n** for Policy Checking & AI Video Analysis.
- **Premium UI:** Dark-mode dashboard built with Tailwind CSS.

## Tech Stack
- **Backend:** Python FastAPI
- **Frontend:** Vanilla JS + Tailwind CSS (Served via FastAPI)
- **Database:** None (Stateless MVP)

## Quick Start

### 1. Requirements
- Python 3.10+
- (Optional) n8n Webhook URL

### 2. Setup
```bash
# Activate Environment
source .venv/bin/activate

# Install Dependencies
pip install -r "Pre-flight check/backend/requirements.txt"
```

### 3. Run
```bash
python "Pre-flight check/backend/main.py"
```
server will start at: `http://localhost:8000`

## Documentation
- **API Specs:** See `Pre-flight check/backend/models.py`
- **Testing:** Run `python "Pre-flight check/backend/tests/test_api.py"`
- **Architecture:** See `implementation_plan.md` in artifacts.

## Deployment Note
To fully utilize the n8n integration (which downloads the video), you must deploy this tool to a public server or use `ngrok` to expose your localhost.
