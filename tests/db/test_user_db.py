import pytest
from typing import Callable, Coroutine, Any
from sqlalchemy import select
from app.models.user import User

from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio


async def test_create_and_get_user(
        db_session: AsyncSession,
        user_factory: Callable[..., Coroutine[Any, Any, User]]
) -> None:
    test_user = await user_factory(
        username="test",
        email="test@test.io",
        hashed_password='testpassword',
        display_name='display_name_test'
    )
    assert test_user.user_id is not None
    assert test_user.username == 'test'
    assert test_user.email == 'test@test.io'
    assert test_user.hashed_password == 'testpassword'
    assert test_user.display_name == 'display_name_test'

    query = select(User).where(User.username == test_user.username)
    result = await db_session.execute(query)
    retrieved_user = result.scalar_one_or_none()

    assert retrieved_user is not None
    assert retrieved_user.user_id == test_user.user_id
    assert retrieved_user.username == test_user.username
    assert retrieved_user.email == test_user.email
    assert retrieved_user.hashed_password == test_user.hashed_password
