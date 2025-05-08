from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.chat import Chat
    from app.models.message import Message


class User(Base):
    __tablename__ = 'user'

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    display_name: Mapped[str] = mapped_column(String(50), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )
    deleted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=None
    )

    chats: Mapped[list["Chat"]] = relationship(
        "Chat",
        secondary="chat_participant",
        back_populates="participants",
        lazy='raise_on_sql'
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="sender",
        lazy='raise_on_sql'
    )
