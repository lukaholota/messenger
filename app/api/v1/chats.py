from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter
from starlette import status

from app.api.deps import get_chat_service

from app.schemas.chat import ChatRead, ChatCreate, ChatWithDetails, ChatUpdate, \
    ChatUpdateRead, ChatAddParticipants
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


@router.get(
    '/chats/{chat_id}',
    response_model=ChatWithDetails,
    dependencies=[
        Depends(RateLimiter(times=60, seconds=60)),
    ],
)
async def read_chat(
        chat_id: int,
        chat_service: ChatService = Depends(get_chat_service),

):
    chat = await chat_service.get_chat(chat_id)
    return chat


@router.post(
    '/chats/update',
    response_model=ChatUpdateRead,
    dependencies=[Depends(RateLimiter(times=30, seconds=60))]
)
async def update_chat(
        chat_in: ChatUpdate,
        chat_service: ChatService = Depends(get_chat_service)
):
    chat = await chat_service.update_chat(chat_in)

    return chat


@router.post(
    '/chats/add-participants',
    response_model=ChatRead,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def add_chat_participants(
        in_data: ChatAddParticipants,
        chat_service: ChatService = Depends(get_chat_service)
):
    chat = await chat_service.add_participants(
        in_data.chat_id,
        in_data.participants_ids
    )
    return chat
