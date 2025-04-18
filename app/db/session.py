import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not in (.env)")

engine = create_async_engine(DATABASE_URL, echo=True, future=True)



