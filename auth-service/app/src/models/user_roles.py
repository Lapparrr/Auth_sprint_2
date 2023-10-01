import uuid as uuid_pkg
from typing import Optional

from sqlmodel import SQLModel, Field


class UserRoles(SQLModel, table=True):
    user_id: Optional[uuid_pkg.UUID] = Field(
        default=None, foreign_key="user.id", primary_key=True
    )
    role_id: Optional[uuid_pkg.UUID] = Field(
        default=None, foreign_key="role.id", primary_key=True
    )
