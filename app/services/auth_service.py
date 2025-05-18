from datetime import datetime, timedelta
from logging import getLogger

from fastapi import HTTPException
from jose import ExpiredSignatureError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_jwt_token, decode_jwt_token
from app.db.repository.refresh_token_repository import RefreshTokenRepository
from app.exceptions import InvalidTokenCredentialsException
from app.models.refresh_token import RefreshToken
from app.schemas.token import TokenPairInfo, TokenPayload
from app.services.cache_token_blacklist_service import \
    CacheTokenBlacklistService

logger = getLogger(__name__)


class AuthService:
    def __init__(
            self,
            *,
            db: AsyncSession,
            refresh_token_repository: RefreshTokenRepository,
            cache_token_blacklist_service: CacheTokenBlacklistService
    ):
        self.db = db
        self.refresh_token_repository = refresh_token_repository
        self.cache_token_blacklist_service = cache_token_blacklist_service

    async def get_refresh_token_payload(self, refresh_token: str) -> (
            TokenPayload):
        try:
            token_payload = decode_jwt_token(refresh_token)
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=403,
                detail="Refresh token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if token_payload.token_type != 'refresh':
            raise InvalidTokenCredentialsException

        return token_payload

    async def get_refresh_token_from_db(self, token_identifier: str) \
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

    async def logout(
            self,
            *,
            refresh_token_payload: TokenPayload,
            access_token_payload: TokenPayload,
    ):
        try:
            await (self.refresh_token_repository.
                    revoke_token_by_identifier_and_user_id(
                        refresh_token_payload.jti,
                        int(access_token_payload.user_id)
            ))
            await self.db.commit()

            await self.cache_token_blacklist_service.add_to_blacklist(
                token_identifier=access_token_payload.jti,
                original_expiration_timestamp=access_token_payload.expires_at
            )
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"SQLAlchemyError: {e}", exc_info=e)
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=e)
            raise
