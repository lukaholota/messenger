from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    MYSQL_HOST: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str

    DATABASE_URL: str | None = None

    SQLALCHEMY_ECHO = False

    DEBUG: bool = False
    PROJECT_NAME: str = 'messenger'
    API_V1_STR: str = '/api/v1'

    SECRET_KEY: str

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
