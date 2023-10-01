import datetime
from sqlmodel import SQLModel, Field
import uuid as uuid_pkg


class AccountHistory(SQLModel, table=True):
    id: uuid_pkg.UUID = Field(
        default=uuid_pkg.uuid4(),
        primary_key=True,
        index=True,
        unique=True,
        nullable=False,
    )

    user_login: str = Field(max_length=256, min_length=6, nullable=False)
    created_at: datetime.datetime = datetime.datetime.now()
