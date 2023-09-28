from pydantic import root_validator
from typing import List, Optional

from models.mixin import MixinModel


class Film(MixinModel):
    title: str
    description: Optional[str] = None  # Allow None as a valid value
    imdb_rating: Optional[float] = None
    genre: Optional[List] = None
    actors: Optional[List] = None
    writers: Optional[List] = None
    director: Optional[List] = None
    actors_names: Optional[List] = None
    writers_names: Optional[List] = None

    @root_validator(pre=True)
    def _set_fields(cls, values: dict) -> dict:
        return values
