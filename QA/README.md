# QA Test Suite

This directory contains automated integration tests for the Pre-flight Check API.

## Prerequisites
- Python 3.8+
- `httpx` installed (`pip install httpx`)

## Usage

### 1. Test Localhost
Make sure your local server is running (`.venv/bin/python api/index.py`).
```bash
python QA/run_tests.py
# Or explicitly
python QA/run_tests.py --url http://localhost:8000
```

### 2. Test Production
Run against the deployed Vercel URL.
```bash
python QA/run_tests.py --url https://project-agents-taupe.vercel.app
```

## Structure
- `run_tests.py`: Main test runner. uses `httpx` to make requests and asserts response formats.
