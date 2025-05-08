from fastapi import APIRouter

from app.api.deps import get_current_user
from app.models import User
from sqlalchemy import select
from fastapi import Depends
from app.db.session import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Hello World from API v1!"}


@router.get("/users")
async def users(
        db: AsyncSession = Depends(get_db_session),
        user = Depends(get_current_user),
):
    return user.user_id
    query = select(User)
    result = await db.execute(query)
    db_users = result.scalars().all()
    return {"users": db_users}
