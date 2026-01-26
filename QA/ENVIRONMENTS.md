# Application Environments

This document serves as a reference for QA and Development teams to access different environments of the Pre-flight Check application.

## 1. Local Development (Localhost)
Used for active development and initial testing by developers.
- **Frontend URL**: [http://localhost:5173](http://localhost:5173)
- **Backend URL**: [http://localhost:8000](http://localhost:8000)
- **Status**: Running locally (requires `npm run dev` and `node api/server.js`).

## 2. Staging Environment (Develop)
Used for QA testing before release. Automatically deployed from the `develop` branch.
- **Primary URL**: [https://pre-flight-check-git-develop-phong-daniels-projects.vercel.app](https://pre-flight-check-git-develop-phong-daniels-projects.vercel.app)
- **Latest Preview**: [https://pre-flight-check-pymtom89b-phong-daniels-projects.vercel.app](https://pre-flight-check-pymtom89b-phong-daniels-projects.vercel.app) (Note: hash may change per deploy)
- **Branch**: `develop`

## 3. Production Environment (Main)
The live application for end users. Deployed from the `main` branch.
- **URL**: [https://pre-flight-check-kohl.vercel.app](https://pre-flight-check-kohl.vercel.app)
- **Branch**: `main`

---
*Note: Staging and Production URLs are managed via Vercel.*
