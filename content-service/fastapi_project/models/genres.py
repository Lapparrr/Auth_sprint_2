from models.mixin import MixinModel
from pydantic import root_validator
from typing import List, Optional


class Genre(MixinModel):
    uuid: str
    name: str
    description: Optional[str]  # Allow None as a valid value
    films: list

    @root_validator(pre=False)
    def _set_fields(cls, values: dict) -> dict:
        return values
