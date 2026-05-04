from fastapi import APIRouter, Request

from app.models.roadmap import MarketRoadmapRequest, MarketRoadmapResponse, RoadmapRequest, RoadmapResponse

router = APIRouter(prefix="/roadmap", tags=["roadmap"])


@router.post("", response_model=RoadmapResponse)
async def roadmap(payload: RoadmapRequest, request: Request) -> RoadmapResponse:
    return await request.app.state.roadmap_service.generate(payload)


@router.post("/market", response_model=MarketRoadmapResponse)
async def market_roadmap(payload: MarketRoadmapRequest, request: Request) -> MarketRoadmapResponse:
    return await request.app.state.market_roadmap_service.generate_company_roadmap(payload)
