from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository.chat_read_status_repository import \
    ChatReadStatusRepository
from app.db.repository.chat_repository import ChatRepository
from app.db.repository.user_repository import UserRepository
from app.infrastructure.exceptions.exceptions import (
    ChatValidationError,
    UsersNotFoundError,
    DatabaseError,
)
from app.infrastructure.cache.redis_cache import RedisCache
from app.models import User, Chat
from app.schemas.chat import ChatCreate, ChatUpdate


class ChatService:
    def __init__(
            self,
            db: AsyncSession,
            chat_repository: ChatRepository,
            user_repository: UserRepository,
            chat_read_status_repository: ChatReadStatusRepository,
            current_user_id: int,
            redis: RedisCache
    ):
        self.db: AsyncSession = db
        self.chat_repository = chat_repository
        self.user_repository = user_repository
        self.chat_read_status_repository = chat_read_status_repository
        self.current_user_id = current_user_id
        self.redis = redis

    async def create_chat(
            self,
            chat_in: ChatCreate,
    ):
        self._validate_chat_input(chat_in)

        users_to_add = await self._get_and_validate_participants(
            chat_in.participant_ids
        )

        await self._check_existing_private_chat(
            chat_in.is_group,
            chat_in.participant_ids
        )

        chat_name = self._determine_chat_name(chat_in, users_to_add)

        try:
            chat = await self._create_chat_in_db(
                chat_name=chat_name,
                users_to_add=users_to_add,
                is_group=chat_in.is_group,
            )
            await self.db.flush()

            await self.create_chat_read_statuses(
                user_ids=chat_in.participant_ids,
                chat_id=chat.chat_id
            )

            await self.db.commit()
            await self.db.refresh(chat, attribute_names=['participants'])

            return chat
        except SQLAlchemyError as db_exc:
            await self.db.rollback()
            raise DatabaseError(
                "Failed to create chat due to database issue"
            ) from db_exc
        except Exception as exc:
            await self.db.rollback()
            raise exc

    def _validate_chat_input(self, chat_in: ChatCreate):
        if not chat_in.participant_ids:
            raise ChatValidationError("No participants in chat")
        if len(set(chat_in.participant_ids)) != len(chat_in.participant_ids):
            raise ChatValidationError("Duplicate user in one chat")
        if not chat_in.is_group and len(chat_in.participant_ids) > 2:
            raise ChatValidationError("More than two users in non group chat")
        if not chat_in.is_group and len(chat_in.participant_ids) < 2:
            raise ChatValidationError("Only one member in private chat")

    async def _get_and_validate_participants(
            self,
            participant_ids: list[int]
    ):
        users_to_add = await self.user_repository.get_by_ids(
            ids=participant_ids
        )
        if len(users_to_add) != len(participant_ids):
            found_ids = {user.user_id for user in users_to_add}
            missing_ids = set(participant_ids) - found_ids
            raise UsersNotFoundError(
                "Couldn't find users for IDs",
                missing_ids
            )

        return users_to_add

    async def _check_existing_private_chat(
            self,
            is_group: bool,
            participant_ids: list[int],
    ):
        if not is_group:
            existing_private_chat = (await self.chat_repository
                                     .get_chat_by_participants_ids(
                participant_ids
            ))
            if existing_private_chat:
                raise ChatValidationError(
                    "Private chat for these users already exists"
                )

    def _determine_chat_name(
            self,
            chat_in: ChatCreate,
            users_to_add: list[User]
    ) -> str:
        chat_name = chat_in.name
        if chat_name:
            return chat_name
        participants_names = [user.display_name for user in users_to_add]
        return ', '.join(participants_names)

    async def _create_chat_in_db(
            self,
            *,
            chat_name: str,
            users_to_add: list[User],
            is_group: bool
    ) -> Chat:
        chat = await self.chat_repository.create_chat_with_participants(
            name=chat_name,
            is_group=is_group,
            users_to_add=users_to_add
        )
        return chat

    async def create_chat_read_statuses(
            self,
            user_ids: list[int],
            chat_id: int,
    ):
        chat_read_statuses = []
        for user_id in user_ids:
            chat_read_statuses.append(await self.chat_read_status_repository
                                      .create_chat_read_status(chat_id, user_id
                                    ))
        self.db.add_all(chat_read_statuses)

    async def get_chat(
            self,
            chat_id: int
    ) -> Chat:
        redis_key = f'chat:{chat_id}:full'

        cached_chat = await self.redis.get(redis_key)
        if cached_chat:
            return cached_chat

        existing_chat = await self.chat_repository.get_chat_with_relationships(
            chat_id
        )
        if not existing_chat:
            raise ChatValidationError('Chat not found')

        if self.current_user_id not in [
            p.user_id for p in existing_chat.participants
        ]:
            raise ChatValidationError('User not in chat')

        await self.redis.set(redis_key, existing_chat)
        return existing_chat

    async def get_user_chat_ids(self, user_id: int) -> list[int]:
        chats = await self.chat_repository.get_user_chat_ids(user_id)

        if not chats:
            return []

        return chats

    async def update_chat(
            self,
            chat_in: ChatUpdate,
    ) -> Chat:
        redis_key = f'chat:{chat_in.chat_id}:*'
        existing_chat = await self._get_and_validate_chat_with_participants(
            chat_in.chat_id
        )
        try:
            if chat_in.name:
                existing_chat.name = chat_in.name
                await self.db.commit()
                await self.db.refresh(existing_chat, attribute_names=['name'])
                await self.redis.delete_pattern(redis_key)
                return existing_chat
        except SQLAlchemyError as db_exc:
            await self.db.rollback()
            raise DatabaseError('Failed to update chat') from db_exc
        except Exception:
            await self.db.rollback()
            raise

    async def _get_and_validate_chat_with_participants(self, chat_id: int):
        existing_chat = await self.chat_repository.get_chat_with_participants(
            chat_id
        )
        if not existing_chat:
            raise ChatValidationError('Chat not found')

        if self.current_user_id not in [
            p.user_id for p in existing_chat.participants
        ]:
            raise ChatValidationError('User not in chat')

        return existing_chat

    async def add_participants(
            self,
            chat_id : int,
            participant_ids: list[int]
    ) -> Chat:
        redis_key = f'chat:{chat_id}:*'
        existing_chat = await self._get_and_validate_chat_with_participants(
            chat_id
        )
        try:
            current_participant_ids = {
                participant.user_id for participant in
                            existing_chat.participants
            }
            new_participant_ids = list(set(participant_ids).
                                       difference(current_participant_ids))

            if new_participant_ids:
                await self.create_chat_read_statuses(
                    user_ids=new_participant_ids,
                    chat_id=existing_chat.chat_id,
                )
                users_to_add_in_db = await self.user_repository.get_by_ids(
                    new_participant_ids
                )
                for user in users_to_add_in_db:
                    existing_chat.participants.append(user)

                await self.db.commit()
                await self.db.refresh(
                    existing_chat, attribute_names=['participants']
                )
                await self.redis.delete_pattern(redis_key)

            return existing_chat
        except SQLAlchemyError as db_exc:
            await self.db.rollback()
            raise DatabaseError('Failed to add participants') from db_exc
        except Exception:
            await self.db.rollback()
            raise
