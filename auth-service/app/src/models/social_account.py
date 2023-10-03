import uuid

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from src.models.base import BaseMixin

from src.models.user import User


class SocialAccount(BaseMixin, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    social_id: str = Field(nullable=False)
    social_name: str = Field(nullable=False)

    user: User = Relationship(back_populates="social_accounts")

    __table_args__ = (
        UniqueConstraint('social_id', 'social_name', name='uq_social_id_social_name'),
    )

    def __repr__(self):
        return f'<SocialAccount {self.social_name}:{self.user_id}>'
