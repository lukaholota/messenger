from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Contact(Base):
    __tablename__ = 'contact'

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('user.user_id', ondelete='CASCADE'),
        primary_key=True
    )
    contact_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('user.user_id', ondelete='CASCADE'),
        primary_key=True
    )

    name: Mapped[str] = mapped_column(String(50), nullable=True)
