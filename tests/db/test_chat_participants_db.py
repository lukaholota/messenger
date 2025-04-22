from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Callable, Coroutine, Any
from app.models.chat import Chat
from app.models.chat_participant import ChatParticipant
from app.models.user import User


async def test_add_multiple_participants_to_group_chat(
        db_session: AsyncSession,
        user_factory: Callable[..., Coroutine[Any, Any, User]],
        chat_factory: Callable[..., Coroutine[Any, Any, Chat]],
) -> None:
    group_chat = await chat_factory(name='Group chat', is_group=True)
    assert group_chat.chat_id is not None

    user1 = await user_factory(username='user1', email='1')
    user2 = await user_factory(username='user2', email='2')
    user3 = await user_factory(username='user3', email='3')
    assert user1.user_id is not None
    assert user2.user_id is not None
    assert user3.user_id is not None

    participant1 = ChatParticipant(
        user_id=user1.user_id,
        chat_id=group_chat.chat_id
    )
    participant2 = ChatParticipant(
        user_id=user2.user_id,
        chat_id=group_chat.chat_id
    )
    participant3 = ChatParticipant(
        user_id=user3.user_id,
        chat_id=group_chat.chat_id
    )

    db_session.add_all([participant1, participant2, participant3])
    await db_session.commit()

    query = select(ChatParticipant).where(
        ChatParticipant.chat_id == group_chat.chat_id
    )
    result = await db_session.execute(query)
    participants_in_db = result.scalars().all()

    participants_ids = {participant.user_id
                        for participant in participants_in_db}

    for user in [user1, user2, user3]:
        assert user.user_id in participants_ids
