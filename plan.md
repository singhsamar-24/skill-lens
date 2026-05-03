# SkillLens Production MVP Plan

## Summary

SkillLens is a full-stack hackathon MVP that validates a candidate's claimed skills against real-world evidence from GitHub, resume content, optional LeetCode problem-solving data, and a multi-source RAG mentor system.

The repository is organized as:

```text
/frontend  React 19 + TypeScript + Vite + Tailwind CSS + Framer Motion
/backend   FastAPI + async services + Groq + GitHub REST + FAISS RAG
/shared    Optional shared contracts and project notes
```

The backend owns all external API credentials. The frontend never receives secrets and communicates only with the FastAPI API.

## System Architecture

### Backend

- `app/main.py`: FastAPI app factory, CORS, rate-limit middleware, health endpoint, routers.
- `app/api/*`: Thin endpoint modules for GitHub, resume, LeetCode, compare, roadmap, mentor.
- `app/services/*`: GitHub extraction, Groq LLM, resume parsing, comparison, roadmap, LeetCode, caching.
- `app/rag/*`: Document chunking, FAISS vector indexes, query router, retrieval, mentor response generation.
- `app/models/*`: Pydantic request/response contracts.
- `app/core/*`: Settings, errors, rate limiting, utility helpers.
- `app/data/rag/*`: Transparent seeded Markdown knowledge packs for alumni, learning, and job/skill RAG.

### Frontend

- `src/pages/*`: Landing, dashboard, compare, roadmap, mentor, insights.
- `src/components/*`: App shell, analysis form, upload dropzone, skill badges, evidence panels, charts, skeleton states, mentor chat.
- `src/lib/api.ts`: Typed API client.
- `src/types.ts`: Frontend-aligned API contracts.
- `src/state/analysis-store.tsx`: Shared analysis state across pages.

## API Contracts

### `GET /health`

Returns safe service readiness flags:

```json
{
  "status": "ok",
  "rag_ready": true,
  "github_token_configured": true,
  "groq_configured": true,
  "cache_items": 12
}
```

### `POST /api/github/analyze`

Request:

```json
{ "username": "octocat" }
```

Response: `GitHubAnalysis` with profile, repositories, language distribution, evidence-backed skills, warnings, and rate-limit metadata.

### `POST /api/resume/analyze`

Multipart PDF upload under `file`. Response: `ResumeAnalysis` with extracted skills classified as `claimed`, `project_backed`, or `weak`.

### `POST /api/leetcode/analyze`

Request:

```json
{ "username": "leetcode_user" }
```

Response: `LeetCodeAnalysis`, or `status: "unavailable"` with warning when the public GraphQL endpoint cannot be reached.

### `POST /api/compare`

Request:

```json
{
  "github": {},
  "resume": {},
  "leetcode": {},
  "target_role": "Frontend Engineer"
}
```

Response includes verified skills, claimed-but-unproven skills, GitHub-only skills, missing role skills, evidence score, problem-solving signal, and recommendations.

### `POST /api/roadmap`

Uses comparison output and target role to return prioritized missing skills, weekly milestones, and project suggestions generated with Groq.

### `POST /api/mentor/chat`

Request:

```json
{
  "message": "How should I learn backend testing?",
  "sources": "auto",
  "profile_context": {}
}
```

Response includes routed source, answer, citations, and retrieved snippets.

## Data Flow

1. User enters GitHub username, optional LeetCode username, target role, and uploads a PDF resume.
2. Frontend progressively calls backend endpoints and shows skeleton states per section.
3. GitHub service fetches public profile, top recent non-fork repositories, languages, README, and latest commits capped at 30 total.
4. Resume service extracts PDF text and asks Groq `llama-3.3-70b-versatile` for structured JSON skill evidence.
5. LeetCode service performs best-effort server-side GraphQL lookup and degrades safely.
6. Compare service normalizes skill aliases, matches resume claims to GitHub evidence, computes scores, and infers gaps for the target role.
7. Roadmap service sends comparison plus RAG context to Groq for a structured learning plan.
8. Mentor chat routes each query to Alumni, Learning, Job, or merged RAG indexes, then passes retrieved context to Groq.

## GitHub Analyzer

- Use GitHub REST with token from `GITHUB_TOKEN` when available.
- Fetch public repositories sorted by recent push.
- Select up to 12 non-fork repos using recency, stars, and language signal.
- Fetch languages, README, and commits with a global latest-commit cap of 30.
- Derive skill evidence from language bytes, README keywords, repo topics, repo names, descriptions, and commit messages.
- Classify:
  - `strong`: repeated evidence across repos or high language share with recent commits.
  - `moderate`: meaningful repo evidence but less breadth or recency.
  - `exposure`: single weak signal or small language/keyword mention.

