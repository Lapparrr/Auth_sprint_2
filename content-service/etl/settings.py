from dotenv import load_dotenv

load_dotenv()

from pydantic import (
    BaseSettings,
    Field,
)


class SettingsPostgres(BaseSettings):
    """Настройки подключений к БД

    Arguments:
        BaseSettings {[type]} -- [description]
    """

    dbname: str = Field(..., env="DB_NAME")
    user: str = Field(..., env="DB_USER")
    password: str = Field(..., env="DB_PASSWORD")
    host: str = Field(..., env="DB_HOST")
    port: str = Field(..., env="DB_PORT")


class SettingsElastic(BaseSettings):
    es_host: str = Field(..., env="ES_HOST")
    es_port: str = Field(..., env="ES_PORT")


class JsonPath(BaseSettings):
    json_storage_path: str = Field(..., env="JSON_STORAGE_PATH")
