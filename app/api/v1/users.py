from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_user_service
from app.models import User
from app.schemas.user import UserUpdate, UserUpdateRead, UserDelete
from app.services.user_service import UserService

router = APIRouter()


@router.get('/user')
async def get_user(
    user: User = Depends(get_current_user)
):
    return user


@router.post('/user/update', response_model=UserUpdateRead)
async def update_user(
        user_in: UserUpdate,
        user: User = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service)
):
    updated_user = await user_service.update_user(user, user_in)

    return updated_user


@router.delete('/user/delete', response_model=UserDelete)
async def delete_user(
        user: User = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service)
):
    deleted_user = user_service.soft_delete_user(user)

    return deleted_user


@router.post('/user/logout', )
async def logout_user():
    pass
