from datetime import datetime, timedelta

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_jwt_token
from app.db.repository.refresh_token_repository import RefreshTokenRepository
from app.exceptions import InvalidTokenCredentialsException
from app.models.refresh_token import RefreshToken
from app.schemas.token import TokenPairInfo


class AuthService:
    def __init__(
            self,
            *,
            db: AsyncSession,
            refresh_token_repository: RefreshTokenRepository,
    ):
        self.db = db
        self.refresh_token_repository = refresh_token_repository

    async def validate_refresh_token(self, token_identifier: str)\
            -> RefreshToken:
        token = await self.refresh_token_repository.get_by_token_identifier(
            token_identifier
        )
        if not token or token.is_revoked:
            raise InvalidTokenCredentialsException
        return token

    async def save_refresh_token(
            self,
            *,
            token_identifier: str,
            user_id: int,
            expires_at: datetime
    ) -> RefreshToken | None:
        new_refresh_token = await (self.refresh_token_repository.
        create_refresh_token(
            token_identifier=token_identifier,
            user_id=user_id,
            expires_at=expires_at
        ))
        await self.db.commit()
        return new_refresh_token

    async def revoke_token(self, token: RefreshToken):
        try:
            await self.refresh_token_repository.revoke_token(token)
            await self.db.commit()
        except SQLAlchemyError:
            raise

    def create_access_and_refresh_tokens(self, user_id) -> TokenPairInfo:
        payload_data = {'sub': str(user_id)}
        access_token_expires_delta = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token_info = create_jwt_token(
            data=payload_data,
            expires_delta=access_token_expires_delta,
            token_type='access'
        )

        refresh_token_expires_delta = timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        refresh_token_info = create_jwt_token(
            data=payload_data,
            expires_delta=refresh_token_expires_delta,
            token_type='refresh'
        )

        return TokenPairInfo(
            access_token_info=access_token_info,
            refresh_token_info=refresh_token_info,
        )
