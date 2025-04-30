from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.db.repository.user_repository import UserRepository
from app.models import User
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password
from app.core.security import create_access_token
from app.exceptions import (
    DuplicateUsernameException,
    DuplicateEmailException,
    InvalidCredentialsException
)


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository: UserRepository = user_repository

    def _generate_access_token(self, user: User) -> str:
        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = create_access_token(
            data={'sub': user.user_id},
            expires_delta=access_token_expires
        )
        return access_token

    async def create_new_user_with_token(
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

        hashed_password = hash_password(user_in.password)
        new_user_model = await (
            self.user_repository.create_with_hashed_password(
            hashed_password=hashed_password,
            object_in=user_in
        )
        )
        access_token = self._generate_access_token(new_user_model)
        return new_user_model, access_token


    async def authenticate_user(
            self,
            user_in: OAuth2PasswordRequestForm,
    ):
        existing_user = await self.user_repository.get_by_username(
            username=user_in.username
        )
        if not existing_user or not verify_password(
            user_in.password,
            existing_user.hashed_password
        ):
            raise InvalidCredentialsException
        access_token = self._generate_access_token(existing_user)
        return access_token
