import uuid

from datetime import timedelta, datetime, timezone

from jose import jwt, ExpiredSignatureError
from passlib.context import CryptContext
from app.core.config import settings
from app.exceptions import InvalidTokenCredentialsException
from app.schemas.token import TokenPayload, CreatedTokenInfo

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_ALGORITHM = settings.JWT_ALGORITHM
SECRET_KEY = settings.SECRET_KEY

def hash_password(plain_password: str) -> str:
    return password_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password) -> bool:
    return password_context.verify(plain_password, hashed_password)


def create_jwt_token(
        *,
        data: dict,
        expires_delta: timedelta,
        token_type: str,
) -> CreatedTokenInfo:
    data_to_encode = data.copy()
    expire_time = datetime.now(timezone.utc) + expires_delta
    jti = str(uuid.uuid4())
    data_to_encode.update({
        'exp': expire_time,
        'type': token_type,
        'jti': jti,
    })
    encoded_jwt = jwt.encode(
        data_to_encode,
        SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )
    return CreatedTokenInfo(
        token=encoded_jwt,
        expires_at=expire_time,
        jti=jti
    )


def decode_jwt_token(token: str) -> TokenPayload | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str | None = payload.get('sub')
        token_type: str | None = payload.get('type')
        jti: str | None = payload.get('jti')
        expires_at: str | None = payload.get('exp')
        if not user_id or not token_type:
            raise InvalidTokenCredentialsException
        token_data = TokenPayload(
            user_id=user_id,
            token_type=token_type,
            jti=jti,
            expires_at=expires_at
        )
        return token_data
    except ExpiredSignatureError:
        raise
    except Exception as e:
        raise e
