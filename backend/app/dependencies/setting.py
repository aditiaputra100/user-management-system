from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class _Settings(BaseSettings):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    database_dialect: str
    database_username: str
    database_password: str
    database_host: str
    database_port: str
    database_name: str
    superuser_username: str
    superuser_password: str

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return _Settings()