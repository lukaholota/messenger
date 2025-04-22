from fastapi import FastAPI

from app.api.v1 import general

from app.db.base import Base
from app.db.session import engine

app = FastAPI(
    title="Messenger API",
    description="API for the Messenger application",
    version="1.0.0",
)

api_prefix = "/api/v1"

app.include_router(general.router, prefix=api_prefix)


def create_tables():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
