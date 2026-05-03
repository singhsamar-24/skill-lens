from fastapi import APIRouter, Request

from app.models.compare import CompareRequest, CompareResponse

router = APIRouter(prefix="/compare", tags=["compare"])


@router.post("", response_model=CompareResponse)
async def compare(payload: CompareRequest, request: Request) -> CompareResponse:
    service = request.app.state.compare_service
    if hasattr(service, "compare_enhanced"):
        return await service.compare_enhanced(payload)
    return service.compare(payload)
