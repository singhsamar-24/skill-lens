from typing import Literal
from pydantic import BaseModel, Field


RagSource = Literal["alumni", "learning", "job"]


class MentorChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    sources: Literal["auto"] | list[RagSource] = "auto"
    profile_context: dict | None = None


class RetrievedSnippet(BaseModel):
    source: RagSource
    source_label: str
    title: str
    text: str
    score: float
    chunk_id: str
    metadata: dict = Field(default_factory=dict)


class MentorChatResponse(BaseModel):
    routed_sources: list[RagSource]
    route_reason: str = ""
    answer: str
    citations: list[str] = Field(default_factory=list)
    snippets: list[RetrievedSnippet] = Field(default_factory=list)
