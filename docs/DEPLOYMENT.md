# Deployment Guide

SkillLens is deployed as two services:

- Frontend: Vercel project `skill-lens`
- Backend: Railway or any Python host that can run FastAPI with Uvicorn

## Frontend on Vercel

The Vercel project should use:

```text
Root directory: frontend
Build command: npm run build
Output directory: dist
Framework preset: Vite
```

Required frontend environment variable:

```env
VITE_API_BASE_URL=https://your-backend-production-url
```

Deploy the already-linked project from the repo root:

```powershell
vercel deploy --prod --yes
```

Useful checks:

```powershell
vercel inspect https://your-production-url
vercel logs --environment production --level error --since 1h --no-branch
```

## Backend on Railway

Railway service root should be:

```text
backend
```

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Required environment variables:

```env
GROQ_API_KEY=your_groq_key
FRONTEND_ORIGIN=https://your-vercel-production-domain
```

Recommended environment variables:

```env
GITHUB_TOKEN=your_github_token
DATABASE_URL=postgresql://user:password@host:port/database
```

`DATABASE_URL` enables recruiter candidate persistence and stored evaluations. Without it, recruiter persistence features are limited.

## CORS

Set `FRONTEND_ORIGIN` to the exact deployed frontend origin. For example:

```env
FRONTEND_ORIGIN=https://skill-lens-two.vercel.app
```

For local development:

```env
FRONTEND_ORIGIN=http://localhost:5173
```

## Production Verification

After deploy:

1. Open the frontend production URL.
2. Check that the landing page loads.
3. Confirm the dashboard form accepts a GitHub username and PDF resume.
4. Confirm backend health:

```powershell
Invoke-WebRequest https://your-backend-url/health -UseBasicParsing
```

5. Check Vercel deployment status:

```powershell
vercel inspect https://your-production-url
```

6. Check recent production errors:

```powershell
vercel logs --environment production --level error --since 1h --no-branch
```

## Common Deployment Issues

### Frontend Cannot Reach Backend

Cause:

- `VITE_API_BASE_URL` is missing or points to the wrong backend.

Fix:

- Set the variable in Vercel project settings.
- Redeploy the frontend.

### Backend Rejects Browser Requests

Cause:

- `FRONTEND_ORIGIN` does not match the deployed frontend origin.

Fix:

- Update backend env on Railway.
- Redeploy or restart backend.

### GitHub Rate Limit

Cause:

- `GITHUB_TOKEN` is missing or rate-limited.

Fix:

- Add a GitHub token to backend env.

### Resume Parsing Fails

Cause:

- PDF has no extractable text or `GROQ_API_KEY` is missing for structured parsing.

Fix:

- Use a text-based PDF.
- Configure `GROQ_API_KEY`.

## Release Checklist

- `frontend npm run build` passes.
- `backend pytest` passes or known missing dependency is documented.
- Vercel deployment is `Ready`.
- Backend `/health` returns `status: ok`.
- `VITE_API_BASE_URL` points to the production backend.
- `FRONTEND_ORIGIN` points to the production frontend.
