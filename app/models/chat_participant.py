from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class ChatParticipant(Base):
    __tablename__ = 'chat_participant'

    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.user_id', ondelete='SET_NULL'),
        primary_key=True,
        nullable=True
    )
    chat_id: Mapped[int] = mapped_column(
        ForeignKey('chat.chat_id'),
        primary_key=True
    )
