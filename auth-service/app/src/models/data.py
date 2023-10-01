import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserSingUp(BaseModel):
    login: Optional[str] = None
    password: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        orm_mode = True


class UserInDb(BaseModel):
    login: str
    email: str

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class PermissionCreate(BaseModel):
    name: str
    description: str

    class Config:
        orm_mode = True


class PermissionInDb(BaseModel):
    name: str
    description: str

    class Config:
        orm_mode = True


class RoleInDb(BaseModel):
    id: uuid.UUID
    name: str
    description: str

    class Config:
        orm_mode = True


class RoleCreate(BaseModel):
    name: str
    description: str

    class Config:
        orm_mode = True


class RoleUpdate(BaseModel):
    name: str
    new_name: str
    new_description: str

    class Config:
        orm_mode = True


class UserRole(BaseModel):
    user_id: uuid.UUID
    role_id: uuid.UUID

    class Config:
        orm_mode = True
