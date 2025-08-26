from datetime import datetime

from sqlalchemy import Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ChatReadStatus(Base):
    __tablename__ = 'chat_read_status'

    last_read_message_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('message.message_id', ondelete='CASCADE'),
        nullable=True,
        default=None
    )
    chat_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('chat.chat_id', ondelete='CASCADE'),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('user.user_id', ondelete='CASCADE'),
        primary_key=True,
    )
    read_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        server_onupdate=func.now()
    )
