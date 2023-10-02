import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class BaseMixin(SQLModel):
    id: uuid.UUID = Field(
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )

    created_at: datetime = Field(default=datetime.utcnow)
    updated_at: datetime = Field(default=datetime.utcnow)
