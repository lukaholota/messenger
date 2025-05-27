from jose import ExpiredSignatureError
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

from app.core.config import settings
from app.core.security import decode_jwt_token
from app.infrastructure.exceptions.exceptions import InvalidAccessTokenException

EXCLUDED_PATHS = {
    f'{settings.API_V1_STR}/token',
    f'{settings.API_V1_STR}/register',
    f'{settings.API_V1_STR}/auth/refresh',
}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)

        auth_header = request.headers.get('Authorization')

        if not auth_header:
            raise InvalidAccessTokenException

        token = auth_header.removeprefix('Bearer ').strip()

        try:
            token_data = decode_jwt_token(token)
        except ExpiredSignatureError:
            raise
        except Exception as e:
            raise InvalidAccessTokenException from e

        request.state.token_payload = token_data
        request.state.user_id = int(token_data.user_id)

        return await call_next(request)
