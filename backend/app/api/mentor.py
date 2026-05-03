from fastapi import APIRouter, Request

from app.models.mentor import MentorChatRequest, MentorChatResponse

router = APIRouter(prefix="/mentor", tags=["mentor"])


@router.post("/chat", response_model=MentorChatResponse)
async def mentor_chat(payload: MentorChatRequest, request: Request) -> MentorChatResponse:
    return await request.app.state.mentor_service.chat(payload)
