from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.token import Token
from app.schemas.user import UserCreate, UserRead
from app.schemas.user import UserWithToken
from app.services.user_service import UserService
from app.api.deps import get_user_service

router = APIRouter()


@router.post(
    '/register',
    response_model=UserWithToken,
    status_code=status.HTTP_201_CREATED
)
async def register_user(
        user_in: UserCreate,
        user_service: UserService = Depends(get_user_service)
) -> UserWithToken:
    new_user_model, access_token = await (
        user_service.create_new_user_with_token(
        user_in=user_in,
    ))
    response_user = UserRead.model_validate(new_user_model)
    response_token = Token(access_token=access_token, token_type='bearer')
    user_with_token = UserWithToken(user=response_user,
                                    token=response_token)
    return user_with_token

@router.post('/token', response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        user_service: UserService = Depends(get_user_service)
):
    access_token = await user_service.authenticate_user(form_data)
    return Token(access_token=access_token, token_type='bearer')
