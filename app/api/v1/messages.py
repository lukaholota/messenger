from fastapi import APIRouter
from fastapi.params import Depends

from app.api.deps import get_message_service
from app.schemas.message import MessageRead, MessageCreate
from app.services.message_service import MessageService

router = APIRouter()


@router.post(
    '/send-message',
    response_model=MessageRead,
)
async def send_message(
        message_in: MessageCreate,
        message_service: MessageService = Depends(get_message_service),
):
    new_message = await message_service.create_message(message_in)
    return new_message
