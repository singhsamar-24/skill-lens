from typing import Literal
from pydantic import BaseModel, Field


class LeetCodeAnalyzeRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50, pattern=r"^[A-Za-z0-9_-]+$")


class TopicCount(BaseModel):
    topic: str
    solved: int


class LeetCodeAnalysis(BaseModel):
    username: str
    status: Literal["ok", "unavailable"] = "ok"
    total_solved: int = 0
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0
    ranking: int | None = None
    topics: list[TopicCount] = Field(default_factory=list)
    problem_solving_signal: Literal["strong", "moderate", "emerging", "unknown"] = "unknown"
    warning: str | None = None
