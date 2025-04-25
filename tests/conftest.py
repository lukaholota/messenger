import os
import asyncio
from typing import AsyncGenerator, Generator, Callable, Coroutine, Any

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (AsyncSession, create_async_engine,
                                    async_sessionmaker)
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.base import Base
from app.models.user import User
from app.models.chat import Chat
from app.models.message import Message

TEST_DATABASE_URL = os.getenv('TEST_DATABASE_URL')
if not TEST_DATABASE_URL:
    print("WARNING: TEST_DATABASE_URL environment variable "
          "not set. Constructing from TEST_DB_... vars.")
    TEST_DB_USER = os.getenv("TEST_DB_USER", "test_user")
    TEST_DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", "test_password")
    TEST_DB_NAME = os.getenv("TEST_DB_NAME", "messenger_test_db")
    TEST_DB_HOST = os.getenv("TEST_DB_HOST", "127.0.0.1")
    TEST_DB_PORT = os.getenv("TEST_DB_PORT", "3306")
    TEST_DATABASE_URL = (f"mysql+aiomysql://{TEST_DB_USER}:{TEST_DB_PASSWORD}"
                         f"@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"
                         f"?charset=utf8mb4")


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def async_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
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


@pytest_asyncio.fixture(scope='function')
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(
            transport=transport,
            base_url='http://test'
    ) as client:
        yield client


@pytest_asyncio.fixture
async def user_factory(db_session: AsyncSession) -> (
        Callable)[..., Coroutine[Any, Any, User]]:
    async def _create_user(
            username: str,
            email: str,
            hashed_password: str = 'testpassword',
            display_name: str = '',
    ) -> User:
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
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
    async def _create_chat(is_group: bool, name: str = 'name') -> Chat:
        new_chat = Chat(name=name, is_group=is_group)
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
        new_message = Message(
            chat_id=chat.chat_id,
            user_id=sender.user_id,
            content=content
        )
        db_session.add(new_message)
        await db_session.commit()
        await db_session.refresh(new_message)
        return new_message
    return _create_message
