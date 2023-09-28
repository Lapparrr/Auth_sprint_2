from models.mixin import MixinModel
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID


class Person(MixinModel):
    full_name: str
    films: list


class FilmRole(BaseModel):
    id_film: str
    roles: List[str]


class PersonSearchResult(BaseModel):
    uuid: str
    full_name: str
    films: List[FilmRole]


class PersonDetail(Person):
    """Детальная модель персоналий."""

    role: str
    film_ids: list
