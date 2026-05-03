from pydantic import BaseModel, Field
from app.models.common import ResumeSkill, WarningMessage


class ResumeProject(BaseModel):
    name: str
    description: str
    skills: list[str] = Field(default_factory=list)


class ResumeAnalysis(BaseModel):
    file_name: str
    text_preview: str
    skills: list[ResumeSkill] = Field(default_factory=list)
    projects: list[ResumeProject] = Field(default_factory=list)
    warnings: list[WarningMessage] = Field(default_factory=list)
