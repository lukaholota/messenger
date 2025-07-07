from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter

from app.api.deps import get_user_service, \
    get_current_user_db_bound
from app.models import User
from app.schemas.user import UserUpdate, UserUpdateRead, UserDelete
from app.services.user.user_service import UserService

router = APIRouter()


@router.get('/user')
async def get_user(
    user: User = Depends(get_current_user_db_bound)
):
    return user


@router.post(
    '/user/update',
    response_model=UserUpdateRead,
    dependencies=[Depends(RateLimiter(times=4, seconds=60))],
)
async def update_user(
        user_in: UserUpdate,
        user_service: UserService = Depends(get_user_service)
):
    updated_user = await user_service.update_user(user_in)

    return updated_user


@router.delete('/user/delete', response_model=UserDelete)
async def delete_user(
        user_service: UserService = Depends(get_user_service)
):
    deleted_user = await user_service.soft_delete_user()

    return deleted_user
