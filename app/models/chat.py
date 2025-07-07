from datetime import datetime

from sqlalchemy import Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.message import Message


class Chat(Base):
    __tablename__ = 'chat'
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    is_group: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    participants: Mapped[list["User"]] = relationship(
        "User",
        secondary="chat_participant",
        back_populates="chats",
        lazy='raise_on_sql'
    )
    messages: Mapped[list["Message"]] = relationship(
        'Message',
        back_populates='chat',
        lazy='raise_on_sql'
    )
