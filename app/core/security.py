from datetime import timedelta, datetime, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_ALGORITHM = settings.JWT_ALGORITHM
SECRET_KEY = settings.SECRET_KEY

def hash_password(plain_password: str) -> str:
    return password_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def create_access_token(
        data: dict,
        expires_delta: timedelta | None = None
) -> str:
    data_to_encode = data.copy()
    if expires_delta:
        expire_time = datetime.now(timezone.utc) + expires_delta
    else:
        expire_time = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    data_to_encode['exp'] = expire_time
    encoded_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str | None = payload.get('sub')
        if username is None:
            return None
        return username
    except JWTError:
        return None