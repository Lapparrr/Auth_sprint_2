import uuid
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import logger
from src.db.postgres import get_session
from src.models.social_account import SocialAccount
from src.models.user import User


class SocialAccountService:
    def __init__(self, pg: AsyncSession) -> None:
        self.pg = pg

    async def get_social_account(
        self, social_id: str, social_name: str
    ) -> SocialAccount:
        logger.info("Start get_social_account")
        data = await self.pg.execute(
            select(SocialAccount)
            .where(
                social_id == social_id,
                social_name == social_name
            )
            .options(selectinload(User).options(selectinload(User.roles)))
        )
        return data.scalars().first()


@lru_cache()
def social_account_services(
    pg: AsyncSession = Depends(get_session),
) -> SocialAccountService:
    return SocialAccountService(pg=pg)
