from datetime import datetime

from sqlalchemy import Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MessageDelivery(Base):
    __tablename__ = 'message_delivery'

    message_delivery_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    message_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('message.message_id', ondelete='CASCADE'),
        nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('user.user_id', ondelete='CASCADE'),
        nullable=False
    )
    chat_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('chat.chat_id', ondelete='CASCADE'),
        nullable=False
    )

    is_delivered: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_read: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    delivered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    read_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    message = relationship(
        'Message',
        back_populates='deliveries'
    )
