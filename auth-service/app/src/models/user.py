import datetime
import uuid as uuid_pkg
from typing import List

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship

from src.models.user_roles import UserRoles
from src.models.role import Role


class User(SQLModel, table=True):
    id: uuid_pkg.UUID = Field(
        default=uuid_pkg.uuid4(),
        primary_key=True,
        index=True,
        unique=True,
        nullable=False,
    )
    login: str = Field(max_length=256, min_length=6, index=True, nullable=False)
    password: str = Field(max_length=256, min_length=6, nullable=False)
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: EmailStr = Field(index=True, unique=True, nullable=False)
    created_at: datetime.datetime = datetime.datetime.now()

    roles: List[Role] = Relationship(back_populates="users", link_model=UserRoles)

    def __repr__(self) -> str:
        return f'<User {self.login}>'
