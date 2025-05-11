import logging

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository.chat_repository import ChatRepository
from app.db.repository.refresh_token_repository import RefreshTokenRepository
from app.db.repository.user_repository import UserRepository
from app.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password, verify_password
from app.exceptions import (
    DuplicateUsernameException,
    DuplicateEmailException,
    InvalidCredentialsException,
    UserNotFoundError,
    DeletedUserServiceError,
    UserDeleteError
)

logger = logging.getLogger(__name__)


class UserService:
    def __init__(
            self,
            db: AsyncSession,
            user_repository: UserRepository,
            chat_repository: ChatRepository | None,
            refresh_token_repository: RefreshTokenRepository | None,
            current_user: User | None,
    ):
        self.db: AsyncSession = db
        self.user_repository: UserRepository = user_repository
        self.chat_repository: ChatRepository | None = chat_repository
        self.refresh_token_repository: RefreshTokenRepository | None = (
            refresh_token_repository
        )
        self.current_user: User | None = current_user

    async def create_new_user(
            self,
            user_in: UserCreate,
    ):
        existing_user = await self.user_repository.get_by_username_or_email(
            username=user_in.username,
            email=user_in.email
        )
        if existing_user:
            if existing_user.username == user_in.username:
                raise DuplicateUsernameException(username=user_in.username)
            elif existing_user.email == user_in.email:
                raise DuplicateEmailException(email=user_in.email)

        if not user_in.display_name:
            user_in.display_name = user_in.username

        hashed_password = hash_password(user_in.password)
        new_user_model = await (
            self.user_repository.create_with_hashed_password(
            hashed_password=hashed_password,
            object_in=user_in
        )
        )
        await self.db.commit()
        await self.db.refresh(new_user_model)

        return new_user_model

    async def authenticate_user(
            self,
            user_in: OAuth2PasswordRequestForm,
    ):
        existing_user = await self.user_repository.get_by_username(
            username=user_in.username
        )
        if existing_user.deleted_at:
            raise DeletedUserServiceError
        if not existing_user or not verify_password(
            user_in.password,
            existing_user.hashed_password
        ):
            raise InvalidCredentialsException
        return existing_user

    async def check_user_exists_by_id(self, user_id):
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError('User is not found')
        return user

    async def update_user(
            self,
            user_in: UserUpdate,
    ) -> User:
        update_data = user_in.model_dump(exclude_unset=True)
        if not update_data:
            return self.current_user

        for key, value in update_data.items():
            if hasattr(self.current_user, key):
                setattr(self.current_user, key, value)
            else:
                logger.warning(f"trying to set value '{value}' "
                               f"to nonexistant attribute '{key}'")

        try:
            await self.db.commit()
            await self.db.refresh(self.current_user)
            return self.current_user
        except IntegrityError:
            await self.db.rollback()

            raise InvalidCredentialsException(
                'username or email already taken'
            )

    async def soft_delete_user(self) -> User:
        try:
            delete_stmt = await (
                self.chat_repository.delete_user_from_group_chats(self.current_user.user_id)
            )
            await self.db.execute(delete_stmt)

            await self.refresh_token_repository.revoke_tokens_by_user_id(
                self.current_user.user_id
            )

            await self.user_repository.soft_delete_user(self.current_user)

            await self.db.commit()
            await self.db.refresh(self.current_user)

            return self.current_user
        except IntegrityError as e:
            await self.db.rollback()
            raise UserDeleteError('integrity error') from e
        except OperationalError as e:
            await self.db.rollback()
            raise UserDeleteError('database operational error') from e
        except Exception as e:
            await self.db.rollback()
            raise UserDeleteError('Unexpected error') from e
