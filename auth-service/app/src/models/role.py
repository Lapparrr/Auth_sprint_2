import uuid as uuid_pkg
from typing import List

from sqlmodel import SQLModel, Field, Relationship
from src.models.role_permission import RolePermission
from src.models.permission import Permission
from src.models.user_roles import UserRoles


class Role(SQLModel, table=True):
    id: uuid_pkg.UUID = Field(
        default=uuid_pkg.uuid4(),
        primary_key=True,
        index=True,
        unique=True,
        nullable=False,
    )
    name: str = Field(max_length=256, min_length=5, nullable=False, unique=True)
    description: str = Field(max_length=256, min_length=5)

    users: List["User"] = Relationship(back_populates="roles", link_model=UserRoles)
    permissions: List[Permission] = Relationship(
        back_populates="roles", link_model=RolePermission
    )

    def __repr__(self) -> str:
        return f'<Role {self.name}>'
