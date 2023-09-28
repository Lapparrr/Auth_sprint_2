import uuid
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from fastapi_pagination import Page

from src.api.v1.schemas.user import UserResponse
from src.models.user import User
from src.services.user import UserService, users_services

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/token")


@router.get(
    '/list',
    status_code=HTTPStatus.OK,
    tags=['user'],
    description='Users',
    summary="Список пользователей",
    response_model=Page[UserResponse],
)
async def get_users(
    token: Annotated[str, Depends(oauth2_scheme)],
    page: int = Query(1),
    items_per_page: int = Query(10),
    service: UserService = Depends(users_services),
) -> Page[User]:
    result = await service.get_users()
    skip_pages = page - 1
    return Page(
        items=result[skip_pages : skip_pages + items_per_page],
        total=len(result),
        page=page,
        size=items_per_page,
    )


@router.get(
    '/',
    status_code=HTTPStatus.OK,
    tags=['user'],
    description='User',
    summary="Получить пользователя",
    response_model=UserResponse,
)
async def get_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: uuid.UUID,
    service: UserService = Depends(users_services),
) -> User:
    result = await service.get_user_by_id(user_id)
    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='user not exist')
    return result
