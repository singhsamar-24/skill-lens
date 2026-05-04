from fastapi import APIRouter, File, Query, Request, UploadFile

from app.models.recruiter import RecruiterEvaluateRequest, RecruiterEvaluateResponse, RecruiterRankResponse, RecruiterUploadResponse

router = APIRouter(prefix="/recruiter", tags=["recruiter"])


@router.post("/upload", response_model=RecruiterUploadResponse)
async def upload_candidates(request: Request, files: list[UploadFile] = File(...)) -> RecruiterUploadResponse:
    return await request.app.state.recruiter_service.upload_resumes(files)


@router.post("/evaluate", response_model=RecruiterEvaluateResponse)
async def evaluate_candidates(payload: RecruiterEvaluateRequest, request: Request) -> RecruiterEvaluateResponse:
    return await request.app.state.recruiter_service.evaluate_candidates(payload.target_role)


@router.get("/rank", response_model=RecruiterRankResponse)
async def rank_candidates(request: Request, target_role: str | None = Query(default=None)) -> RecruiterRankResponse:
    return await request.app.state.recruiter_service.rank_candidates(target_role)
