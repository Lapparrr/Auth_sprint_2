from pydantic import (
    BaseSettings,
    Field,
)

from models import FilmWork, Person, PersonFilmWork, Genre, GenreFilmWork


class Settings(BaseSettings):
    dbname: str = Field(..., env="DB_NAME")
    user: str = Field(..., env="DB_USER")
    password: str = Field(..., env="DB_PASSWORD")
    host: str = Field(..., env="DB_HOST")
    port: str = Field(..., env="DB_PORT")


datatables_list = {
    "film_work": FilmWork,
    "person": Person,
    "person_film_work": PersonFilmWork,
    "genre": Genre,
    "genre_film_work": GenreFilmWork,
}
