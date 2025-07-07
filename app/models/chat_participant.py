from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, func, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class ChatParticipant(Base):
    __tablename__ = 'chat_participant'

    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.user_id', ondelete='CASCADE'),
        primary_key=True,
    )
    chat_id: Mapped[int] = mapped_column(
        ForeignKey('chat.chat_id'),
        primary_key=True
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    chat_name: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
