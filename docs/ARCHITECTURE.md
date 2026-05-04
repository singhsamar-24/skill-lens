# SkillLens Architecture

## Overview

SkillLens is organized as a typed full-stack application. The frontend gathers user input and presents analysis. The backend owns all external API calls, secret handling, normalization, scoring, RAG retrieval, and persistence.

```text
User
  -> React/Vite frontend
  -> FastAPI backend
  -> GitHub / Groq / LeetCode / Codeforces / PostgreSQL
```

The frontend never receives provider secrets. It calls the backend through the typed API client in `frontend/src/lib/api.ts`.

## Backend Modules

- `backend/app/main.py`: FastAPI app setup, CORS, health endpoint, middleware, and router registration.
- `backend/app/api/*`: Thin route handlers for GitHub, resume, compare, roadmap, mentor, recruiter, LeetCode, and Codeforces.
- `backend/app/services/*`: Business logic for external API calls, resume extraction, scoring, roadmap generation, RAG mentor behavior, and recruiter workflows.
- `backend/app/models/*`: Pydantic request and response contracts.
- `backend/app/core/*`: settings, error helpers, rate limiting, normalization, cache, and database setup.
- `backend/app/rag/*`: chunking and retrieval manager for local knowledge sources.
- `backend/app/data/*`: seeded company profiles, job role data, and local RAG Markdown corpora.
- `backend/tests/*`: service and API regression tests.

## Frontend Modules

- `frontend/src/App.tsx`: application route registration.
- `frontend/src/pages/*`: major screens such as Landing, Dashboard, Compare, Roadmap, Mentor, Recruiter, and Insights.
- `frontend/src/components/*`: reusable panels, charts, forms, badges, upload controls, visual scene, and analysis cards.
- `frontend/src/state/analysis-store.tsx`: shared analysis state and orchestration for running GitHub, resume, LeetCode, Codeforces, compare, and roadmap calls.
- `frontend/src/types.ts`: TypeScript interfaces mirroring backend Pydantic contracts.
- `frontend/src/lib/api.ts`: fetch wrapper and endpoint functions.

## Primary User Flow

1. User enters GitHub username, target role, optional LeetCode and Codeforces handles, and uploads a PDF resume.
2. Frontend starts GitHub, resume, and optional coding-platform analysis in parallel.
3. Backend fetches public GitHub repositories, languages, README content, topics, and recent commits.
4. Backend extracts resume text and uses Groq for structured resume skill parsing when configured.
5. Backend compares normalized resume skills against GitHub skills and target-role expectations.
6. Frontend receives `CompareResponse` and renders trust score, distribution, insights, evidence, gaps, and role matches.
7. User can generate a roadmap or ask the mentor chat for RAG-grounded guidance.

## Scoring Model

The backend evidence score is computed in `backend/app/services/compare_service.py`.

Core inputs:

- `verified_skills`: skills found in both resume and GitHub evidence.
- `claimed_unproven_skills`: resume skills without enough GitHub proof.
- `github_only_skills`: credible GitHub skills missing from the resume.
- `missing_skills`: role-relevant skills missing from both sources.
- Optional problem-solving signal from LeetCode and Codeforces.

The dashboard trust card applies a small display calibration per completed comparison so repeated attempts do not feel visually frozen when the backend score lands in the same bucket. The adjustment is bounded and clamped to `0-100`.

## Skill Normalization

Skill aliases are normalized in `backend/app/core/normalization.py`. This avoids treating names like `JS`, `JavaScript`, `React.js`, and `React` as separate signals.

Contract rule:

1. Add or change backend Pydantic models first.
2. Update `frontend/src/types.ts`.
3. Update UI rendering and tests.

## RAG Mentor Design

SkillLens ships with three local Markdown knowledge sources:

- Alumni: mentorship, career experience, interview and portfolio advice.
- Learning: learning paths, project-based preparation, practical skill building.
- Job: hiring expectations, role requirements, market signals.

The mentor service routes queries to the most relevant source or a merged set. Retrieval has a lexical fallback so the app can still answer when optional semantic dependencies are unavailable.

## Recruiter Workflow

The recruiter flow supports bulk resume uploads and role-based ranking.

When `DATABASE_URL` is configured:

- candidates are stored in PostgreSQL,
- evaluations are persisted,
- ranking can be retrieved later.

Without `DATABASE_URL`, core candidate analysis can still run, but durable recruiter storage is unavailable.

## Reliability Choices

- External API calls use backend-owned timeouts and safe degradation.
- Optional LeetCode and Codeforces failures do not block the main comparison.
- GitHub rate-limit metadata is surfaced safely.
- In-memory caching reduces repeated external calls during demos.
- Rate limiting protects expensive resume, roadmap, mentor, and external API routes.
