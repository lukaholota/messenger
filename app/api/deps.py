from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_jwt_token
from app.db.repository.chat_repository import ChatRepository
from app.db.repository.message_repository import MessageRepository
from app.db.repository.refresh_token_repository import RefreshTokenRepository
from app.db.repository.user_repository import UserRepository
from app.db.session import get_db_session
from app.exceptions import InvalidAccessTokenException, DeletedUserError
from app.models import User, Chat, Message
from app.services.auth_service import AuthService
from app.services.chat_service import ChatService
from app.services.message_service import MessageService
from app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/token')


def get_user_repository(
        db: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    user_repository = UserRepository(db, User)
    return user_repository


async def get_chat_repository(
        db: AsyncSession = Depends(get_db_session),
) -> ChatRepository:
    chat_repository = ChatRepository(db, Chat)
    return chat_repository


async def get_message_repository(
        db: AsyncSession = Depends(get_db_session)
) -> MessageRepository:
    message_repository = MessageRepository(db, Message)
    return message_repository


async def get_refresh_token_repository(
        db: AsyncSession = Depends(get_db_session)
) -> RefreshTokenRepository:
    refresh_token_repository = RefreshTokenRepository(db)
    return refresh_token_repository


def get_user_service(
        db: AsyncSession = Depends(get_db_session),
        user_repository: UserRepository = Depends(get_user_repository),
        chat_repository: ChatRepository = Depends(get_chat_repository),
        refresh_token_repository: RefreshTokenRepository = (
                Depends(get_refresh_token_repository)
        ),
) -> UserService:
    return UserService(
        db=db,
        user_repository=user_repository,
        chat_repository=chat_repository,
        refresh_token_repository=refresh_token_repository
    )


async def get_current_user(
        user_repository: UserRepository = Depends(get_user_repository),
        token: str = Depends(oauth2_scheme)
) -> User:
    token_data = decode_jwt_token(token)
    if not token_data.user_id or not token_data.token_type:
        raise InvalidAccessTokenException
    user = await user_repository.get_by_id(token_data.user_id)
    if not user:
        raise InvalidAccessTokenException
    if user.deleted_at:
        raise DeletedUserError
    return user





async def get_chat_service(
        db: AsyncSession = Depends(get_db_session),
        chat_repository: ChatRepository = Depends(get_chat_repository),
        user_repository: UserRepository = Depends(get_user_repository),
        current_user: User = Depends(get_current_user)
) -> ChatService:
    chat_service = ChatService(
        db=db,
        chat_repository=chat_repository,
        user_repository=user_repository,
        current_user=current_user
    )
    return chat_service





async def get_message_service(
        db: AsyncSession = Depends(get_db_session),
        message_repository = Depends(get_message_repository),
        user_repository: UserRepository = Depends(get_user_repository),
        chat_repository: ChatRepository = Depends(get_chat_repository),
        current_user: User = Depends(get_current_user)
) -> MessageService:
    message_service = MessageService(
        db,
        message_repository=message_repository,
        user_repository=user_repository,
        chat_repository=chat_repository,
        current_user=current_user
    )
    return message_service


async def get_auth_service(
        db: AsyncSession = Depends(get_db_session),
        refresh_token_repository: RefreshTokenRepository =
        Depends(get_refresh_token_repository)
) -> AuthService:
    auth_service = AuthService(
        db=db,
        refresh_token_repository=refresh_token_repository
    )
    return auth_service
