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


class MarketUserSkill(BaseModel):
    name: str
    weight: float = Field(default=1.0, ge=0, le=1.5)


class MarketRoadmapRequest(BaseModel):
    target_role: str = "Software Engineer"
    user_skills: list[str | MarketUserSkill] = Field(default_factory=list)


class MarketCompanyRoadmap(BaseModel):
    company: str
    fit: int = Field(ge=0, le=100)
    salary: str
    apply_link: str | None = None
    process: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    prep_plan: list[str] = Field(default_factory=list)
    question_themes: list[str] = Field(default_factory=list)


class MarketRoadmapResponse(BaseModel):
    companies: list[MarketCompanyRoadmap] = Field(default_factory=list)
