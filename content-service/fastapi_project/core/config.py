import os

# load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()
from pydantic import (
    BaseSettings,
    Field,
)

from logging import config as logging_config

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    PROJECT_NAME: str = Field(..., env="PROJECT_NAME")
    REDIS_HOST: str = Field(..., env="REDIS_HOST")
    REDIS_PORT: float = Field(..., env="REDIS_PORT")
    ELASTIC_HOST: str = Field(..., env="ES_HOST")
    ELASTIC_PORT: str = Field(..., env="ES_PORT")


# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
