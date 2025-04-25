from sqlalchemy import ForeignKey, Integer, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base import Base


class Message(Base):
    __tablename__ = 'message'

    message_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('chat.chat_id', ondelete='CASCADE')
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey('user.user_id', ondelete='SET NULL'),
        nullable=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    chat = relationship('Chat', back_populates='messages')
    sender = relationship('User', back_populates='messages')
