import uuid
from functools import lru_cache
from typing import Optional

from fastapi import Depends
from sqlmodel import select, delete
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.postgres import get_session
from src.models.role import Role

from src.models.user import User
from src.core.config import logger


class RoleService:
    def __init__(self, pg: AsyncSession) -> None:
        self.pg = pg

    async def get_role_by_name(self, name: str) -> Role:
        logger.info("Check if role exist")
        result = await self.pg.execute(select(Role).where(Role.name == name))
        found = result.scalars().first()

        return found

    async def create_role(self, name: str, description: str) -> Optional[Role]:
        logger.info("Start create_role")
        if await self.get_role_by_name(name=name):
            return None
        role = Role(name=name, description=description)
        self.pg.add(role)
        await self.pg.commit()
        return role

    async def get_roles(self) -> list[Role]:
        logger.info("Start all get_permissions")
        data = await self.pg.execute(select(Role))
        return data.scalars().all()

    async def delete_role(self, role_id: uuid.UUID) -> bool:
        logger.info("Start delete_role")
        result = await self.pg.execute(delete(Role).where(Role.id == role_id))
        await self.pg.commit()
        return bool(result)

    async def set_user_role(self, user: User, role: Role) -> User:
        logger.info("Start set_role_to_user")
        user.roles.append(role)
        self.pg.add(user)
        await self.pg.commit()
        return user

    async def delete_user_role(self, user: User, role: Role) -> User:
        logger.info("Delete users role")
        if user.roles:
            user.roles.remove(role)
            self.pg.add(user)
            await self.pg.commit()
        return user

    async def get_role_by_id(self, role_id: uuid.UUID) -> Role:
        logger.info("Start get_role_by_id")
        result = await self.pg.execute(select(Role).where(Role.id == role_id))
        role_found = result.scalars().first()
        return role_found if role_found else None

@lru_cache()
def role_services(
    pg: AsyncSession = Depends(get_session),
) -> RoleService:
    return RoleService(pg=pg)
