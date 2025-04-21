from typing import TYPE_CHECKING, Callable, Coroutine, Any

from sqlalchemy import select

from app.models.chat import Chat
from app.models.message import Message

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def test_create_chat(
        db_session: AsyncSession,
        chat_factory: Callable[..., Coroutine[Any, Any, Chat]],
        message_factory: Callable[..., Coroutine[Any, Any, Message]],
) -> None:
    test_private_chat = chat_factory(name='test_private_chat', is_group=False)

    assert test_private_chat.chat_id is not None
    assert test_private_chat.name == 'test_private_chat'
    assert test_private_chat.is_group is False

    query = select(Chat).where(Chat.chat_id == test_private_chat.chat_id)
    result = await db_session.execute(query)
    retrieved_chat = result.scalar_one_or_none()

    assert retrieved_chat is not None
    assert retrieved_chat.chat_id == test_private_chat.chat_id
    assert retrieved_chat.name == test_private_chat.name
