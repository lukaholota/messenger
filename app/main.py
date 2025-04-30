from fastapi import FastAPI, Request, HTTPException
from starlette.responses import JSONResponse

from app.api.v1 import general
from app.api.v1 import auth

from app.db.base import Base
from app.db.session import engine

import app.models as models  # noqa: F401


app = FastAPI(
    title="Messenger API",
    description="API for the Messenger application",
    version="1.0.0",
)

api_prefix = "/api/v1"

app.include_router(general.router, prefix=api_prefix)
app.include_router(auth.router, prefix=api_prefix)


def create_tables():
    Base.metadata.create_all(bind=engine)


@app.exception_handler(Exception)
def base_exception_handle_except_http(_request: Request, exc):
    if isinstance(exc, HTTPException):
        raise exc
    return JSONResponse(
        status_code=500,
        content={"messsage": '500 womp womp'},
    )

if __name__ == "__main__":
    create_tables()
