from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.token import Token
from app.schemas.user import UserCreate
from app.schemas.user import UserWithToken
from app.db.session import get_db_session
from app.services.user_service import create_new_user
from app.db.repository.user_repository import UserRepository
from app.api.deps import get_user_repository

router = APIRouter()


@router.post(
    '/register',
    response_model=UserWithToken,
    status_code=status.HTTP_201_CREATED
)
async def register(
        user_in: UserCreate,
        db: AsyncSession = Depends(get_db_session),
        user_repository: UserRepository = Depends(get_user_repository)
) -> UserWithToken:
    try:
        user_with_token = await create_new_user(
            db=db,
            user_in=user_in,
            user_repository=user_repository
        )
        return user_with_token
    except Exception as _e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(
                "Виникла внутрішня помилка сервера під час реєстрації."
                       )
        )


@router.post('/token', response_model=Token)
async def login_for_access_token(
        db: AsyncSession = Depends(get_db_session),
        form_data: OAuth2PasswordRequestForm = Depends()
):
    pass
