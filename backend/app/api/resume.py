from fastapi import APIRouter, File, Request, UploadFile

from app.models.resume import ResumeAnalysis

router = APIRouter(prefix="/resume", tags=["resume"])


@router.post("/analyze", response_model=ResumeAnalysis)
async def analyze_resume(request: Request, file: UploadFile = File(...)) -> ResumeAnalysis:
    return await request.app.state.resume_service.analyze_upload(file)
