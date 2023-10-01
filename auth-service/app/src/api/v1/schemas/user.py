from typing import Optional, List

from src.models.role import Role
from src.models.utils import ModelWithConf


class UserSignUp(ModelWithConf):
    login: str
    password: str
    email: str
    first_name: str
    last_name: str


class UserResponse(ModelWithConf):
    login: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: List[Role] = []
