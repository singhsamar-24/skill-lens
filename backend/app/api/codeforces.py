from fastapi import APIRouter, Request

from app.models.codeforces import CodeforcesAnalysis, CodeforcesAnalyzeRequest

router = APIRouter(prefix="/codeforces", tags=["codeforces"])


@router.post("/analyze", response_model=CodeforcesAnalysis)
async def analyze_codeforces(payload: CodeforcesAnalyzeRequest, request: Request) -> CodeforcesAnalysis:
    return await request.app.state.codeforces_service.analyze_user(payload.username)
