from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from typing import Any

from fastapi import UploadFile
from sqlalchemy import desc, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from app.core.db import Candidate, CandidateSkill, Evaluation
from app.core.errors import bad_request, unavailable
from app.models.compare import CompareRequest, CompareResponse
from app.models.github import GitHubAnalysis
from app.models.recruiter import (
    RecruiterCandidateSummary,
    RecruiterEvaluateResponse,
    RecruiterEvaluationResult,
    RecruiterRankItem,
    RecruiterRankResponse,
    RecruiterUploadResponse,
)
from app.models.resume import ResumeAnalysis
from app.services.compare_service import CompareService
from app.services.github_service import GitHubService
from app.services.resume_service import ResumeService


@dataclass
class UploadedCandidate:
    candidate: Candidate
    resume: ResumeAnalysis


class RecruiterService:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession] | None,
        resume_service: ResumeService,
        compare_service: CompareService,
        github_service: GitHubService,
    ) -> None:
        self.session_factory = session_factory
        self.resume_service = resume_service
        self.compare_service = compare_service
        self.github_service = github_service
        self._github_semaphore = asyncio.Semaphore(3)
        self._evaluation_semaphore = asyncio.Semaphore(3)

    def _require_db(self) -> async_sessionmaker[AsyncSession]:
        if not self.session_factory:
            raise unavailable("database_unavailable", "DATABASE_URL is not configured, so recruiter persistence is unavailable.")
        return self.session_factory

    async def upload_resumes(self, files: list[UploadFile]) -> RecruiterUploadResponse:
        if not files:
            raise bad_request("recruiter_no_files", "Upload at least one resume PDF.")

        session_factory = self._require_db()
        uploaded: list[UploadedCandidate] = []
        async with session_factory() as session:
            for file in files:
                filename = file.filename or "resume.pdf"
                content = await file.read()
                analysis, resume_text = await self.resume_service.analyze_pdf_bytes(filename, content)
                candidate = Candidate(
                    name=self._extract_name(resume_text, filename),
                    email=self._extract_email(resume_text),
                    github_username=self._extract_github_username(resume_text),
                    resume_text=resume_text,
                )
                session.add(candidate)
                await session.flush()
                session.add(
                    CandidateSkill(
                        candidate_id=candidate.id,
                        source="resume",
                        skills=[skill.model_dump(mode="json") for skill in analysis.skills],
                    )
                )
                uploaded.append(UploadedCandidate(candidate=candidate, resume=analysis))
            await session.commit()

        return RecruiterUploadResponse(
            uploaded=len(uploaded),
            candidates=[
                RecruiterCandidateSummary(
                    id=item.candidate.id,
                    name=item.candidate.name,
                    email=item.candidate.email,
                    github_username=item.candidate.github_username,
                    skills=item.resume.skills,
                )
                for item in uploaded
            ],
        )

    async def evaluate_candidates(self, target_role: str) -> RecruiterEvaluateResponse:
        session_factory = self._require_db()
        async with session_factory() as session:
            candidates = (
                await session.scalars(
                    select(Candidate)
                    .options(selectinload(Candidate.skills))
                    .order_by(Candidate.created_at.desc(), Candidate.id.desc())
                )
            ).all()

        results = await asyncio.gather(*(self._evaluate_candidate(candidate, target_role) for candidate in candidates))

        async with session_factory() as session:
            for result in results:
                await self._store_evaluation(session, result)
            await session.commit()

        return RecruiterEvaluateResponse(target_role=target_role, evaluated=len(results), results=results)

    async def rank_candidates(self, target_role: str | None = None) -> RecruiterRankResponse:
        session_factory = self._require_db()
        async with session_factory() as session:
            query = (
                select(Evaluation, Candidate)
                .join(Candidate, Candidate.id == Evaluation.candidate_id)
                .order_by(desc(Evaluation.match_score), Evaluation.updated_at.desc())
            )
            if target_role:
                query = query.where(Evaluation.target_role == target_role)
            rows = (await session.execute(query)).all()

        items: list[RecruiterRankItem] = []
        for index, (evaluation, candidate) in enumerate(rows, start=1):
            verified = evaluation.verified_skills or []
            missing = evaluation.missing_skills or []
            score = evaluation.match_score
            items.append(
                RecruiterRankItem(
                    rank=index,
                    candidate_id=candidate.id,
                    name=candidate.name,
                    email=candidate.email,
                    github_username=candidate.github_username,
                    target_role=evaluation.target_role,
                    match_score=score,
                    top_verified_skills=[str(skill.get("name", "")) for skill in verified[:5] if skill.get("name")],
                    top_missing_skills=[str(skill.get("name", "")) for skill in missing[:5] if skill.get("name")],
                    recommendation="high" if score >= 70 else "medium" if score >= 45 else "low",
                    explanations=evaluation.explanations or {},
                )
            )
        return RecruiterRankResponse(target_role=target_role, candidates=items)

    async def _evaluate_candidate(self, candidate: Candidate, target_role: str) -> RecruiterEvaluationResult:
        async with self._evaluation_semaphore:
            resume = self._resume_from_candidate(candidate)
            github = await self._github_for_candidate(candidate)
            request = CompareRequest(github=github, resume=resume, target_role=target_role)
            if hasattr(self.compare_service, "compare_enhanced"):
                comparison = await self.compare_service.compare_enhanced(request)
            else:
                comparison = self.compare_service.compare(request)
            return self._result_from_comparison(candidate, comparison)

    def _resume_from_candidate(self, candidate: Candidate) -> ResumeAnalysis:
        resume_skill_rows = [row for row in candidate.skills if row.source == "resume"]
        skills = resume_skill_rows[-1].skills if resume_skill_rows else []
        return ResumeAnalysis(
            file_name=f"candidate-{candidate.id}.pdf",
            text_preview=candidate.resume_text[:500],
            skills=skills,
            projects=[],
            warnings=[],
        )

    async def _github_for_candidate(self, candidate: Candidate) -> GitHubAnalysis:
        if not candidate.github_username:
            return self._empty_github(candidate)
        try:
            async with self._github_semaphore:
                return await self.github_service.analyze_user(candidate.github_username)
        except Exception:
            return self._empty_github(candidate)

    @staticmethod
    def _empty_github(candidate: Candidate) -> GitHubAnalysis:
        username = candidate.github_username or f"candidate-{candidate.id}"
        return GitHubAnalysis(username=username, profile_url=f"https://github.com/{username}", public_repos=0)

    @staticmethod
    def _result_from_comparison(candidate: Candidate, comparison: CompareResponse) -> RecruiterEvaluationResult:
        return RecruiterEvaluationResult(
            candidate_id=candidate.id,
            name=candidate.name,
            email=candidate.email,
            github_username=candidate.github_username,
            target_role=comparison.target_role,
            match_score=comparison.evidence_score,
            verified_skills=[skill.model_dump(mode="json") for skill in comparison.verified_skills],
            missing_skills=[skill.model_dump(mode="json") for skill in comparison.missing_skills],
            explanations={
                "insights": [item.model_dump(mode="json") for item in comparison.insights],
                "recommendations": comparison.recommendations,
                "claimed_unproven_skills": [skill.model_dump(mode="json") for skill in comparison.claimed_unproven_skills],
                "github_only_skills": [skill.model_dump(mode="json") for skill in comparison.github_only_skills],
                "problem_solving_signal": comparison.problem_solving_signal,
            },
            role_matches=[match.model_dump(mode="json") for match in comparison.career_matches],
        )

    @staticmethod
    async def _store_evaluation(session: AsyncSession, result: RecruiterEvaluationResult) -> None:
        payload = {
            "candidate_id": result.candidate_id,
            "target_role": result.target_role,
            "match_score": result.match_score,
            "verified_skills": result.verified_skills,
            "missing_skills": result.missing_skills,
            "explanations": result.explanations,
            "role_matches": result.role_matches,
        }
        statement = insert(Evaluation).values(**payload)
        statement = statement.on_conflict_do_update(
            constraint="uq_candidate_role_evaluation",
            set_={
                "match_score": statement.excluded.match_score,
                "verified_skills": statement.excluded.verified_skills,
                "missing_skills": statement.excluded.missing_skills,
                "explanations": statement.excluded.explanations,
                "role_matches": statement.excluded.role_matches,
            },
        )
        await session.execute(statement)

    @staticmethod
    def _extract_email(text: str) -> str | None:
        match = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.IGNORECASE)
        return match.group(0).lower() if match else None

    @staticmethod
    def _extract_github_username(text: str) -> str | None:
        match = re.search(r"github\.com/([A-Za-z0-9-]{1,39})", text, re.IGNORECASE)
        if match:
            return match.group(1).strip("-")
        match = re.search(r"github\s*[:|-]\s*([A-Za-z0-9-]{1,39})", text, re.IGNORECASE)
        return match.group(1).strip("-") if match else None

    @staticmethod
    def _extract_name(text: str, filename: str) -> str:
        for line in text.splitlines()[:8]:
            cleaned = re.sub(r"\s+", " ", line).strip(" -|")
            if 2 <= len(cleaned) <= 80 and not re.search(r"@|github|linkedin|resume|curriculum", cleaned, re.IGNORECASE):
                return cleaned
        return filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()