## Resume LLM Parsing

- Accept PDF only, with a fixed size limit.
- Extract text with `pypdf`.
- Reject empty or unreadable resumes with stable error code `resume_empty`.
- Use Groq Chat Completions with strict JSON instructions.
- Validate the response with Pydantic.
- Retry once with validation feedback if Groq returns malformed JSON.

## Compare Engine

- Normalize common aliases such as JS/JavaScript, TS/TypeScript, React.js/React, Node/Node.js, PostgreSQL/Postgres.
- `verified`: resume skill plus GitHub evidence above threshold.
- `claimed_unproven`: resume skill without enough GitHub evidence.
- `github_only`: GitHub evidence not present in resume.
- `missing`: target-role skills absent from both GitHub and resume.
- LeetCode contributes to problem-solving signal, not direct skill verification.

## Gap Analysis And Roadmap

- Generate missing skills with priority and rationale.
- Use target role defaults when no role is provided.
- Pass comparison output plus Learning and Job RAG snippets into Groq.
- Return machine-validated milestones with week labels, tasks, project suggestions, and measurable outcomes.

## Multi-RAG Design

- Three seeded local corpora:
  - Alumni Knowledge: experience, career advice, interview stories, mentorship guidance.
  - Learning Knowledge: roadmaps, tutorials, project-based learning paths.
  - Job/Skill Knowledge: role expectations, hiring signals, required skills.
- Chunk Markdown into 700-900 character chunks with overlap.
- Embed with `sentence-transformers/all-MiniLM-L6-v2`.
- Store each corpus in an in-memory FAISS index.
- Provide deterministic fallback lexical retrieval if FAISS or model loading is unavailable in a local environment.
- Query routing:
  - `how`, `learn`, `roadmap`, `tutorial`, `build`, `study` -> Learning RAG.
  - `job`, `required`, `role`, `hiring`, `expectations` -> Job RAG.
  - Mixed intent or explicit multi-source request -> merged retrieval.
  - Otherwise -> Alumni RAG.

## Caching Strategy

- In-memory TTL cache:
  - GitHub analysis: 30 minutes.
  - LeetCode analysis: 30 minutes.
  - Resume parse by SHA-256 file hash: 15 minutes.
  - RAG query embedding/retrieval: short TTL.
- Cache values are server-local and safe for MVP deployment on single-instance Render/Railway.

## Rate Limit Strategy

- Per-IP token bucket middleware.
- Endpoint-aware costs:
  - GitHub and LeetCode: moderate.
  - Resume, roadmap, mentor LLM: high.
  - Health: low.
- External API calls use timeouts, bounded concurrency, and exponential backoff.
- GitHub rate-limit headers are surfaced as safe metadata and 403/429 responses become `github_rate_limited`.

## UI/UX Decisions

- Pure white background, black/neutral typography, minimal blue/emerald/amber accents.
- Startup-grade dashboard with clear hierarchy, high scanability, progressive rendering, and no raw JSON.
- Smooth Framer Motion transitions on page entry, cards, and progressive analysis states.
- Responsive layout with desktop side navigation and mobile top navigation.
- Use skeletons and optimistic section shells so users see progress immediately.
- Use accessible buttons, inputs, focus rings, reduced clutter, and clear warning states.

## Folder Structure

```text
SkillLens/
  plan.md
  README.md
  shared/
    contracts.md
  backend/
    requirements.txt
    pytest.ini
    .env.example
    app/
      main.py
      api/
      core/
      models/
      rag/
      services/
      data/rag/
    tests/
  frontend/
    package.json
    tsconfig.json
    vite.config.ts
    tailwind.config.ts
    postcss.config.js
    index.html
    vercel.json
    .env.example
    src/
      main.tsx
      App.tsx
      index.css
      components/
      lib/
      pages/
      state/
      types.ts
```

## Verification Plan

- Backend pytest coverage:
  - GitHub no repos.
  - GitHub rate limit.
  - Empty resume.
  - Invalid Groq JSON retry.
  - LeetCode unavailable degradation.
  - Compare alias normalization.
  - RAG routing and retrieval.
- API simulation with FastAPI test client.
- Frontend typecheck and production build.
- Browser verification against local dev server across desktop and mobile viewports.

## Deployment

- Frontend: Vercel, configured with `VITE_API_BASE_URL`.
- Backend: Render/Railway with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- Required backend env: `GROQ_API_KEY`.
- Recommended backend env: `GITHUB_TOKEN`, `FRONTEND_ORIGIN`.
