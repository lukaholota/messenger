from datetime import datetime, timezone

from sqlalchemy import select

from app.db.repository.base import BaseRepository
from app.models import Contact
from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[UserModel, UserCreate, UserUpdate]):
    async def get_by_username(
            self,
            *,
            username: str
    ) -> UserModel | None:
        query = select(UserModel).where(UserModel.username == username)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        return user

    async def get_by_email(
            self,
            *,
            email: str
    ) -> UserModel | None:
        query = select(UserModel).where(UserModel.email == email)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        return user

    async def get_by_username_or_email(
            self,
            *,
            email: str,
            username: str
    ) -> UserModel | None:
        query = select(UserModel).where(
            UserModel.username == username or UserModel.email == email
        )
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        return user

    async def create_with_hashed_password(
            self,
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
        self.db.add(db_object)
        return db_object

    async def get_by_ids(self, ids: list[int]):
        if not ids:
            return []

        query = select(UserModel).where(
            UserModel.user_id.in_(ids)).where(
            UserModel.deleted_at.is_(None)
        ).distinct()
        result = await self.db.execute(query)
        users = result.scalars().all()
        return users

    async def soft_delete_user(self, user: UserModel):
        user.deleted_at = datetime.now(timezone.utc)
        user.display_name = 'Deleted user'

    async def search_users_raw(self, prompt: str, user_id: int):
        query = (
            select(
                UserModel.user_id,
                UserModel.username,
                UserModel.display_name,
                Contact.name.label('contact_name')
            )
            .outerjoin(
                Contact,
                (Contact.user_id==user_id) &
                (Contact.contact_id==UserModel.user_id)
            )
            .where(
                UserModel.username.like(f'%{prompt}%') | Contact.name.like(f'%{prompt}%'),
                UserModel.user_id != user_id,
                UserModel.deleted_at.is_(None)
                )
        )
        result = await self.db.execute(query)
        return result.fetchall()
