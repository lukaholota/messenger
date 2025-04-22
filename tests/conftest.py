import os
import asyncio
from typing import AsyncGenerator, Generator, Callable, Coroutine, Any

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (AsyncSession, create_async_engine,
                                    async_sessionmaker)
from sqlalchemy.pool import NullPool

from app.db.base import Base
from app.models.chat import Chat
from app.models.message import Message
from app.models.user import User

DATABASE_URL = os.getenv('DATABASE_URL', None)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def async_engine():
    engine = create_async_engine(DATABASE_URL, pool_class=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope='function')
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    connection = await async_engine.connect()
    transaction = await connection.begin()
    async_session_factory = async_sessionmaker(
        bind=connection,
        expire_on_commit=False,
        class_=AsyncSession
    )
    session = async_session_factory()

    try:
        yield session
    finally:
        await session.close()
        if transaction.is_active:
            await transaction.rollback()
        await connection.close()


@pytest_asyncio.fixture
async def user_factory(db_session: AsyncSession) -> (
        Callable)[..., Coroutine[Any, Any, User]]:
    async def _create_user(
            username: str,
            email: str,
            password: str = 'testpassword',
            display_name: str = '',
    ) -> User:
        new_user = User(
            username=username,
            email=email,
            password=password,
            display_name=display_name
        )
        db_session.add(new_user)
        await db_session.commit()
        await db_session.refresh(new_user)
        return new_user
    return _create_user


@pytest_asyncio.fixture
async def chat_factory(db_session: AsyncSession) -> (
        Callable)[..., Coroutine[Any, Any, Chat]]:
    async def _create_chat(is_group: bool) -> Chat:
        new_chat = Chat(name='test', is_group=is_group)
        db_session.add(new_chat)
        await db_session.commit()
        await db_session.refresh(new_chat)
        return new_chat
    return _create_chat


@pytest_asyncio.fixture
async def message_factory(db_session: AsyncSession) -> (
        Callable)[..., Coroutine[Any, Any, Message]]:
    async def _create_message(
            sender: User,
            chat: Chat,
            content: str
    ) -> Message:
        new_message = Message(chat=chat, sender=sender, content=content)
        db_session.add(new_message)
        await db_session.commit()
        await db_session.refresh(new_message)
        return new_message
    return _create_message
