import uuid as uuid_pkg
from typing import Optional

from sqlmodel import SQLModel, Field


class RolePermission(SQLModel, table=True):
    role_id: Optional[uuid_pkg.UUID] = Field(
        default=None, foreign_key="role.id", primary_key=True
    )
    permission_id: Optional[uuid_pkg.UUID] = Field(
        default=None, foreign_key="permission.id", primary_key=True
    )
