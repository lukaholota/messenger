from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class ChatParticipant(Base):
    __tablename__ = 'chat_participant'

    user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey('chat.chat_id'), primary_key=True)
