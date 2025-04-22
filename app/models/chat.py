from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.message import Message


class Chat(Base):
    __tablename__ = 'chat'
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    is_group: Mapped[bool] = mapped_column(Boolean, default=False)

    participants: Mapped[list["User"]] = relationship(
        "User",
        secondary="ChatParticipant",
        back_populates="chats"
    )
    messages: Mapped[list["Message"]] = relationship(
        'Message',
        back_populates='chat'
    )
