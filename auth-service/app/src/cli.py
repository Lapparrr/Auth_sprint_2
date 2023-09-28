import logging
from typing import Optional
import asyncio

import typer
from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncEngine
from typing_extensions import Annotated


from src.db import postgres
from src.db.postgres import get_session
from src.db.redis import get_redis
from src.services.role import role_services
from src.services.auth import get_auth_service
from src.models.data import UserSingUp
from src.services.user import users_services
from src.settings import settings

app = typer.Typer()


@app.command()
def create_user(
    login: str,
    password: str,
    email: str,
    first_name: Annotated[Optional[str], typer.Argument()] = 'Admin',
    last_name: Annotated[Optional[str], typer.Argument()] = 'Super',
):
    asyncio.run(create_user_async(login, password, email, first_name, last_name))


async def create_user_async(
    login: str,
    password: str,
    email: str,
    first_name: str = 'Admin',
    last_name: str = 'Super',
):
    """
    Create a new user with USERNAME.
    """
    async_session_auth = get_session()
    auth_service = get_auth_service(
        pg=await async_session_auth.__anext__(), redis=await get_redis()
    )
    user = UserSingUp(
        login=login,
        password=password,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )

    if await auth_service.get_by_login(login):
        logging.warning('User has already been created')
    else:
        user = await auth_service.add_user(user)


@app.command()
def add_role(login: str, role: str):
    asyncio.run(add_role_async(login, role))


async def add_role_async(login, role):
    async_session_role = get_session()
    role_service = role_services(await async_session_role.__anext__())
    user = await role_service.get_by_login(login)
    role_in_db = await role_service.get_role_by_name(role)
    await role_service.set_user_role(user, role_in_db)


@app.command()
def create_role(name: str, description: str):
    asyncio.run(create_role_async(name, description))


async def create_role_async(name: str, description: str):
    role_service = role_services([item async for item in get_session()][0])
    if await role_service.get_role_by_name(name):
        logging.log(logging.WARNING, "Role has already been created")
    else:
        await role_service.create_role(name, description)


if __name__ == "__main__":
    postgres.engine = AsyncEngine(
        create_engine(settings.pg_url(), echo=True, future=True)
    )
    app()
