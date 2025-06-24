from datetime import datetime

from sqlalchemy import Integer, ForeignKey, String, DateTime, func, Boolean, \
    Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RefreshToken(Base):
    __tablename__ = 'refresh_token'

    refresh_token_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('user.user_id', ondelete='CASCADE'),
        nullable=False,
    )
    token_identifier: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
        unique=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)

    user = relationship('User', lazy='raise_on_sql')
