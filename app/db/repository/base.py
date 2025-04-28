from typing import Generic, Any, TypeVar, List, Dict, Type
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import inspect, select
from app.db.base import Base


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType =  TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
        self._primary_key_name = inspect(model).primary_key[0].name

    async def get_by_id(self, db: AsyncSession, id: Any) -> ModelType | None:
        query = select(self.model).where(
            getattr(self.model, self._primary_key_name) == id
        )
        result = await db.execute(query)
        return result.scalar().one()

    async def get_multi(
            self,
            db: AsyncSession,
            *,
            skip: int = 0,
            limit: int = 100
    ):
        query = select(self.model).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def create(
            self,
            db:
            AsyncSession,
            *,
            object_in: CreateSchemaType
    ) -> ModelType:
        object_in_data = object_in.model_dump(exclude_unset=True)
        db_object = self.model(**object_in_data)
        db.add(db_object)
        await db.commit()
        await db.refresh(db_object)
        return db_object

    async def update(
            self,
            db: AsyncSession,
            *,
            db_object: ModelType,
            object_in: UpdateSchemaType | Dict[str, Any]
    ) -> ModelType:
        db_object_data = db_object.__dict__
        if isinstance(object_in, dict):
            update_data = object_in
        else:
            update_data = object_in.model_dump(exclude_unset=True)
        for field in db_object_data:
            if field in update_data:
                setattr(db_object, field, update_data[field])

        db.add(db_object)
        await db.commit()
        await db.refresh(db_object)
        return db_object

    async def delete(
            self,
            db: AsyncSession,
            *,
            id: Any
    ) -> bool:
        object = await self.get_by_id(db, id)
        if object:
            await db.delete(object)
            await db.commit()
            return True
        return False
