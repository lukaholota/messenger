import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository.chat_read_status_repository import \
    ChatReadStatusRepository
from app.infrastructure.cache.redis_pubsub import RedisPubSub
from app.schemas.chat_read_status import ChatReadStatusUpdate, \
    ChatReadStatusRead


class ChatReadService:
    def __init__(
            self,
            db: AsyncSession,
            chat_read_status_repository: ChatReadStatusRepository,
            pubsub: RedisPubSub
    ):
        self.db = db
        self.chat_read_status_repository = chat_read_status_repository
        self.pubsub = pubsub

    async def update_read_status(
            self,
            user_id: int,
            data_in: ChatReadStatusUpdate
    ):
        chat_id = data_in.chat_id
        last_read_message = await (
            self.chat_read_status_repository.get_last_read_message(
                chat_id, user_id
            )
        )
        last_read_message = await (self.chat_read_status_repository
        .mark_as_read(
            last_read_message, data_in.message_id
        ))
        await self.db.commit()
        await self.db.refresh(last_read_message)

        data_out = ChatReadStatusRead(
            chat_id=chat_id,
            user_id=user_id,
            last_read_message_id=last_read_message.last_read_message_id,
            read_at=last_read_message.read_at
        ).model_dump(mode='json')
        await self.pubsub.publish(
            f'chat:{chat_id}',
            json.dumps({'event': 'read_status_updated', 'data': data_out})
        )
