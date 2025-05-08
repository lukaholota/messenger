from fastapi import APIRouter, Depends, status, Body, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import ExpiredSignatureError

from app.core.security import decode_jwt_token
from app.exceptions import InvalidTokenCredentialsException, \
    DeletedUserServiceError, DeletedUserError
from app.schemas.token import TokenRead, TokenPairInfo
from app.schemas.user import UserCreate, UserRead
from app.schemas.user import UserWithToken
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.api.deps import get_user_service, get_auth_service

router = APIRouter()


@router.post(
    '/register',
    response_model=UserWithToken,
    status_code=status.HTTP_201_CREATED
)
async def register_user(
        user_in: UserCreate,
        user_service: UserService = Depends(get_user_service),
        auth_service: AuthService = Depends(get_auth_service)
) -> UserWithToken:
    new_user_model = await (
        user_service.create_new_user(
        user_in=user_in,
    ))
    token_pair_info: TokenPairInfo = (
        auth_service.create_access_and_refresh_tokens(new_user_model.user_id)
    )

    await auth_service.save_refresh_token(
        user_id=new_user_model.user_id,
        token_identifier=token_pair_info.refresh_token_info.jti,
        expires_at=token_pair_info.refresh_token_info.expires_at,
    )

    response_user = UserRead.model_validate(new_user_model)
    response_token = TokenRead(
        access_token=token_pair_info.access_token_info.token,
        refresh_token=token_pair_info.refresh_token_info.token,
        token_type='bearer'
    )
    user_with_token = UserWithToken(
        user=response_user,
        token=response_token
    )
    return user_with_token

@router.post('/token', response_model=TokenRead)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        user_service: UserService = Depends(get_user_service),
        auth_service: AuthService = Depends(get_auth_service)
):
    try:
        user = await user_service.authenticate_user(form_data)
    except DeletedUserServiceError:
        raise DeletedUserError

    token_pair_info: TokenPairInfo = (
        auth_service.create_access_and_refresh_tokens(user.user_id)
    )

    await auth_service.save_refresh_token(
        token_identifier=token_pair_info.refresh_token_info.jti,
        user_id=user.user_id,
        expires_at=token_pair_info.refresh_token_info.expires_at,
    )

    return {
        'access_token': token_pair_info.access_token_info.token,
        'refresh_token': token_pair_info.refresh_token_info.token,
        'token_type': 'bearer'
    }


@router.post('/auth/refresh', response_model=TokenRead)
async def make_token_rotation(
        refresh_token: str = Body(..., embed=True),
        auth_service: AuthService = Depends(get_auth_service),
        user_service: UserService = Depends(get_user_service)
):
    try:
        token_payload = decode_jwt_token(refresh_token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=403,
            detail="Refresh token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if token_payload.token_type != 'refresh':
        raise InvalidTokenCredentialsException

    refresh_token_in_db = await auth_service.validate_refresh_token(
        token_identifier=token_payload.jti
    )

    await user_service.check_user_exists_by_id(refresh_token_in_db.user_id)

    await auth_service.revoke_token(refresh_token_in_db)

    token_pair_info: TokenPairInfo = (
        auth_service.create_access_and_refresh_tokens(
            refresh_token_in_db.user_id
        )
    )

    await auth_service.save_refresh_token(
        user_id=refresh_token_in_db.user_id,
        token_identifier=token_pair_info.refresh_token_info.jti,
        expires_at=token_pair_info.refresh_token_info.expires_at,
    )
    return {
        'access_token': token_pair_info.access_token_info.token,
        'refresh_token': token_pair_info.refresh_token_info.token,
        'token_type': 'bearer'
    }
