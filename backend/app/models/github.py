from pydantic import BaseModel, Field
from app.models.common import SkillEvidence, WarningMessage


class GitHubAnalyzeRequest(BaseModel):
    username: str = Field(min_length=1, max_length=39, pattern=r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")


class CommitEvidence(BaseModel):
    message: str
    url: str
    date: str | None = None


class RepositoryEvidence(BaseModel):
    name: str
    full_name: str
    url: str
    description: str | None = None
    stars: int = 0
    forks: int = 0
    pushed_at: str | None = None
    languages: dict[str, int] = Field(default_factory=dict)
    topics: list[str] = Field(default_factory=list)
    readme_excerpt: str | None = None
    commits: list[CommitEvidence] = Field(default_factory=list)


class RateLimitInfo(BaseModel):
    remaining: int | None = None
    reset_epoch: int | None = None
    resource: str | None = None


class GitHubAnalysis(BaseModel):
    username: str
    profile_url: str
    avatar_url: str | None = None
    public_repos: int = 0
    analyzed_repos: list[RepositoryEvidence] = Field(default_factory=list)
    language_totals: dict[str, int] = Field(default_factory=dict)
    skills: list[SkillEvidence] = Field(default_factory=list)
    warnings: list[WarningMessage] = Field(default_factory=list)
    rate_limit: RateLimitInfo | None = None
