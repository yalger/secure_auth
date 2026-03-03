from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):

    DATABASE_URL: str = "sqlite:///./test.db"
    SECRET_KEY: str = "dev-secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings():
    return Settings()

settings = get_settings()