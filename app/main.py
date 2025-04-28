from fastapi import FastAPI, Request, status
from starlette.responses import JSONResponse

from app.api.v1 import general
from app.api.v1 import auth

from app.db.base import Base
from app.db.session import engine

import app.models as models  # noqa: F401
from app.exceptions import DuplicateEmailException, DuplicateUsernameException

app = FastAPI(
    title="Messenger API",
    description="API for the Messenger application",
    version="1.0.0",
)

api_prefix = "/api/v1"

app.include_router(general.router, prefix=api_prefix)
app.include_router(auth.router, prefix=api_prefix)


@app.exception_handler(DuplicateEmailException)
async def duplicate_email_exception_handler(
        _request: Request,
        exc: DuplicateEmailException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": f'email {exc.email} already registered.'}
    )


@app.exception_handler(DuplicateUsernameException)
async def duplicate_username_exception_handler(
        _request: Request,
        exc: DuplicateUsernameException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": f'username {exc.username} already registered.'}
    )

def create_tables():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
