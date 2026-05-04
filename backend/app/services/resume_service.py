from __future__ import annotations

import hashlib
from io import BytesIO
from typing import Any

from fastapi import UploadFile
from pydantic import BaseModel, Field, ValidationError
from pypdf import PdfReader

from app.core.cache import cache
from app.core.errors import bad_request
from app.core.normalization import normalize_skill
from app.core.settings import Settings
from app.models.common import ResumeSkill, WarningMessage
from app.models.resume import ResumeAnalysis, ResumeProject
from app.services.groq_service import GroqService
from app.services.skill_catalog import keyword_skill_hits


class _LLMResumeSkill(BaseModel):
    name: str
    classification: str = Field(pattern="^(claimed|project_backed|weak)$")
    confidence: float = Field(ge=0, le=1)
    evidence: list[str] = Field(default_factory=list)


class _LLMResumeProject(BaseModel):
    name: str
    description: str
    skills: list[str] = Field(default_factory=list)


class _LLMResumeResponse(BaseModel):
    skills: list[_LLMResumeSkill] = Field(default_factory=list)
    projects: list[_LLMResumeProject] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ResumeService:
    def __init__(self, settings: Settings, groq: GroqService) -> None:
        self.settings = settings
        self.groq = groq

    async def analyze_upload(self, file: UploadFile) -> ResumeAnalysis:
        filename = file.filename or "resume.pdf"
        if not filename.lower().endswith(".pdf"):
            raise bad_request("resume_invalid_type", "Resume upload must be a PDF file.")

        content = await file.read()
        if len(content) > self.settings.max_resume_bytes:
            raise bad_request("resume_too_large", "Resume PDF exceeds the configured size limit.")
        if not content:
            raise bad_request("resume_empty", "Resume PDF is empty.")

        file_hash = hashlib.sha256(content).hexdigest()
        cache_key = f"resume:{file_hash}"
        cached = cache.get(cache_key)
        if isinstance(cached, ResumeAnalysis):
            return cached

        text = self._extract_pdf_text(content)
        if len(text.strip()) < 40:
            raise bad_request("resume_empty", "Could not extract enough text from the resume PDF.")

        try:
            parsed = await self._parse_with_groq(text)
            warnings = [WarningMessage(code="resume_llm_warning", message=warning) for warning in parsed.warnings]
        except Exception:
            parsed = self._parse_with_keywords(text)
            warnings = [
                WarningMessage(
                    code="resume_fallback_parser",
                    message="AI resume parsing was temporarily unavailable, so SkillLens used keyword-based extraction.",
                )
            ]
        analysis = ResumeAnalysis(
            file_name=filename,
            text_preview=text[:500],
            skills=[
                ResumeSkill(
                    name=skill.name,
                    normalized=normalize_skill(skill.name),
                    classification=skill.classification,  # type: ignore[arg-type]
                    confidence=skill.confidence,
                    evidence=skill.evidence[:5],
                )
                for skill in parsed.skills
            ],
            projects=[
                ResumeProject(
                    name=project.name,
                    description=project.description,
                    skills=[normalize_skill(skill) for skill in project.skills],
                )
                for project in parsed.projects
            ],
            warnings=warnings,
        )
        cache.set(cache_key, analysis, ttl_seconds=15 * 60)
        return analysis

    @staticmethod
    def _parse_with_keywords(text: str) -> _LLMResumeResponse:
        skills = [
            _LLMResumeSkill(
                name=skill,
                classification="claimed",
                confidence=0.45,
                evidence=[f"{skill} appears in the resume text."],
            )
            for skill in sorted(keyword_skill_hits(text))
        ]
        if not skills:
            skills = [
                _LLMResumeSkill(
                    name="General Engineering",
                    classification="weak",
                    confidence=0.25,
                    evidence=["Resume text was readable, but no catalogued technical skills were detected."],
                )
            ]
        return _LLMResumeResponse(skills=skills[:18], projects=[], warnings=[])

    @staticmethod
    def _extract_pdf_text(content: bytes) -> str:
        try:
            reader = PdfReader(BytesIO(content))
            pages = [(page.extract_text() or "") for page in reader.pages]
        except Exception as exc:
            raise bad_request("resume_invalid_pdf", "Could not read the uploaded PDF.") from exc
        return "\n".join(pages).strip()

    async def _parse_with_groq(self, text: str) -> _LLMResumeResponse:
        system = (
            "You extract resume skill evidence for a career analysis product. "
            "Return only strict JSON with keys: skills, projects, warnings. "
            "Each skill must include name, classification, confidence, evidence. "
            "classification must be one of claimed, project_backed, weak."
        )
        prompt = (
            "Analyze this resume text. Classify skills as project_backed only when tied to explicit work, project, or impact. "
            "Use weak when a skill is listed with no context. Keep evidence short.\n\n"
            f"RESUME_TEXT:\n{text[:12000]}"
        )
        data: dict[str, Any] = await self.groq.complete_json(system, prompt, max_tokens=2200)
        try:
            return _LLMResumeResponse.model_validate(data)
        except ValidationError as first_error:
            repair_prompt = (
                "The previous JSON failed this validation error. Return corrected strict JSON only.\n"
                f"VALIDATION_ERROR:\n{first_error}\n\nPREVIOUS_JSON:\n{data}"
            )
            repaired = await self.groq.complete_json(system, repair_prompt, max_tokens=1600)
            return _LLMResumeResponse.model_validate(repaired)
