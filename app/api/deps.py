from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.repository.chat_repository import ChatRepository
from app.db.repository.user_repository import UserRepository
from app.db.session import get_db_session
from app.exceptions import InvalidAccessTokenException
from app.models import User, Chat
from app.services.chat_service import ChatService
from app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/token')


def get_user_repository(
        db: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    user_repository = UserRepository(db, User)
    return user_repository


def get_user_service(
        user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repository=user_repository)


async def get_current_user(
        user_repository: UserRepository = Depends(get_user_repository),
        token: str = Depends(oauth2_scheme)
) -> User:
    user_id = decode_access_token(token)
    if user_id is None:
        raise InvalidAccessTokenException
    user = await user_repository.get_by_id(user_id)
    if not user:
        raise InvalidAccessTokenException
    return user


async def get_chat_repository(
        db: AsyncSession = Depends(get_db_session),
) -> ChatRepository:
    chat_repository = ChatRepository(db, Chat)
    return chat_repository


async def get_chat_service(
        db: AsyncSession = Depends(get_db_session),
        chat_repository: ChatRepository = Depends(get_chat_repository),
        user_repository: UserRepository = Depends(get_user_repository),
) -> ChatService:
    chat_service = ChatService(
        db=db,
        chat_repository=chat_repository,
        user_repository=user_repository
    )
    return chat_service