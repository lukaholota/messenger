from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends

from app.api.deps import get_message_service
from app.exceptions import MessagingConnectionError, InvalidMessageDataError, \
    MessagePublishError
from app.rabbitmq_client import publish_delayed_message
from app.schemas.message import MessageRead, MessageCreate, \
    ScheduledMessageCreate
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


@router.post("/send-schedule-message")
async def send_scheduled_message(
        scheduled_message_in: ScheduledMessageCreate,
):
    now = datetime.now()
    send_at_datetime = scheduled_message_in.send_at

    if send_at_datetime <= now:
        raise HTTPException(
            status_code=400, detail="Scheduled time must be in future"
        )

    delay = send_at_datetime - now
    delay_seconds = int(delay.total_seconds())

    if delay_seconds <= 0:
        raise HTTPException(
            status_code=400, detail="Delay must be greater than 0"
        )

    message_payload = {
        'chat_id': scheduled_message_in.chat_id,
        'content': scheduled_message_in.content,
        'scheduled_at_iso': send_at_datetime.isoformat(),
        'created_at_iso': now.isoformat(),
    }

    try:
        await publish_delayed_message(message_payload, delay_seconds)
        return {"message": "Message scheduled successfully"}
    except MessagingConnectionError:
        raise HTTPException(
            status_code=403,
            detail="Messaging connection error",
        )
    except InvalidMessageDataError:
        raise HTTPException(
            status_code=400,
            detail="Invalid message data",
        )
    except MessagePublishError:
        raise HTTPException(
            status_code=500,
            detail="Messaging server error",
        )
