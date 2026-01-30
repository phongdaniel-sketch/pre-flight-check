# Application Environments

This document serves as a reference for QA and Development teams to access different environments of the Pre-flight Check application.

## 1. Local Development (Localhost)
Used for active development and initial testing by developers.
- **Frontend URL**: [http://localhost:5173](http://localhost:5173)
- **Backend URL**: [http://localhost:8000](http://localhost:8000)
- **Status**: Running locally (requires `npm run dev` and `node api/server.js`).

## 2. Staging Environment (Develop)
Used for QA testing before release. Automatically deployed from the `develop` branch.

> [!NOTE]
> **Vercel Protection Bypass:** Staging environment uses Vercel Deployment Protection. Tests require bypass token in headers.
> - Token is configured in `/QA/run_tests.py`
> - Header: `x-vercel-protection-bypass: preflightcheckqatesting202612345`

- **URL**: [https://pre-flight-check-phong-daniels-projects.vercel.app](https://pre-flight-check-phong-daniels-projects.vercel.app)
- **Branch**: `develop`
- **Status**: ✅ **Active** (All tests passing with bypass token)
- **Last Tested**: 2026-01-27 (3/3 tests passed)

## 3. Production Environment (Main)
The live application for end users. Deployed from the `main` branch.
- **URL**: [https://pre-flight-check-kohl.vercel.app](https://pre-flight-check-kohl.vercel.app)
- **Branch**: `main`
- **Status**: ✅ **Active** (All tests passing)
- **Last Tested**: 2026-01-27 (3/3 tests passed)

---

## Testing Environments

### Run QA Tests

**Production:**
```bash
.venv/bin/python QA/run_tests.py --url https://pre-flight-check-kohl.vercel.app
```

**Staging (with bypass token):**
```bash
.venv/bin/python QA/run_tests.py --url https://pre-flight-check-phong-daniels-projects.vercel.app
```

**Local (Requires server running):**
```bash
# Start backend first: node api/server.js
# Start frontend: cd client && npm run dev
.venv/bin/python QA/run_tests.py --url http://localhost:8000
```

---

## Vercel Deployment Protection

Staging environment has Vercel Deployment Protection enabled. The bypass token is stored in:
- **File**: `/QA/run_tests.py`
- **Constant**: `VERCEL_BYPASS_TOKEN`
- **Current Token**: `preflightcheckqatesting202612345`

To update the token:
1. Go to Vercel Dashboard → Project Settings → Deployment Protection
2. Add/update bypass token (must be 32 alphanumeric characters)
3. Update `VERCEL_BYPASS_TOKEN` in `/QA/run_tests.py`

---
*Note: Staging and Production URLs are managed via Vercel.*

