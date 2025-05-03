from fastapi import APIRouter, Depends
from starlette import status

from app.api.deps import get_chat_service
from app.schemas.chat import ChatRead, ChatCreate
from app.services.chat_service import ChatService

router = APIRouter()


@router.post(
    "/create-chat",
    response_model=ChatRead,
    status_code=status.HTTP_201_CREATED
)
async def create_chat(
        chat_in: ChatCreate,
        chat_service: ChatService = Depends(get_chat_service)
) -> ChatRead:
    new_chat = await chat_service.create_chat(chat_in)
    return new_chat
