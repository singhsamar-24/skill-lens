from __future__ import annotations

import json
from pathlib import Path

from app.core.normalization import normalize_skill
from app.models.compare import CompareRequest, JobRoleMatch


class JobRoleService:
    def __init__(self, dataset_path: Path | None = None) -> None:
        self.dataset_path = dataset_path or Path(__file__).resolve().parents[1] / "data" / "job_roles.json"
        self.roles = self._load_roles()

    def match(self, request: CompareRequest, *, limit: int = 5) -> list[JobRoleMatch]:
        user_strengths = self._user_skill_strengths(request)
        matches: list[JobRoleMatch] = []

        for role, data in self.roles.items():
            role_skills = [normalize_skill(skill) for skill in data.get("skills", [])]
            if not role_skills:
                continue
            matched = [skill for skill in role_skills if skill in user_strengths]
            missing = [skill for skill in role_skills if skill not in user_strengths]
            weighted_overlap = sum(min(1.0, user_strengths.get(skill, 0.0)) for skill in role_skills)
            score = int(round((weighted_overlap / len(role_skills)) * 100))
            matches.append(
                JobRoleMatch(
                    role=role,
                    match=max(0, min(100, score)),
                    salary=str(data.get("salary_range", "Market dependent")),
                    reason=self._reason(role, matched, missing),
                    matched_skills=matched[:6],
                    missing_skills=missing[:5],
                )
            )

        return sorted(matches, key=lambda item: (item.match, len(item.matched_skills)), reverse=True)[:limit]

    def _load_roles(self) -> dict[str, dict[str, object]]:
        with self.dataset_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    @staticmethod
    def _user_skill_strengths(request: CompareRequest) -> dict[str, float]:
        strengths: dict[str, float] = {}

        for skill in request.github.skills:
            normalized = normalize_skill(skill.normalized or skill.name)
            weight = 1.0 if skill.level == "strong" else 0.85 if skill.level == "moderate" else 0.6
            strengths[normalized] = max(strengths.get(normalized, 0.0), weight)

        for skill in request.resume.skills:
            normalized = normalize_skill(skill.normalized or skill.name)
            weight = 0.95 if skill.classification == "project_backed" else 0.8 if skill.classification == "claimed" else 0.45
            strengths[normalized] = max(strengths.get(normalized, 0.0), weight)

        return strengths

    @staticmethod
    def _reason(role: str, matched: list[str], missing: list[str]) -> str:
        if matched:
            visible = ", ".join(matched[:4])
            if missing:
                return f"You fit {role} because your profile shows {visible}; adding {missing[0]} would raise confidence."
            return f"You fit {role} strongly because the core skill set is already visible: {visible}."
        return f"{role} is a stretch fit right now because the role's core skills are not yet visible in your resume or GitHub evidence."
