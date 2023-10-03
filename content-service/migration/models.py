from dataclasses import dataclass, field
from datetime import datetime
import uuid


# Он требует от меня дефолтные поля, что делать если я не хочу так
@dataclass
class IdMixin:
    id: uuid.UUID = field(default=uuid.uuid4)


@dataclass
class TimeStampedMixin:
    created: datetime = field(default=None)
    modified: datetime = field(default=None)


@dataclass
class Genre(IdMixin, TimeStampedMixin):
    name: str = field(default="")
    description: str = field(default="")


@dataclass
class Person(IdMixin, TimeStampedMixin):
    full_name: str = field(default="")


@dataclass
class FilmWork(IdMixin, TimeStampedMixin):
    title: str = field(default="")
    description: str = field(default="")
    rating: float = field(default=None)
    type: str = field(default="")
    creation_date: datetime = field(default=None)


@dataclass
class GenreFilmWork(IdMixin):
    film_work_id: uuid.UUID = field(default=uuid.uuid4)
    genre_id: uuid.UUID = field(default=uuid.uuid4)
    created: datetime = field(default=None)


@dataclass
class PersonFilmWork(IdMixin):
    film_work_id: uuid.UUID = field(default=uuid.uuid4)
    person_id: uuid.UUID = field(default=uuid.uuid4)
    role: str = field(default="")
    created: datetime = field(default=None)
