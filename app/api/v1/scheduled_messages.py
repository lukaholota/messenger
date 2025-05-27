from fastapi import APIRouter
from fastapi.params import Depends
from fastapi_limiter.depends import RateLimiter

from app.api.deps import get_scheduled_message_service
from app.schemas.scheduled_message import ScheduledMessageCreate, \
    ScheduledMessageGet, ScheduledMessageRead, ScheduledMessageDelete, \
    ScheduledMessageReadMultiple, ScheduledMessageUpdate, \
    ScheduledMessageUpdateResponse
from app.services.scheduled_message_service import ScheduledMessageService

router = APIRouter()


@router.post("/schedule-message")
async def schedule_message(
        scheduled_message_in: ScheduledMessageCreate,
        message_service: ScheduledMessageService = Depends(
            get_scheduled_message_service
        ),
):
    return await message_service.schedule_new_message(
        chat_id=scheduled_message_in.chat_id,
        content=scheduled_message_in.content,
        scheduled_send_at=scheduled_message_in.scheduled_send_at,
    )


@router.post(
    "/get-scheduled-messages",
    response_model=ScheduledMessageReadMultiple
)
async def get_scheduled_messages(
        data_in: ScheduledMessageGet,
        scheduled_message_service: ScheduledMessageService = Depends(
            get_scheduled_message_service
        ),
):
    chat_id = data_in.chat_id

    scheduled_messages = await (
        scheduled_message_service.get_scheduled_messages(
            chat_id
    ))
    return ScheduledMessageReadMultiple(scheduled_messages=scheduled_messages)


@router.delete(
    '/delete-scheduled-message',
    response_model=ScheduledMessageRead
)
async def delete_scheduled_message(
        scheduled_message_in: ScheduledMessageDelete,
        scheduled_message_service: ScheduledMessageService = Depends(
            get_scheduled_message_service
        )
):
    chat_id = scheduled_message_in.chat_id
    scheduled_message_id = scheduled_message_in.scheduled_message_id

    deleted_scheduled_message = await (
        scheduled_message_service.cancel_scheduled_message(
            scheduled_message_id=scheduled_message_id,
            chat_id=chat_id,
        )
    )
    return deleted_scheduled_message


@router.post(
    '/update-scheduled-message',
    response_model=ScheduledMessageUpdateResponse,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def update_scheduled_message(
        scheduled_message_in: ScheduledMessageUpdate,
        scheduled_message_service: ScheduledMessageService = Depends(
            get_scheduled_message_service
        )
):
    chat_id = scheduled_message_in.chat_id
    scheduled_message_id = scheduled_message_in.scheduled_message_id
    content = scheduled_message_in.content
    scheduled_send_at = scheduled_message_in.scheduled_send_at

    old_scheduled_message, new_scheduled_message = await (
        scheduled_message_service.update_scheduled_message(
            chat_id=chat_id,
            scheduled_message_id=scheduled_message_id,
            content=content,
            scheduled_send_at=scheduled_send_at,
    ))

    return {
        'old_scheduled_message': old_scheduled_message,
        'new_scheduled_message': new_scheduled_message,
    }
