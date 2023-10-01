import uuid as uuid_pkg
from typing import List

from sqlmodel import SQLModel, Field, Relationship

from src.models.role_permission import RolePermission


class Permission(SQLModel, table=True):
    id: uuid_pkg.UUID = Field(
        default=uuid_pkg.uuid4(),
        primary_key=True,
        index=True,
        unique=True,
        nullable=False,
    )
    name: str = Field(max_length=256, min_length=6, nullable=False, unique=True)
    description: str = Field(max_length=256, min_length=6)

    roles: List["Role"] = Relationship(
        back_populates="permissions", link_model=RolePermission
    )

    def __repr__(self) -> str:
        return f'<Role {self.name}>'
