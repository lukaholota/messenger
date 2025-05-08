from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repository.chat_repository import ChatRepository
from app.db.repository.user_repository import UserRepository
from app.exceptions import (
    ChatValidationError,
    UsersNotFoundError,
    DatabaseError,
)
from app.models import User, Chat
from app.schemas.chat import ChatCreate


class ChatService:
    def __init__(
            self,
            db: AsyncSession,
            chat_repository: ChatRepository,
            user_repository: UserRepository,
            current_user: User
    ):
        self.db: AsyncSession = db
        self.chat_repository = chat_repository
        self.user_repository = user_repository
        self.current_user = current_user

    async def create_chat(
            self,
            chat_in: ChatCreate,
    ):
        self._validate_chat_input(chat_in)

        users_to_add = await self._get_and_validate_participants(
            chat_in.participants_ids
        )

        await self._check_existing_private_chat(
            chat_in.is_group,
            chat_in.participants_ids
        )

        chat_name = self._determine_chat_name(chat_in, users_to_add)

        try:
            chat = await self._create_chat_in_db(
                chat_name=chat_name,
                users_to_add=users_to_add,
                is_group=chat_in.is_group,
            )
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
        if not chat_in.participants_ids:
            raise ChatValidationError("No participants in chat")
        if len(set(chat_in.participants_ids)) != len(chat_in.participants_ids):
            raise ChatValidationError("Duplicate user in one chat")
        if not chat_in.is_group and len(chat_in.participants_ids) > 2:
            raise ChatValidationError("More than two users in non group chat")
        if not chat_in.is_group and len(chat_in.participants_ids) < 2:
            raise ChatValidationError("Only one member in private chat")

    async def _get_and_validate_participants(
            self,
            participants_ids: list[int]
    ):
        users_to_add = await self.user_repository.get_by_ids(
            ids=participants_ids
        )
        if len(users_to_add) != len(participants_ids):
            found_ids = {user.user_id for user in users_to_add}
            missing_ids = set(participants_ids) - found_ids
            raise UsersNotFoundError(
                "Couldn't find users for IDs",
                missing_ids
            )

        return users_to_add

    async def _check_existing_private_chat(
            self,
            is_group: bool,
            participants_ids: list[int],
    ):
        if not is_group:
            existing_private_chat = (await self.chat_repository
                                     .get_chat_by_participants_ids(
                participants_ids
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
        await self.db.commit()
        await self.db.refresh(chat, attribute_names=['participants'])
        return chat

    async def get_chat(
            self,
            chat_id: int
    ) -> Chat:
        existing_chat = await self.chat_repository.get_chat_with_relationships(
            chat_id
        )
        if not existing_chat:
            raise ChatValidationError('Chat not found')

        if self.current_user not in existing_chat.participants:
            raise ChatValidationError('User not in chat')

        return existing_chat
