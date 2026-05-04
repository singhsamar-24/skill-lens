# SkillLens Project Report

## Problem Statement

Hiring profiles often contain long skill lists, but recruiters and mentors need evidence. A resume may claim React, Python, APIs, testing, or AI experience, yet the proof is scattered across public repositories, coding profiles, and project descriptions.

SkillLens solves this by turning a candidate profile into an evidence-backed skill report.

## Solution

SkillLens combines:

- resume skill extraction,
- GitHub repository evidence,
- optional competitive programming signals,
- target-role expectations,
- RAG-grounded career guidance,
- recruiter ranking workflows.

The result is a dashboard that shows what is verified, what is claimed but unproven, what the candidate is under-selling, and what they should build next.

## Key Features

- Trust score dashboard with attempt-level display calibration.
- GitHub proof extraction from languages, README content, topics, descriptions, and commits.
- Resume PDF parsing and skill classification.
- Target-role gap analysis.
- Roadmap generation with milestones and portfolio project suggestions.
- Mentor chat using local Alumni, Learning, and Job knowledge sources.
- Recruiter bulk upload, evaluation, and ranking.
- Optional PostgreSQL-backed persistence.

## Target Users

- Students preparing for internships or placements.
- Developers improving portfolio credibility.
- Mentors reviewing student readiness.
- Recruiters shortlisting candidates from uploaded resumes.
- Hackathon teams presenting practical AI-assisted career tooling.

## Technical Approach

The backend normalizes all skills before comparison. This prevents alias mismatches such as `JS` versus `JavaScript` or `Postgres` versus `PostgreSQL`.

The trust score rewards:

- skill overlap between resume and GitHub,
- credible repository evidence,
- confidence and breadth,
- role-relevant proof.

It penalizes:

- unsupported resume claims,
- high-priority role gaps.

The mentor system retrieves relevant snippets from local project-curated knowledge packs before generating guidance.

## Impact

SkillLens gives candidates a clearer way to answer:

- Which skills can I actually prove?
- Which resume claims need better evidence?
- Which hidden GitHub strengths should I add to my resume?
- What should I build next for my target role?
- How would a recruiter compare me against a role?

## Limitations

- Public GitHub data can miss private or non-code work.
- Resume extraction depends on readable PDF text.
- LLM parsing requires a valid Groq API key.
- In-memory cache is suitable for MVP and demos, not multi-region persistence.
- Recruiter persistence requires PostgreSQL configuration.

## Future Scope

- OAuth GitHub connection for private repository evidence.
- Better commit and code-level semantic analysis.
- Historical score tracking per candidate.
- More company-specific hiring profiles.
- Exportable PDF reports.
- Team dashboards for colleges, bootcamps, and placement cells.
- Stronger observability and audit logs for production recruiter usage.
