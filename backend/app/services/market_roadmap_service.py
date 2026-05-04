from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from app.core.cache import cache
from app.core.normalization import normalize_skill
from app.models.roadmap import MarketCompanyRoadmap, MarketRoadmapRequest, MarketRoadmapResponse, MarketUserSkill
from app.services.groq_service import GroqService


class _LLMCompanyRoadmap(BaseModel):
    company: str
    fit: int = Field(ge=0, le=100)
    gaps: list[str] = Field(default_factory=list)
    prep_plan: list[str] = Field(default_factory=list)
    question_themes: list[str] = Field(default_factory=list)


class _LLMMarketRoadmap(BaseModel):
    companies: list[_LLMCompanyRoadmap] = Field(default_factory=list)


class MarketRoadmapService:
    def __init__(self, groq: GroqService | None, dataset_path: Path | None = None) -> None:
        self.groq = groq
        self.dataset_path = dataset_path or Path(__file__).resolve().parents[1] / "data" / "company_profiles.json"
        self.company_profiles = self._load_profiles()

    def get_company_profiles(self, role: str) -> list[dict[str, Any]]:
        if role in self.company_profiles:
            return self.company_profiles[role]
        role_l = role.lower()
        if "front" in role_l:
            return self.company_profiles["Frontend Engineer"]
        if "back" in role_l:
            return self.company_profiles["Backend Engineer"]
        if "full" in role_l:
            return self.company_profiles["Full Stack Developer"]
        if "mobile" in role_l or "app" in role_l or "android" in role_l or "ios" in role_l:
            return self.company_profiles["Mobile/App Developer"]
        return self.company_profiles.get("Backend Engineer", [])

    def compute_fit_score(self, user_skills: list[str | MarketUserSkill], company_skills: list[str]) -> int:
        strengths = self._skill_strengths(user_skills)
        required = [normalize_skill(skill) for skill in company_skills]
        if not required:
            return 0
        matched = sum(min(1.0, strengths.get(skill, 0.0)) for skill in required)
        return max(0, min(100, int(round((matched / len(required)) * 100))))

    async def generate_company_roadmap(self, request: MarketRoadmapRequest) -> MarketRoadmapResponse:
        cache_key = self._cache_key(request)
        cached = cache.get(cache_key)
        if isinstance(cached, MarketRoadmapResponse):
            return cached

        profiles = self.get_company_profiles(request.target_role)
        fallback = self._fallback_response(request.user_skills, profiles)
        if not self.groq:
            cache.set(cache_key, fallback, ttl_seconds=30 * 60)
            return fallback

        system = (
            "You are a senior India-focused tech hiring coach. Return strict JSON only with key companies. "
            "Each company item must include company, fit, gaps, prep_plan, question_themes. "
            "Use the provided company profiles and user skills. Keep prep_plan to 2-3 concrete weekly actions. "
            "Do not invent companies or salary ranges."
        )
        prompt = (
            f"TARGET_ROLE: {request.target_role}\n"
            f"USER_SKILLS: {self._skill_strengths(request.user_skills)}\n"
            f"COMPANY_PROFILES: {json.dumps(profiles, ensure_ascii=True)}\n\n"
            "Enhance the fallback fit analysis with concise company-specific gaps, likely question themes, "
            "and a 2-3 week preparation roadmap per company. Preserve company names."
        )
        try:
            data = await self.groq.complete_json(system, prompt, max_tokens=3600, temperature=0.18)
            parsed = _LLMMarketRoadmap.model_validate(data)
            response = self._merge_llm_response(fallback, parsed)
        except (ValidationError, Exception):
            response = fallback
        cache.set(cache_key, response, ttl_seconds=30 * 60)
        return response

    def _fallback_response(self, user_skills: list[str | MarketUserSkill], profiles: list[dict[str, Any]]) -> MarketRoadmapResponse:
        strengths = self._skill_strengths(user_skills)
        companies: list[MarketCompanyRoadmap] = []
        for profile in profiles:
            required = [normalize_skill(skill) for skill in profile.get("must_have_skills", [])]
            gaps = [skill for skill in required if strengths.get(skill, 0.0) < 0.55]
            fit = self.compute_fit_score(user_skills, required)
            companies.append(
                MarketCompanyRoadmap(
                    company=str(profile.get("company", "")),
                    fit=fit,
                    salary=str(profile.get("salary_range", "Market dependent")),
                    process=[str(item) for item in profile.get("hiring_process", [])],
                    gaps=gaps[:5],
                    prep_plan=self._prep_plan(gaps, profile),
                    question_themes=[str(item) for item in profile.get("question_style", [])[:6]],
                )
            )
        return MarketRoadmapResponse(companies=sorted(companies, key=lambda item: item.fit, reverse=True))

    @staticmethod
    def _merge_llm_response(fallback: MarketRoadmapResponse, parsed: _LLMMarketRoadmap) -> MarketRoadmapResponse:
        by_company = {item.company: item for item in parsed.companies}
        companies: list[MarketCompanyRoadmap] = []
        for company in fallback.companies:
            enhanced = by_company.get(company.company)
            if not enhanced:
                companies.append(company)
                continue
            companies.append(
                company.model_copy(
                    update={
                        "fit": max(0, min(100, enhanced.fit or company.fit)),
                        "gaps": enhanced.gaps[:5] or company.gaps,
                        "prep_plan": enhanced.prep_plan[:4] or company.prep_plan,
                        "question_themes": enhanced.question_themes[:6] or company.question_themes,
                    }
                )
            )
        return MarketRoadmapResponse(companies=sorted(companies, key=lambda item: item.fit, reverse=True))

    @staticmethod
    def _prep_plan(gaps: list[str], profile: dict[str, Any]) -> list[str]:
        primary_gap = gaps[0] if gaps else "portfolio depth"
        tips = [str(item) for item in profile.get("prep_tips", [])]
        plan = [
            f"Week 1: close the {primary_gap} gap with focused notes, 25-35 targeted problems, and one implementation drill.",
            "Week 2: build or upgrade one role-relevant project artifact with tests, README decisions, and measurable behavior.",
            "Week 3: run mock interviews for DSA, machine coding, and the company-specific design themes.",
        ]
        return [*tips[:1], *plan][:4]

    @staticmethod
    def _skill_strengths(user_skills: list[str | MarketUserSkill]) -> dict[str, float]:
        strengths: dict[str, float] = {}
        for item in user_skills:
            if isinstance(item, MarketUserSkill):
                name = item.name
                weight = item.weight
            elif isinstance(item, dict):
                name = str(item.get("name", ""))
                weight = float(item.get("weight", 1.0))
            else:
                name = str(item)
                weight = 1.0
            normalized = normalize_skill(name)
            if normalized:
                strengths[normalized] = max(strengths.get(normalized, 0.0), min(1.5, weight))
        return strengths

    def _cache_key(self, request: MarketRoadmapRequest) -> str:
        payload = {
            "role": request.target_role,
            "skills": sorted(self._skill_strengths(request.user_skills).items()),
        }
        return f"market-roadmap:{sha256(json.dumps(payload, sort_keys=True).encode('utf-8')).hexdigest()}"

    def _load_profiles(self) -> dict[str, list[dict[str, Any]]]:
        with self.dataset_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
