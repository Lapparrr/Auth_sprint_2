import uuid
from functools import lru_cache

from fastapi import Depends
from sqlalchemy import delete
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import logger
from src.db.postgres import get_session
from src.models.permission import Permission


class PermissionService:
    def __init__(self, pg: AsyncSession) -> None:
        self.pg = pg

    async def exist_permission(self, name) -> bool:
        result = await self.pg.execute(
            select(Permission).where(Permission.name == name)
        )
        found = result.scalars().first()

        return bool(found)

    async def create_permission(self, name: str, description: str) -> Permission | bool:
        logger.info("Start create_permission")

        if await self.exist_permission(name=name):
            return False

        permission = Permission(name=name, description=description)

        self.pg.add(permission)
        await self.pg.commit()

        logger.info("create_permission ok")

        return permission

    async def get_permissions(self) -> list[Permission]:
        logger.info("Start get_permissions")
        data = await self.pg.execute(select(Permission))
        return data.scalars().all()

    async def delete_permission(self, permission_id: uuid.UUID) -> bool:
        logger.info("Start delete_permission")
        result = await self.pg.execute(
            delete(Permission).where(Permission.id == permission_id)
        )
        await self.pg.commit()
        return bool(result)


@lru_cache()
def permission_services(
    pg: AsyncSession = Depends(get_session),
) -> PermissionService:
    return PermissionService(pg=pg)
