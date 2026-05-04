from pydantic import BaseModel, Field

from app.models.common import Priority, ResumeSkill


class RecruiterCandidateSummary(BaseModel):
    id: int
    name: str
    email: str | None = None
    github_username: str | None = None
    skills: list[ResumeSkill] = Field(default_factory=list)


class RecruiterUploadResponse(BaseModel):
    uploaded: int
    candidates: list[RecruiterCandidateSummary] = Field(default_factory=list)


class RecruiterEvaluateRequest(BaseModel):
    target_role: str = "Software Engineer"


class RecruiterEvaluationResult(BaseModel):
    candidate_id: int
    name: str
    email: str | None = None
    github_username: str | None = None
    target_role: str
    match_score: int
    verified_skills: list[dict] = Field(default_factory=list)
    missing_skills: list[dict] = Field(default_factory=list)
    explanations: dict = Field(default_factory=dict)
    role_matches: list[dict] = Field(default_factory=list)


class RecruiterEvaluateResponse(BaseModel):
    target_role: str
    evaluated: int
    results: list[RecruiterEvaluationResult] = Field(default_factory=list)


class RecruiterRankItem(BaseModel):
    rank: int
    candidate_id: int
    name: str
    email: str | None = None
    github_username: str | None = None
    target_role: str
    match_score: int
    top_verified_skills: list[str] = Field(default_factory=list)
    top_missing_skills: list[str] = Field(default_factory=list)
    recommendation: Priority
    explanations: dict = Field(default_factory=dict)


class RecruiterRankResponse(BaseModel):
    target_role: str | None = None
    candidates: list[RecruiterRankItem] = Field(default_factory=list)
