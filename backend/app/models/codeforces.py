from typing import Literal

from pydantic import BaseModel, Field


class CodeforcesAnalyzeRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")


class CodeforcesTopicCount(BaseModel):
    topic: str
    solved: int


class CodeforcesAnalysis(BaseModel):
    username: str
    status: Literal["ok", "unavailable"] = "ok"
    handle: str | None = None
    rank: str | None = None
    rating: int | None = None
    max_rank: str | None = None
    max_rating: int | None = None
    contribution: int | None = None
    friend_of_count: int | None = None
    contests: int = 0
    solved_count: int = 0
    attempted_count: int = 0
    accepted_submissions: int = 0
    topics: list[CodeforcesTopicCount] = Field(default_factory=list)
    problem_solving_signal: Literal["strong", "moderate", "emerging", "unknown"] = "unknown"
    warning: str | None = None
