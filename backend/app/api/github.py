from fastapi import APIRouter, Request

from app.models.github import GitHubAnalysis, GitHubAnalyzeRequest

router = APIRouter(prefix="/github", tags=["github"])


@router.post("/analyze", response_model=GitHubAnalysis)
async def analyze_github(payload: GitHubAnalyzeRequest, request: Request) -> GitHubAnalysis:
    return await request.app.state.github_service.analyze_user(payload.username)
