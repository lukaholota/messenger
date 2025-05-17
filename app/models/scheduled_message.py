from datetime import datetime

from sqlalchemy import Integer, ForeignKey, DateTime, String, func
from sqlalchemy import Enum as SQLAlchemyEnum

from app.db.base import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship

from enum import Enum


class ScheduledMessageStatus(Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    SENT = 'sent'
    FAILED = 'failed'
    CANCELED = 'canceled'


class ScheduledMessage(Base):
    __tablename__ = 'scheduled_message'

    scheduled_message_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('user.user_id'),
        nullable=False,
    )
    chat_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('chat.chat_id'),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    scheduled_send_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    status: Mapped[ScheduledMessageStatus] = mapped_column(
        SQLAlchemyEnum(
            ScheduledMessageStatus,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=ScheduledMessageStatus.PENDING,
        nullable=False,
    )
    error_message: Mapped[str] = mapped_column(
        String,
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    user = relationship('User')
    chat = relationship('Chat')
