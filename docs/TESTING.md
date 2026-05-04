# Testing Guide

## Backend Tests

Run:

```powershell
cd backend
pytest
```

Coverage areas:

- API route behavior.
- GitHub analyzer edge cases.
- Resume parsing and empty resume handling.
- Compare service scoring and normalization.
- Roadmap service fallbacks.
- RAG retrieval and routing.
- LeetCode and Codeforces degradation.
- Recruiter scoring behavior.

## Frontend Checks

Run:

```powershell
cd frontend
npm run build
```

This validates:

- TypeScript project references.
- Vite production build.
- Import correctness.
- Basic bundle generation.

## Manual End-to-End Flow

1. Start backend on port `8000`.
2. Start frontend on port `5173`.
3. Upload a text-based PDF resume.
4. Enter a public GitHub username.
5. Optionally add LeetCode and Codeforces handles.
6. Run analysis.
7. Confirm dashboard sections populate:
   - trust score,
   - skill distribution,
   - insights,
   - GitHub proofs,
   - resume claims,
   - repository intel,
   - optional coding signals.
8. Generate roadmap and verify milestones render.
9. Ask mentor chat a learning or job-prep question.

## Regression Checklist

Before pushing:

- No unrelated generated files in `git status`.
- `git diff --check` has no whitespace errors.
- Frontend build passes.
- Backend tests pass when Python dependencies are installed.
- API contract changes are reflected in both backend models and frontend types.

## Known Test Notes

- Groq-backed features require `GROQ_API_KEY`.
- GitHub analysis works best with `GITHUB_TOKEN`.
- Recruiter persistence requires `DATABASE_URL`.
- Optional platform APIs can be unavailable; the app should degrade with warnings instead of blocking analysis.
