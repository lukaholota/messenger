from sqlalchemy import ForeignKey, Integer, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.chat import Chat
from app.models.user import User


class Message(Base):
    __tablename__ = 'message'

    message_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[int] = mapped_column(Integer, ForeignKey('chat.chat_id'), ondelete='CASCADE')
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.user_id'), ondelete='SET NULL')
    content: Mapped[Text] = mapped_column(Text)
    sent_at: Mapped[DateTime] = mapped_column(server_default=func.now())

    chat = relationship('Chat', back_populates='messages')
    sender = relationship('User', back_populates='messages')
