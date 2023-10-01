
import uuid
# load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()
from pydantic import (
    BaseSettings,
    Field,
)

class Settings(BaseSettings):
    PROJECT_NAME: str = Field(..., env="PROJECT_NAME")
    REDIS_HOST: str = Field(..., env="REDIS_HOST")
    REDIS_PORT: float = Field(..., env="REDIS_PORT")
    ELASTIC_HOST: str = Field(..., env="ES_HOST")
    ELASTIC_PORT: str = Field(..., env="ES_PORT")
    es_index_movies: str = 'movies'
    es_id_field_movies: str = 'uuid'
    service_url: str ='http://api:8000'
    create_number = 10
    check_url_search_film = '/api/v1/films/search/'
    es_index_persons: str = 'persons'
    es_id_field_persons: str = 'uuid'
    check_url_search_person = '/api/v1/persons/search/'
    check_url_id_film = '/api/v1/films/'
    check_url_id_genres = '/api/v1/genres/'
    check_url_id_persons = '/api/v1/persons/'
    es_index_genres: str = 'genres'


settings = Settings()