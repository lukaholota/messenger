from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository.base import BaseRepository
from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[UserModel, UserCreate, UserUpdate]):
    async def get_by_username(
            self,
            db: AsyncSession,
            *,
            username: str
    ) -> UserModel | None:
        query = select(UserModel).where(UserModel.username == username)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        return user

    async def get_by_email(
            self,
            db: AsyncSession,
            *,
            email: str
    ) -> UserModel | None:
        query = select(UserModel).where(UserModel.email == email)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        return user

    async def get_by_username_or_email(
            self,
            db,
            *,
            email: str,
            username: str
    ) -> UserModel | None:
        query = select(UserModel).where(
            UserModel.username == username or UserModel.email == email
        )
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        return user

    async def create_with_hashed_password(
            self,
            db: AsyncSession,
            *,
            object_in: UserCreate,
            hashed_password: str,
    ) -> UserModel | None:
        object_in_data = object_in.model_dump(
            exclude={'password'},
            exclude_unset=True
        )
        db_object = self.model(
            **object_in_data,
            hashed_password=hashed_password
        )
        db.add(db_object)
        await db.commit()
        await db.refresh(db_object)
        return db_object


user_repository = UserRepository(UserModel)
