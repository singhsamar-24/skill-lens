# SkillLens

SkillLens is a full-stack candidate verification platform. It compares skills claimed in a resume with real evidence from GitHub repositories, optional LeetCode and Codeforces signals, role-specific skill expectations, and a local RAG mentor system.

The project is built as a production-style hackathon MVP with a React dashboard, FastAPI backend, recruiter workflows, roadmap generation, and deployment-ready configuration for Vercel plus Railway or another Python host.

## What It Does

- Verifies resume skills against public GitHub repository evidence.
- Extracts resume skills, projects, and confidence signals from uploaded PDF resumes.
- Adds optional competitive programming context from LeetCode and Codeforces.
- Computes a trust score, skill gaps, role matches, and personalized recommendations.
- Generates learning roadmaps for target roles.
- Provides a mentor chat backed by local Alumni, Learning, and Job RAG sources.
- Supports recruiter bulk resume upload, candidate evaluation, ranking, and persistence when PostgreSQL is configured.

## Documentation

- [Architecture](docs/ARCHITECTURE.md): system design, data flow, scoring, RAG, and module responsibilities.
- [API Reference](docs/API_REFERENCE.md): backend endpoints, request bodies, response shapes, and error model.
- [Deployment Guide](docs/DEPLOYMENT.md): Vercel frontend, Railway backend, environment variables, and production checks.
- [Testing Guide](docs/TESTING.md): backend tests, frontend builds, manual checks, and release checklist.
- [Project Report](docs/PROJECT_REPORT.md): problem statement, solution, features, impact, limitations, and future scope.
- [Shared Contracts](shared/contracts.md): contract ownership notes for backend Pydantic models and frontend TypeScript types.

## Tech Stack

- Frontend: React 19, TypeScript, Vite, Tailwind CSS, Framer Motion, lucide-react, React Router.
- Backend: FastAPI, Pydantic, Groq `llama-3.3-70b-versatile`, GitHub REST, LeetCode GraphQL, Codeforces API.
- RAG: local Markdown corpora, lexical fallback retrieval, optional semantic retrieval hooks.
- Persistence: optional PostgreSQL for recruiter candidate and evaluation storage.
- Deployment: Vercel for frontend, Railway or compatible Python host for backend.

## Repository Layout

```text
skill-lens/
  backend/              FastAPI app, services, Pydantic models, tests, data
  frontend/             React/Vite dashboard and product UI
  shared/               Cross-app contract notes
  docs/                 Detailed project documentation
  plan.md               Original MVP implementation plan
  README.md             Project overview and quick start
```

## Local Setup

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Required for LLM-backed features:

```env
GROQ_API_KEY=your_groq_key
```

Recommended:

```env
GITHUB_TOKEN=your_github_token
FRONTEND_ORIGIN=http://localhost:5173
DATABASE_URL=postgresql://user:password@host:port/db
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

For deployed or non-local backend usage, set:

```env
VITE_API_BASE_URL=https://your-backend-url
```

## Validation

```powershell
cd backend
pytest

cd ../frontend
npm run build
```

The frontend build runs TypeScript project references and a production Vite bundle.

## Deployment Summary

- Frontend is deployed from the existing Vercel `skill-lens` project.
- Backend can be deployed on Railway from `/backend`.
- Production frontend must point `VITE_API_BASE_URL` to the backend API.
- Backend CORS must allow the frontend production domain via `FRONTEND_ORIGIN`.

See [Deployment Guide](docs/DEPLOYMENT.md) for exact steps.
