from fastapi import APIRouter
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
        db_session: AsyncSession = Depends(get_db_session)
):
    query = select(User)
    result = await db_session.execute(query)
    db_users = result.scalars().all()
    return {"users": db_users}
