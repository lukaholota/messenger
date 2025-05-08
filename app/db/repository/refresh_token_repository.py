from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_refresh_token(
            self,
            *,
            user_id: int,
            token_identifier: str,
            expires_at: datetime,
    ):
        new_refresh_token = RefreshToken(
            user_id=user_id,
            token_identifier=token_identifier,
            expires_at=expires_at,
        )
        self.db.add(new_refresh_token)
        return new_refresh_token

    async def get_by_token_identifier(self, token_identifier: str) \
            -> RefreshToken | None:
        query = select(RefreshToken).where(
            RefreshToken.token_identifier == token_identifier
        )
        result = await self.db.execute(query)
        token = result.scalar_one_or_none()
        return token

    async def revoke_token(self, token: RefreshToken):
        token.is_revoked = True
        self.db.add(token)

    async def revoke_token_by_user_id(self, user_id: int):
        query = select(RefreshToken).where(
            RefreshToken.user_id == user_id
        ).where(RefreshToken.is_revoked == False)
        result = await self.db.execute(query)
        token = result.scalar_one_or_none()
        if token:
            token.is_revoked = True
            self.db.add(token)
