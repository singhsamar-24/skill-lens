from typing import Literal
from pydantic import BaseModel, Field


SkillLevel = Literal["strong", "moderate", "exposure"]
ResumeSkillLevel = Literal["claimed", "project_backed", "weak"]
Priority = Literal["high", "medium", "low"]


class EvidenceItem(BaseModel):
    source: str
    detail: str
    url: str | None = None
    weight: float = Field(default=1.0, ge=0, le=5)


class SkillCredibility(BaseModel):
    score: int = Field(default=0, ge=0, le=100)
    repo_count: int = Field(default=0, ge=0)
    commit_count: int = Field(default=0, ge=0)
    recent_repo_count: int = Field(default=0, ge=0)
    language_share: float = Field(default=0, ge=0, le=1)
    last_seen_at: str | None = None


class SkillEvidence(BaseModel):
    name: str
    normalized: str
    level: SkillLevel
    confidence: float = Field(ge=0, le=1)
    credibility: SkillCredibility = Field(default_factory=SkillCredibility)
    evidence: list[EvidenceItem] = Field(default_factory=list)


class ResumeSkill(BaseModel):
    name: str
    normalized: str
    classification: ResumeSkillLevel
    confidence: float = Field(ge=0, le=1)
    evidence: list[str] = Field(default_factory=list)


class WarningMessage(BaseModel):
    code: str
    message: str
