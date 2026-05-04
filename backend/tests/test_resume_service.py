from io import BytesIO

import pytest
from fastapi import UploadFile

from app.core.errors import SkillLensError
from app.core.settings import Settings
from app.services.groq_service import GroqService
from app.services.resume_service import ResumeService


@pytest.mark.asyncio
async def test_resume_empty_pdf_rejected():
    service = ResumeService(Settings(), GroqService(Settings()))
    upload = UploadFile(filename="resume.pdf", file=BytesIO(b""))

    with pytest.raises(SkillLensError) as error:
        await service.analyze_upload(upload)

    assert error.value.detail["code"] == "resume_empty"


@pytest.mark.asyncio
async def test_resume_groq_failure_uses_keyword_fallback():
    text = "Python FastAPI React TypeScript REST API testing project"
    parsed = ResumeService._parse_with_keywords(text)

    assert any(skill.name == "Python" for skill in parsed.skills)
    assert any(skill.name == "React" for skill in parsed.skills)
