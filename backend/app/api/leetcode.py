from fastapi import APIRouter, Request

from app.models.leetcode import LeetCodeAnalysis, LeetCodeAnalyzeRequest

router = APIRouter(prefix="/leetcode", tags=["leetcode"])


@router.post("/analyze", response_model=LeetCodeAnalysis)
async def analyze_leetcode(payload: LeetCodeAnalyzeRequest, request: Request) -> LeetCodeAnalysis:
    return await request.app.state.leetcode_service.analyze_user(payload.username)
