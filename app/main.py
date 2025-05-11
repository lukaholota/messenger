import logging
from contextlib import asynccontextmanager

import sqlalchemy
from fastapi import FastAPI, Request
from jose import JWTError
from starlette.responses import JSONResponse
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE, HTTP_409_CONFLICT, \
    HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from app.api.v1 import general
from app.api.v1 import auth
from app.api.v1 import chats
from app.api.v1 import messages
from app.api.v1 import users

from app.db.base import Base
from app.db.session import engine
from app.redis.connection import add_redis_client_to_app_state

import app.models as models  # noqa: F401
from app.exceptions import (
    DuplicateEmailException, DuplicateUsernameException,
    InvalidCredentialsException, ChatValidationError, UsersNotFoundError,
    DatabaseError, MessageValidationError, InvalidTokenCredentialsException,
    UserDeleteError
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Connecting to Redis...")
    await add_redis_client_to_app_state(app)

    yield

    logger.info("Disconnecting from Redis...")
    if (
            hasattr(app.state, 'redis_client') and
            app.state.redis_client is not None
    ):
        app.state.redis_client.close()
        logger.info("Disconnected from Redis")

app = FastAPI(
    title="Messenger API",
    description="API for the Messenger application",
    version="1.0.0",
    lifespan=lifespan,
)

api_prefix = "/api/v1"

app.include_router(general.router, prefix=api_prefix)
app.include_router(auth.router, prefix=api_prefix)
app.include_router(chats.router, prefix=api_prefix)
app.include_router(messages.router, prefix=api_prefix)
app.include_router(users.router, prefix=api_prefix)


def create_tables():
    Base.metadata.create_all(bind=engine)


@app.exception_handler(DatabaseError)
def database_error_handler(
        _request: Request,
        exc: DatabaseError,
):
    logger.error(f"Database error: {exc}", exc_info=exc)
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": exc.detail},
    )


@app.exception_handler(DuplicateEmailException)
def duplicate_email_exception_handler(
        _request: Request,
        exc: DuplicateEmailException
):
    logger.error(f"Duplicate email exception: {exc}", exc_info=exc)
    return JSONResponse(
        status_code=HTTP_409_CONFLICT,
        content={"detail": exc.detail}
    )


@app.exception_handler(DuplicateUsernameException)
def duplicate_username_exception_handler(
        _request: Request,
        exc: DuplicateUsernameException
):
    logger.error(f"Duplicate username exception: {exc}", exc_info=exc)
    return JSONResponse(
        status_code=HTTP_409_CONFLICT,
        content={"detail": exc.detail}
    )


@app.exception_handler(InvalidCredentialsException)
def invalid_credentials_exception_handler(
        _request: Request,
        exc: InvalidCredentialsException
):
    logger.error(f"invalid credentials exception: {exc}", exc_info=exc)
    return JSONResponse(
        status_code=HTTP_401_UNAUTHORIZED,
        content={"detail": exc.detail}
    )


@app.exception_handler(InvalidTokenCredentialsException)
def invalid_token_credentials_exception_handler(
        _request: Request,
        exc: InvalidTokenCredentialsException
):
    logger.error(
    f"invalid token credentials exception: {exc}",
        exc_info=exc
    )
    return JSONResponse(
        status_code=HTTP_401_UNAUTHORIZED,
        content={"detail": exc.detail}
    )


@app.exception_handler(ChatValidationError)
def chat_validation_error_handler(
        _request: Request,
        exc: ChatValidationError
):
    logger.error(f"Chat validation exception: {exc}", exc_info=exc)
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={"detail": exc.detail}
    )


@app.exception_handler(UsersNotFoundError)
def users_not_found_error_handler(
        _request: Request,
        exc: UsersNotFoundError
):
    logger.error(f"Couldn't find users by IDS: {exc}, "
                 f"missing IDs: {exc.missing_ids}", exc_info=exc)
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={"detail": exc.detail}
    )

@app.exception_handler(UserDeleteError)
def user_delete_error_handler(
        _request: Request,
        exc: UserDeleteError
):
    logger.error(f'delete error: {exc}', exc_info=exc)
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": exc.detail}
    )


@app.exception_handler(MessageValidationError)
def message_validation_error_handler(
        _request: Request,
        exc: MessageValidationError
):
    logger.error(f"Message validation error: {exc}", exc_info=exc)
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={"detail": exc.detail}
    )


@app.exception_handler(sqlalchemy.exc.OperationalError)
async def db_connection_exception_handler(
        _request: Request,
        exc: sqlalchemy.exc.OperationalError
) -> JSONResponse:
    logger.error(f"Database connection exception: {exc}", exc_info=exc)
    return JSONResponse(
        status_code=HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Database service is temporarily unavailable"}
    )


@app.exception_handler(sqlalchemy.exc.IntegrityError)
def integrity_error_handler(
        _request: Request,
        exc: sqlalchemy.exc.IntegrityError
):
    logger.error(f"Integrity exception: {exc}", exc_info=exc)
    return JSONResponse(
        status_code=HTTP_409_CONFLICT,
        content={"detail": "Resource already exists or "
                           "violates integrity constraint"}
    )


@app.exception_handler(JWTError)
def jwt_error_handler(
        _request: Request,
        exc: JWTError
):
    logger.error(f"JWT error: {exc}", exc_info=exc)
    return JSONResponse(
        status_code=HTTP_401_UNAUTHORIZED,
        content={"detail": "Access token expired"}
    )


@app.exception_handler(Exception)
def generic_exception_handler(
        _request: Request,
        exc: Exception
):
    logger.exception(f"Generic exception occurred: {exc}", exc_info=exc)
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred"}
    )

if __name__ == "__main__":
    create_tables()
