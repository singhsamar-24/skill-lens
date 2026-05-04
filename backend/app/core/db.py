from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.core.settings import Settings


class Base(DeclarativeBase):
    pass


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    github_username: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    resume_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    skills: Mapped[list[CandidateSkill]] = relationship(back_populates="candidate", cascade="all, delete-orphan")
    evaluations: Mapped[list[Evaluation]] = relationship(back_populates="candidate", cascade="all, delete-orphan")


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"
    __table_args__ = (UniqueConstraint("candidate_id", "source", name="uq_candidate_skills_source"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    skills: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    source: Mapped[str] = mapped_column(String(40), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    candidate: Mapped[Candidate] = relationship(back_populates="skills")


class Evaluation(Base):
    __tablename__ = "evaluations"
    __table_args__ = (UniqueConstraint("candidate_id", "target_role", name="uq_candidate_role_evaluation"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    target_role: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    match_score: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    verified_skills: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    missing_skills: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    explanations: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    role_matches: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    candidate: Mapped[Candidate] = relationship(back_populates="evaluations")


class JobRole(Base):
    __tablename__ = "job_roles"

    role: Mapped[str] = mapped_column(String(120), primary_key=True)
    skills: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    salary_range: Mapped[str] = mapped_column(String(80), nullable=False)


def normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        return "postgresql+asyncpg://" + url.removeprefix("postgresql://")
    return url


def create_engine(settings: Settings) -> AsyncEngine | None:
    if not settings.database_url:
        return None
    return create_async_engine(
        normalize_database_url(settings.database_url),
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_pre_ping=True,
    )


def create_session_factory(engine: AsyncEngine | None) -> async_sessionmaker[AsyncSession] | None:
    if not engine:
        return None
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_session(session_factory: async_sessionmaker[AsyncSession]) -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


async def init_db(engine: AsyncEngine | None, session_factory: async_sessionmaker[AsyncSession] | None) -> None:
    if not engine or not session_factory:
        return
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    await seed_job_roles(session_factory)


async def seed_job_roles(session_factory: async_sessionmaker[AsyncSession]) -> None:
    roles = {
        "Backend Engineer": {
            "skills": ["Python", "FastAPI", "REST APIs", "PostgreSQL", "Caching", "System Design", "Testing", "Docker"],
            "salary_range": "10-22 LPA",
        },
        "Frontend Engineer": {
            "skills": ["JavaScript", "TypeScript", "React", "REST APIs", "Testing", "Tailwind CSS"],
            "salary_range": "8-18 LPA",
        },
        "Full Stack Engineer": {
            "skills": ["JavaScript", "TypeScript", "React", "Python", "FastAPI", "REST APIs", "Databases", "Testing"],
            "salary_range": "10-24 LPA",
        },
        "AI Engineer": {
            "skills": ["Python", "LLMs", "RAG", "FastAPI", "Vector Databases", "System Design", "Testing"],
            "salary_range": "12-30 LPA",
        },
        "DevOps Engineer": {
            "skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "System Design", "Testing", "Monitoring"],
            "salary_range": "9-22 LPA",
        },
        "Software Engineer": {
            "skills": ["Python", "JavaScript", "REST APIs", "Data Structures", "Testing", "System Design", "Databases"],
            "salary_range": "8-20 LPA",
        },
        "Data Engineer": {
            "skills": ["Python", "SQL", "Databases", "AWS", "Data Pipelines", "Testing", "System Design"],
            "salary_range": "10-24 LPA",
        },
    }
    async with session_factory() as session:
        existing = set((await session.scalars(select(JobRole.role))).all())
        for role, data in roles.items():
            if role not in existing:
                session.add(JobRole(role=role, skills=data["skills"], salary_range=data["salary_range"]))
        await session.commit()
