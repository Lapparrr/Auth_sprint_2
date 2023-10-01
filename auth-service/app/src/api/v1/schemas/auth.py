from pydantic import BaseModel
from fastapi import Request

from src.models.data import UserInDb


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str


class AuthRequest(Request):
    custom_user: UserInDb
