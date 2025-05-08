from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.deps import get_chat_service, get_current_user
from app.db.session import get_db_session
from app.models import User
from app.schemas.chat import ChatRead, ChatCreate, ChatWithDetails
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


@router.get('/chats/{chat_id}', response_model=ChatWithDetails)
async def read_chat(
        chat_id: int,
        chat_service: ChatService = Depends(get_chat_service)
):
    chat = await chat_service.get_chat(chat_id)

    return chat
