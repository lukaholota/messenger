from typing import Generic, Any, TypeVar, List, Dict, Type
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import inspect, select
from app.db.base import Base


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType =  TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, db: AsyncSession, model: Type[ModelType]):
        self.model = model
        self._primary_key_name = inspect(model).primary_key[0].name
        self.db = db

    async def get_by_id(self, id: Any) -> ModelType | None:
        query = select(self.model).where(
            getattr(self.model, self._primary_key_name) == id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
            self,
            *,
            skip: int = 0,
            limit: int = 100
    ):
        query = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(
            self,
            *,
            object_in: CreateSchemaType
    ) -> ModelType:
        object_in_data = object_in.model_dump(exclude_unset=True)
        db_object = self.model(**object_in_data)
        self.db.add(db_object)
        await self.db.commit()
        await self.db.refresh(db_object)
        return db_object

    async def update(
            self,
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

        self.db.add(db_object)
        await self.db.commit()
        await self.db.refresh(db_object)
        return db_object

    async def delete(
            self,
            *,
            id: Any
    ) -> bool:
        object = await self.get_by_id(id)
        if object:
            await self.db.delete(object)
            await self.db.commit()
            return True
        return False
