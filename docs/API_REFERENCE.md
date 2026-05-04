# SkillLens API Reference

Base URL in local development: `http://localhost:8000`

The frontend reads the backend URL from `VITE_API_BASE_URL`. In Vite dev mode, it defaults to `http://localhost:8000`.

## Error Format

Most API errors use a stable detail object:

```json
{
  "detail": {
    "code": "resume_empty",
    "message": "Could not extract readable text from this PDF."
  }
}
```

Frontend callers show `detail.message` when available.

## Health

### `GET /health`

Returns service readiness and safe configuration flags.

Example response:

```json
{
  "status": "ok",
  "rag_ready": true,
  "groq_configured": true,
  "rag_backend": "lexical"
}
```

## GitHub

### `POST /api/github/analyze`

Analyzes public GitHub evidence for a username.

Request:

```json
{
  "username": "octocat"
}
```

Response includes:

- profile URL and avatar,
- repository evidence,
- language totals,
- detected skills,
- warnings,
- rate-limit metadata when available.

Important behavior:

- Uses `GITHUB_TOKEN` when configured.
- Degrades with helpful warnings when public data is missing.
- Avoids exposing tokens or raw provider internals.

## Resume

### `POST /api/resume/analyze`

Accepts a multipart PDF upload.

Form field:

```text
file=<resume.pdf>
```

Response includes:

- file name,
- text preview,
- extracted skills,
- project summaries,
- warnings.

Skill classifications:

- `project_backed`: resume evidence mentions project or applied usage.
- `claimed`: listed skill with some confidence.
- `weak`: low-confidence mention.

## LeetCode

### `POST /api/leetcode/analyze`

Request:

```json
{
  "username": "leetcode_user"
}
```

Response includes solved counts, difficulty split, topic coverage, and `problem_solving_signal`.

If the public endpoint is unavailable, the API returns `status: "unavailable"` with a warning instead of breaking the whole analysis.

## Codeforces

### `POST /api/codeforces/analyze`

Request:

```json
{
  "username": "tourist"
}
```

Response includes rating, rank, contests, solved count, accepted tags, and `problem_solving_signal`.

## Compare

### `POST /api/compare`

Compares GitHub, resume, optional coding-platform signals, and target-role expectations.

Request:

```json
{
  "github": {},
  "resume": {},
  "leetcode": null,
  "codeforces": null,
  "target_role": "Frontend Engineer"
}
```

Response fields:

- `verified_skills`
- `claimed_unproven_skills`
- `github_only_skills`
- `missing_skills`
- `career_matches`
- `evidence_score`
- `problem_solving_signal`
- `insights`
- `recommendations`

## Roadmap

### `POST /api/roadmap`

Generates a target-role learning roadmap from comparison results.

Request:

```json
{
  "comparison": {},
  "target_role": "Backend Engineer"
}
```

Response includes focus skills, weekly milestones, portfolio projects, and mentor note.

### `POST /api/roadmap/market`

Returns India-focused company fit and preparation guidance.

Request:

```json
{
  "target_role": "AI Engineer",
  "user_skills": [
    "Python",
    { "name": "RAG", "weight": 0.8 }
  ]
}
```

## Mentor

### `POST /api/mentor/chat`

Runs a RAG-grounded mentor answer.

Request:

```json
{
  "message": "How should I improve backend evidence?",
  "sources": "auto",
  "profile_context": {
    "targetRole": "Backend Engineer",
    "evidenceScore": 62
  }
}
```

Response includes routed sources, answer, citations, and retrieved snippets.

## Recruiter

### `POST /api/recruiter/upload`

Uploads multiple PDF resumes for recruiter review.

Form field:

```text
files=<resume1.pdf>
files=<resume2.pdf>
```

### `POST /api/recruiter/evaluate`

Evaluates uploaded candidates against a target role.

Request:

```json
{
  "target_role": "Software Engineer"
}
```

### `GET /api/recruiter/rank?target_role=Software%20Engineer`

Returns ranked candidates for the selected role.

Requires `DATABASE_URL` for durable recruiter persistence.
