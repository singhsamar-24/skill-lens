from pydantic import BaseModel, Field
from typing import Literal
from app.models.common import EvidenceItem, Priority
from app.models.codeforces import CodeforcesAnalysis
from app.models.github import GitHubAnalysis
from app.models.leetcode import LeetCodeAnalysis
from app.models.resume import ResumeAnalysis


class CompareRequest(BaseModel):
    github: GitHubAnalysis
    resume: ResumeAnalysis
    leetcode: LeetCodeAnalysis | None = None
    codeforces: CodeforcesAnalysis | None = None
    target_role: str | None = "Software Engineer"


class ComparedSkill(BaseModel):
    name: str
    confidence: float = Field(ge=0, le=1)
    resume_signal: str | None = None
    github_signal: str | None = None
    evidence: list[EvidenceItem | str] = Field(default_factory=list)


class MissingSkill(BaseModel):
    name: str
    priority: Priority
    reason: str
    usage: list[str] = Field(default_factory=list)
    impact: str = ""


class JobRoleMatch(BaseModel):
    role: str
    match: int = Field(ge=0, le=100)
    salary: str
    reason: str
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)


class SkillInsight(BaseModel):
    type: Literal["over_claim", "under_sell", "strength", "gap", "proof"]
    title: str
    detail: str
    severity: Priority


class CompareResponse(BaseModel):
    target_role: str
    verified_skills: list[ComparedSkill] = Field(default_factory=list)
    claimed_unproven_skills: list[ComparedSkill] = Field(default_factory=list)
    github_only_skills: list[ComparedSkill] = Field(default_factory=list)
    missing_skills: list[MissingSkill] = Field(default_factory=list)
    career_matches: list[JobRoleMatch] = Field(default_factory=list)
    evidence_score: int = Field(ge=0, le=100)
    problem_solving_signal: str = "unknown"
    insights: list[SkillInsight] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
