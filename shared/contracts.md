# SkillLens Shared Contracts

The source of truth for runtime contracts is the backend Pydantic models in `backend/app/models`.

Frontend TypeScript interfaces in `frontend/src/types.ts` mirror those models for a typed MVP flow:

- `GitHubAnalysis`
- `ResumeAnalysis`
- `LeetCodeAnalysis`
- `CodeforcesAnalysis`
- `CompareResponse`
- `RoadmapResponse`
- `MentorChatResponse`

Contract changes should be made in backend models first, then reflected in frontend types and API rendering components.
