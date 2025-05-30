from typing import Callable, Coroutine, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat import Chat


async def test_create_chat(
        db_session: AsyncSession,
        chat_factory: Callable[..., Coroutine[Any, Any, Chat]],
) -> None:
    test_private_chat = await chat_factory(
        name='test_private_chat',
        is_group=False
    )

    assert test_private_chat.chat_id is not None
    assert test_private_chat.name == 'test_private_chat'
    assert test_private_chat.is_group is False

    query = select(Chat).where(Chat.chat_id == test_private_chat.chat_id)
    result = await db_session.execute(query)
    retrieved_chat = result.scalar_one_or_none()

    assert retrieved_chat is not None
    assert retrieved_chat.chat_id == test_private_chat.chat_id
    assert retrieved_chat.name == test_private_chat.name
