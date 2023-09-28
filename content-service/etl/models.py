import uuid

from pydantic import BaseModel, root_validator
from pydantic.schema import Optional
from numpy import mean


class PersonAggDB(BaseModel):
    """Модель данных аггрегата Person

    Arguments:
        BaseModel {[type]} -- [description]
    """

    person_role: str
    person_id: uuid.UUID
    person_name: str


class Person(BaseModel):
    """Модель данных для сценаристов, актеров и режиссеров

    Arguments:
        BaseModel {[type]} -- [description]
    """

    full_name: str
    uuid: uuid.UUID


class Genre(BaseModel):
    """Модель данных для сценаристов, актеров и режиссеров

    Arguments:
        BaseModel {[type]} -- [description]
    """

    name: str
    uuid: uuid.UUID


class MoviesToES(BaseModel):
    """Модель данных для загрузки в Elastic

    Arguments:
        BaseModel {[type]} -- [description]

    Returns:
        [type] -- [description]
    """

    id: uuid.UUID
    uuid: Optional[uuid.UUID]
    imdb_rating: Optional[float]
    genre: list[Genre]
    title: str
    description: Optional[str]
    persons: Optional[list[PersonAggDB]]
    director: list[Person] = None
    actors: list[Person] = None
    writers: list[Person] = None
    actors_names: list[str] = None
    writers_names: list[str] = None

    @root_validator(pre=False)
    def _set_fields(cls, values: dict) -> dict:
        """This is a validator that sets the field values

        Args:
            values (dict): Stores the attributes of the User object.

        Returns:
            dict: The attributes of the user object with the user's fields.
        """
        values["director"] = [
            {"full_name": r.person_name, "uuid": r.person_id}
            for r in values["persons"]
            if r.person_role == "director"
        ]
        values["actors"] = [
            {"full_name": r.person_name, "uuid": r.person_id}
            for r in values["persons"]
            if r.person_role == "actor"
        ]
        values["writers"] = [
            {"full_name": r.person_name, "uuid": r.person_id}
            for r in values["persons"]
            if r.person_role == "writer"
        ]
        values["actors_names"] = [r["full_name"] for r in values["actors"]]
        values["writers_names"] = [r["full_name"] for r in values["writers"]]
        values["uuid"] = values["id"]
        return values


class GenreToES(BaseModel):
    """Модель жанра."""

    id: uuid.UUID
    uuid: Optional[uuid.UUID]
    name: str
    description: Optional[str] = ""
    imdb_rating: Optional[list] = 0
    films: list

    @root_validator(pre=False)
    def _set_fields(cls, values: dict) -> dict:
        values["imdb_rating"] = mean(
            [
                rate["rating"] if rate["rating"] != None else 0
                for rate in values["films"]
            ]
        )
        values["uuid"] = values["id"]
        return values


class PersonToES(BaseModel):
    """Модель персоналии (директор, актер, сценарист)."""

    id: str
    uuid: Optional[uuid.UUID]
    full_name: str
    films: list

    @root_validator(pre=False)
    def _set_fields(cls, values: dict) -> dict:
        new_films = dict()
        for i in values["films"]:
            if new_films.__contains__(i["uuid"]):
                new_films[i["uuid"]]["roles"].append(i["roles"])
            else:
                new_films[i["uuid"]] = dict()
                new_films[i["uuid"]]["roles"] = [i["roles"]]
        values["films"] = [
            {"uuid": id, "roles": roles["roles"]}
            for id, roles in zip(new_films, new_films.values())
        ]
        values["uuid"] = values["id"]
        return values
