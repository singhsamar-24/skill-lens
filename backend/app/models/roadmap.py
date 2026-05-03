from pydantic import BaseModel, Field
from app.models.common import Priority
from app.models.compare import CompareResponse


class RoadmapRequest(BaseModel):
    comparison: CompareResponse
    target_role: str = "Software Engineer"


class RoadmapSkill(BaseModel):
    skill: str
    priority: Priority
    rationale: str


class RoadmapMilestone(BaseModel):
    week: str
    title: str
    tasks: list[str] = Field(default_factory=list)
    project: str
    outcomes: list[str] = Field(default_factory=list)


class RoadmapResponse(BaseModel):
    target_role: str
    focus_skills: list[RoadmapSkill] = Field(default_factory=list)
    milestones: list[RoadmapMilestone] = Field(default_factory=list)
    portfolio_projects: list[str] = Field(default_factory=list)
    mentor_note: str
