from __future__ import annotations

from hashlib import sha256
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from app.core.cache import cache
from app.core.normalization import normalize_skill
from app.models.compare import ComparedSkill, CompareRequest, CompareResponse, JobRoleMatch, MissingSkill, SkillInsight
from app.models.common import EvidenceItem
from app.services.groq_service import GroqService
from app.services.job_role_service import JobRoleService
from app.services.skill_catalog import skills_for_role


class _LLMMissingSkill(BaseModel):
    name: str
    reason: str
    usage: list[str] = Field(default_factory=list)
    impact: str
    priority: str = Field(pattern="^(high|medium|low)$")


class _LLMGapResponse(BaseModel):
    missing_skills: list[_LLMMissingSkill] = Field(default_factory=list)


class _LLMRoleMatch(BaseModel):
    role: str
    reason: str


class _LLMRoleResponse(BaseModel):
    roles: list[_LLMRoleMatch] = Field(default_factory=list)


class CompareService:
    def __init__(self, groq: GroqService | None = None, job_roles: JobRoleService | None = None) -> None:
        self.groq = groq
        self.job_roles = job_roles or JobRoleService()

    def compare(self, request: CompareRequest) -> CompareResponse:
        target_role = request.target_role or "Software Engineer"
        github_by_skill = {skill.normalized: skill for skill in request.github.skills}
        resume_by_skill = {skill.normalized: skill for skill in request.resume.skills}

        verified: list[ComparedSkill] = []
        claimed_unproven: list[ComparedSkill] = []
        github_only: list[ComparedSkill] = []

        for name, resume_skill in resume_by_skill.items():
            github_skill = github_by_skill.get(name)
            if github_skill and github_skill.confidence >= 0.32:
                verified.append(
                    ComparedSkill(
                        name=name,
                        confidence=min(0.99, (resume_skill.confidence + github_skill.confidence) / 2),
                        resume_signal=resume_skill.classification,
                        github_signal=github_skill.level,
                        evidence=[*resume_skill.evidence[:2], *github_skill.evidence[:3]],
                    )
                )
            else:
                claimed_unproven.append(
                    ComparedSkill(
                        name=name,
                        confidence=resume_skill.confidence,
                        resume_signal=resume_skill.classification,
                        evidence=resume_skill.evidence[:3],
                    )
                )

        for name, github_skill in github_by_skill.items():
            if name not in resume_by_skill:
                github_only.append(
                    ComparedSkill(
                        name=name,
                        confidence=github_skill.confidence,
                        github_signal=github_skill.level,
                        evidence=github_skill.evidence[:3],
                    )
                )

        known = set(github_by_skill) | set(resume_by_skill)
        missing = [
            self._fallback_missing_skill(skill, target_role)
            for skill in skills_for_role(target_role)
            if normalize_skill(skill) not in known
        ]

        career_matches = self.job_roles.match(request)
        score = self._score(verified, claimed_unproven, missing)
        insights = self._insights(verified, claimed_unproven, github_only, missing)
        recommendations = self._recommendations(verified, claimed_unproven, github_only, missing)
        return CompareResponse(
            target_role=target_role,
            verified_skills=verified,
            claimed_unproven_skills=claimed_unproven,
            github_only_skills=github_only,
            missing_skills=missing,
            career_matches=career_matches,
            evidence_score=score,
            problem_solving_signal=(request.leetcode.problem_solving_signal if request.leetcode else "unknown"),
            insights=insights,
            recommendations=recommendations,
        )

    async def compare_enhanced(self, request: CompareRequest) -> CompareResponse:
        response = self.compare(request)
        if not self.groq:
            return response

        response.missing_skills = await self._enhance_missing_skills(response, request)
        response.career_matches = await self._enhance_career_matches(response, request)
        response.insights = self._insights(
            response.verified_skills,
            response.claimed_unproven_skills,
            response.github_only_skills,
            response.missing_skills,
        )
        response.recommendations = self._recommendations(
            response.verified_skills,
            response.claimed_unproven_skills,
            response.github_only_skills,
            response.missing_skills,
        )
        return response

    @staticmethod
    def _priority(skill: str, role: str) -> str:
        role_l = role.lower()
        critical = {
            "frontend": {"React", "TypeScript", "JavaScript"},
            "backend": {"Python", "FastAPI", "PostgreSQL"},
            "ai": {"Python", "LLMs", "RAG"},
        }
        for key, skills in critical.items():
            if key in role_l and skill in skills:
                return "high"
        return "medium" if skill in {"Testing", "REST APIs", "System Design"} else "low"

    @classmethod
    def _fallback_missing_skill(cls, skill: str, role: str) -> MissingSkill:
        usage_map = {
            "Redis": ["API response caching", "session storage", "rate-limit counters"],
            "Caching": ["API response caching", "expensive query reuse", "session storage"],
            "PostgreSQL": ["transactional product data", "reporting queries", "relational modeling"],
            "REST APIs": ["service integrations", "frontend-backend contracts", "public API design"],
            "System Design": ["scalability planning", "failure isolation", "technical tradeoff reviews"],
            "Testing": ["regression safety", "CI quality gates", "refactor confidence"],
            "Docker": ["repeatable local setup", "deployment packaging", "service isolation"],
            "FastAPI": ["Python API services", "typed request validation", "async backend endpoints"],
            "React": ["interactive dashboards", "stateful product UI", "component systems"],
            "TypeScript": ["safe frontend contracts", "large codebase refactors", "API response typing"],
        }
        impact_map = {
            "Caching": "Improves response times and reduces repeated database or API load in scalable systems.",
            "PostgreSQL": "Adds reliable data modeling, transactions, and query depth for production backends.",
            "REST APIs": "Makes your work legible as deployable service contracts instead of isolated code.",
            "System Design": "Shows you can reason about scale, reliability, and tradeoffs beyond feature code.",
            "Testing": "Raises trust by proving changes can be shipped without silent regressions.",
            "Docker": "Makes projects easier to run, review, and deploy in production-like environments.",
        }
        normalized = normalize_skill(skill)
        return MissingSkill(
            name=skill,
            priority=cls._priority(skill, role),  # type: ignore[arg-type]
            reason=f"{skill} is a visible hiring signal for {role} because it appears in production-grade role expectations.",
            usage=usage_map.get(normalized, [f"{role} project work", "production feature delivery"]),
            impact=impact_map.get(normalized, f"Strengthens your ability to design and ship credible {role} systems."),
        )

    async def _enhance_missing_skills(self, response: CompareResponse, request: CompareRequest) -> list[MissingSkill]:
        if not response.missing_skills or not self.groq:
            return response.missing_skills
        cache_key = self._gap_cache_key(response, request)
        cached = cache.get(cache_key)
        if isinstance(cached, list) and all(isinstance(item, MissingSkill) for item in cached):
            return cached

        system = (
            "You are a senior engineering hiring bar raiser. Return only strict JSON in this exact shape: "
            '{"missing_skills":[{"name":"Redis","reason":"...","usage":["..."],"impact":"...","priority":"high"}]}. '
            "Every explanation must be role-aware, skill-specific, concise, and grounded in real production usage. "
            "Do not use generic study advice."
        )
        prompt = (
            f"TARGET_ROLE: {response.target_role}\n"
            f"VISIBLE_SKILLS: {self._visible_skill_names(request)}\n"
            f"MISSING_SKILLS_TO_EXPLAIN: {[skill.model_dump() for skill in response.missing_skills]}\n\n"
            "For each missing skill, explain why learning it matters, where it is used in real systems, "
            "and its impact on system design. Preserve the skill names. Priority must be high, medium, or low."
        )
        try:
            data = await self.groq.complete_json(system, prompt, max_tokens=1800, temperature=0.2)
            parsed = _LLMGapResponse.model_validate(data)
            by_name = {normalize_skill(item.name): item for item in parsed.missing_skills}
            enhanced = [
                MissingSkill(
                    name=skill.name,
                    reason=by_name.get(normalize_skill(skill.name), skill).reason,
                    usage=(by_name.get(normalize_skill(skill.name)).usage[:4] if by_name.get(normalize_skill(skill.name)) else skill.usage),
                    impact=by_name.get(normalize_skill(skill.name), skill).impact,
                    priority=(by_name.get(normalize_skill(skill.name), skill).priority),  # type: ignore[arg-type]
                )
                for skill in response.missing_skills
            ]
            cache.set(cache_key, enhanced, ttl_seconds=60 * 60)
            return enhanced
        except (ValidationError, Exception):
            return response.missing_skills

    async def _enhance_career_matches(self, response: CompareResponse, request: CompareRequest) -> list[JobRoleMatch]:
        if not response.career_matches or not self.groq:
            return response.career_matches
        cache_key = self._role_cache_key(response, request)
        cached = cache.get(cache_key)
        if isinstance(cached, list) and all(isinstance(item, JobRoleMatch) for item in cached):
            return cached

        system = (
            "You are a technical recruiter and staff engineer. Return strict JSON only: "
            '{"roles":[{"role":"Backend Engineer","reason":"..."}]}. '
            "Reasons must connect visible skills to the role, mention one practical strength, and stay under 28 words."
        )
        prompt = (
            f"TARGET_ROLE: {response.target_role}\n"
            f"VISIBLE_SKILLS: {self._visible_skill_names(request)}\n"
            f"ROLE_MATCHES: {[match.model_dump() for match in response.career_matches]}\n\n"
            "Rewrite the reason for each role without changing role names, match percentages, salary, or skill lists."
        )
        try:
            data = await self.groq.complete_json(system, prompt, max_tokens=900, temperature=0.2)
            parsed = _LLMRoleResponse.model_validate(data)
            reason_by_role = {item.role: item.reason for item in parsed.roles if len(item.reason.strip()) >= 35}
            enhanced = [match.model_copy(update={"reason": reason_by_role.get(match.role, match.reason)}) for match in response.career_matches]
            cache.set(cache_key, enhanced, ttl_seconds=60 * 60)
            return enhanced
        except (ValidationError, Exception):
            return response.career_matches

    @staticmethod
    def _visible_skill_names(request: CompareRequest) -> list[str]:
        names = {normalize_skill(skill.normalized or skill.name) for skill in request.github.skills}
        names.update(normalize_skill(skill.normalized or skill.name) for skill in request.resume.skills)
        return sorted(names)

    @staticmethod
    def _gap_cache_key(response: CompareResponse, request: CompareRequest) -> str:
        payload = {
            "role": response.target_role,
            "missing": [skill.name for skill in response.missing_skills],
            "visible": CompareService._visible_skill_names(request),
        }
        return f"gap-explain:{sha256(str(payload).encode('utf-8')).hexdigest()}"

    @staticmethod
    def _role_cache_key(response: CompareResponse, request: CompareRequest) -> str:
        payload: dict[str, Any] = {
            "roles": [(match.role, match.match) for match in response.career_matches],
            "visible": CompareService._visible_skill_names(request),
        }
        return f"role-map:{sha256(str(payload).encode('utf-8')).hexdigest()}"

    @staticmethod
    def _score(verified: list[ComparedSkill], claimed: list[ComparedSkill], missing: list[MissingSkill]) -> int:
        if not verified:
            return max(0, 25 - min(25, len(claimed) * 4 + len(missing) * 3))
        base = min(90, 35 + len(verified) * 10)
        penalty = min(30, len(claimed) * 3 + len([skill for skill in missing if skill.priority == "high"]) * 6)
        breadth_bonus = min(15, len(verified) * 2)
        return max(0, min(100, base + breadth_bonus - penalty))

    @staticmethod
    def _recommendations(
        verified: list[ComparedSkill],
        claimed: list[ComparedSkill],
        github_only: list[ComparedSkill],
        missing: list[MissingSkill],
    ) -> list[str]:
        recommendations: list[str] = []
        if verified:
            recommendations.append("Move your strongest verified skills to the top of the resume and link the evidence repositories.")
        if claimed:
            recommendations.append("Add small portfolio commits or README case studies for claimed skills that lack GitHub evidence.")
        if github_only:
            recommendations.append("Add GitHub-only strengths to the resume so recruiters see evidence-backed breadth.")
        if missing:
            recommendations.append("Prioritize one high-impact missing skill and ship a focused project within two weeks.")
        return recommendations[:4]

    @staticmethod
    def _insights(
        verified: list[ComparedSkill],
        claimed: list[ComparedSkill],
        github_only: list[ComparedSkill],
        missing: list[MissingSkill],
    ) -> list[SkillInsight]:
        insights: list[SkillInsight] = []

        for skill in sorted(claimed, key=lambda item: item.confidence, reverse=True)[:2]:
            insights.append(
                SkillInsight(
                    type="over_claim",
                    title=f"You are over-claiming {skill.name}",
                    detail=f"{skill.name} appears on the resume, but SkillLens found little matching GitHub evidence. Add a focused repository, tests, or a README case study.",
                    severity="high" if skill.confidence >= 0.65 else "medium",
                )
            )

        for skill in sorted(github_only, key=lambda item: item.confidence, reverse=True)[:2]:
            if skill.confidence >= 0.42:
                insights.append(
                    SkillInsight(
                        type="under_sell",
                        title=f"You are under-selling {skill.name}",
                        detail=f"GitHub shows credible {skill.name} evidence, but the resume does not claim it clearly. Add a concise evidence-backed bullet.",
                        severity="medium",
                    )
                )

        strongest_area = CompareService._strongest_area(verified + github_only)
        if strongest_area:
            insights.append(
                SkillInsight(
                    type="strength",
                    title=f"Your strongest area is {strongest_area}",
                    detail="This area has the densest evidence across verified and GitHub-only skills. Lead interviews with projects from this cluster.",
                    severity="low",
                )
            )

        high_missing = [skill for skill in missing if skill.priority == "high"]
        if high_missing:
            names = ", ".join(skill.name for skill in high_missing[:3])
            insights.append(
                SkillInsight(
                    type="gap",
                    title=f"High-priority gaps: {names}",
                    detail="These role-critical skills should become the next portfolio proof targets.",
                    severity="high",
                )
            )

        if not insights and verified:
            insights.append(
                SkillInsight(
                    type="proof",
                    title="Your claims are unusually well supported",
                    detail="The strongest resume claims have matching repository evidence. Keep source links visible and explain the decisions behind them.",
                    severity="low",
                )
            )
        return insights[:5]

    @staticmethod
    def _strongest_area(skills: list[ComparedSkill]) -> str | None:
        areas = {
            "frontend development": {"React", "TypeScript", "JavaScript", "Tailwind CSS"},
            "backend development": {"Python", "FastAPI", "PostgreSQL", "REST APIs", "Docker"},
            "AI engineering": {"LLMs", "RAG", "Python", "FastAPI"},
            "engineering fundamentals": {"Testing", "System Design", "Data Structures", "CI/CD"},
        }
        scores: dict[str, float] = {area: 0.0 for area in areas}
        for skill in skills:
            for area, names in areas.items():
                if skill.name in names:
                    scores[area] += skill.confidence
        best_area, best_score = max(scores.items(), key=lambda item: item[1])
        return best_area if best_score > 0 else None
