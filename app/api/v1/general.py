from fastapi import APIRouter

from app.api.deps import get_current_user_id

from fastapi import Depends


router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Hello World from API v1!"}


@router.get("/users")
async def users(
        current_user_id = Depends(get_current_user_id),
):
    return current_user_id
