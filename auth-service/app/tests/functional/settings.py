import os

from dotenv import load_dotenv
from pydantic import BaseSettings, Field


BASE_PATH = os.path.abspath(os.path.dirname(os.path.dirname(os.getcwd())))
ENV_PATH = os.path.join(BASE_PATH, 'env', '.env')

load_dotenv(ENV_PATH)


class TestSettings(BaseSettings):
    postgres_db: str = Field(..., env='POSTGRES_DB')
    postgres_host: str = ...
    postgres_port: str = ...
    postgres_password: str = ...
    postgres_user: str = ...

    service_url: str = ...


class DatabaseSettings(BaseSettings):
    db: str = Field(..., env='POSTGRES_DB')
    user: str = ...
    password: str = ...
    host: str = ...
    port: int = ...


test_settings = TestSettings()
