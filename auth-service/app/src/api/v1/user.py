import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_pagination import Page

from src.api.v1.schemas.auth import AuthRequest
from src.api.v1.schemas.user import UserResponse
from src.models.role import RoleEnum
from src.models.user import User
from src.services.dependencies import roles_required
from src.services.user import UserService, users_services

router = APIRouter()


@router.get(
    '/list',
    status_code=HTTPStatus.OK,
    tags=['user'],
    description='Users',
    summary="Список пользователей",
    response_model=Page[UserResponse],
)
@roles_required(roles_list=[RoleEnum.ADMIN])
async def get_users(
    request: AuthRequest,
    page: int = Query(1),
    items_per_page: int = Query(10),
    service: UserService = Depends(users_services),
) -> Page[User]:
    result = await service.get_users()
    skip_pages = page - 1
    return Page(
        items=result[skip_pages: skip_pages + items_per_page],
        total=len(result),
        page=page,
        size=items_per_page
    )


@router.get(
    '/',
    status_code=HTTPStatus.OK,
    tags=['user'],
    description='User',
    summary="Получить пользователя",
    response_model=UserResponse,
)
@roles_required(roles_list=[RoleEnum.ADMIN, RoleEnum.REGISTERED, RoleEnum.SUBSCRIBER])
async def get_user(
    request: AuthRequest,
    user_id: uuid.UUID,
    service: UserService = Depends(users_services),
) -> User:
    result = await service.get_user_by_id(user_id)
    if (
        RoleEnum.ADMIN not in [role.name for role in request.custom_user.roles]
        and result.email != request.custom_user.email
    ):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='This operation is forbidden for you'
        )
    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='user not exist')
    return result
