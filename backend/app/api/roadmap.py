from fastapi import APIRouter, Request

from app.models.roadmap import RoadmapRequest, RoadmapResponse

router = APIRouter(prefix="/roadmap", tags=["roadmap"])


@router.post("", response_model=RoadmapResponse)
async def roadmap(payload: RoadmapRequest, request: Request) -> RoadmapResponse:
    return await request.app.state.roadmap_service.generate(payload)
