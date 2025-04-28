from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository.user_repository import UserRepository
from app.schemas.user import UserCreate, UserRead, UserWithToken
from app.schemas.token import Token
from app.core.security import hash_password
from app.core.security import create_access_token
from app.exceptions import DuplicateUsernameException, DuplicateEmailException


async def create_new_user(
        user_in: UserCreate,
        db: AsyncSession,
        user_repository: UserRepository
):
    existing_user = await user_repository.get_by_username_or_email(
        db=db,
        username=user_in.username,
        email=user_in.email
    )
    if existing_user:
        if existing_user.username == user_in.username:
            raise DuplicateUsernameException
        elif existing_user.email == user_in.email:
            raise DuplicateEmailException


    hashed_password = hash_password(user_in.password)
    new_user_model = await user_repository.create_with_hashed_password(
        db,
        hashed_password=hashed_password,
        object_in=user_in
    )

    access_token = create_access_token(
        data={'sub': new_user_model.username}
    )

    response_user = UserRead.model_validate(new_user_model)
    response_token = Token(access_token=access_token, token_type='bearer')
    response = UserWithToken(user=response_user, token=response_token)

    return response
