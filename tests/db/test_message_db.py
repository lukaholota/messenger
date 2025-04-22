from typing import Callable, Coroutine, Any

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import Chat
from app.models.message import Message
from app.models.user import User

pytestmark = pytest.mark.asyncio


async def test_create_message_with_user_in_private_chat(
        db_session: AsyncSession,
        user_factory: Callable[..., Coroutine[Any, Any, User]],
        chat_factory: Callable[..., Coroutine[Any, Any, Chat]],
        message_factory: Callable[..., Coroutine[Any, Any, Message]],
) -> None:
    test_private_chat = await chat_factory(
        name='private_test_chat',
        is_group=False
    )
    assert test_private_chat.chat_id is not None
    assert test_private_chat.name == 'private_test_chat'

    test_user = user_factory(name='test', email='<EMAIL>')
    assert test_user.user_id is not None
    assert test_user.username == 'test'

    message_text = 'test_message_text'
    new_message = message_factory(
        chat=test_private_chat,
        sender=test_user,
        content=message_text
    )

    assert new_message.chat_id is not None
    assert new_message.user_id == test_user.user_id
    assert new_message.content == message_text
    assert new_message.sender == test_user
    assert new_message.sent_at is not None

    query = select(Message).where(
        Message.message_id == new_message.message_id
    )
    result = await db_session.execute(query)
    retrieved_message = result.scalar_one_or_none()

    assert retrieved_message is not None
    assert retrieved_message.message_id == new_message.message_id
    assert retrieved_message.content == new_message.content
    assert retrieved_message.sender == test_user
