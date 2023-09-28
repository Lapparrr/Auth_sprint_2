import uuid
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from fastapi_pagination import Page

from src.api.v1.schemas.user import UserResponse
from src.models.data import RoleCreate, UserRole
from src.models.role import Role
from src.models.user import User
from src.services.role import RoleService, role_services
from src.services.user import UserService, users_services

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/token")


@router.post(
    '/create',
    status_code=HTTPStatus.OK,
    tags=['roles'],
    description='Create new Role',
    summary="Создать роль",
    response_model=Role,
)
async def create_role(
    token: Annotated[str, Depends(oauth2_scheme)],
    role: RoleCreate,
    service: RoleService = Depends(role_services),
) -> Role:
    role = await service.create_role(name=role.name, description=role.description)
    if not role:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Role is taken')
    return role


@router.get(
    '/list',
    status_code=HTTPStatus.OK,
    tags=['roles'],
    description='List Roles',
    summary="Список ролей",
    response_model=Page[Role],
)
async def get_role(
    token: Annotated[str, Depends(oauth2_scheme)],
    page: int = Query(1),
    items_per_page: int = Query(10),
    service: RoleService = Depends(role_services),
) -> Page[Role]:
    result = await service.get_roles()
    if not result:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Role not exist')
    skip_pages = page - 1
    return Page(
        items=result[skip_pages : skip_pages + items_per_page],
        total=len(result),
        page=page,
        size=items_per_page,
    )


@router.delete(
    '/delete',
    status_code=HTTPStatus.NO_CONTENT,
    tags=['roles'],
    description='Delete Roles',
    summary="Удалить роль",
)
async def delete_role(
    token: Annotated[str, Depends(oauth2_scheme)],
    role_id: Annotated[uuid.UUID, Query()],
    service: RoleService = Depends(role_services),
) -> None:
    result = await service.delete_role(role_id=role_id)

    if not result:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Permission not exist'
        )


@router.post(
    '/user_set',
    status_code=HTTPStatus.OK,
    tags=['roles'],
    description='User set Roles',
    summary="Назначить роль user",
    response_model=UserResponse,
)
async def user_set_role(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_role: UserRole,
    role_service: RoleService = Depends(role_services),
    user_service: UserService = Depends(users_services),
) -> User:
    user = await user_service.get_user_by_id(user_role.user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not exist')

    role = await role_service.get_role_by_id(user_role.role_id)
    if not role:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Role not exist')

    result = await role_service.set_user_role(user, role)

    return result


@router.delete(
    '/user_del',
    status_code=HTTPStatus.OK,
    tags=['roles'],
    description='User delete Roles',
    summary="Удалить роль у пользователя user",
    response_model=UserResponse,
)
async def user_delete_role(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_role: UserRole,
    role_service: RoleService = Depends(role_services),
    user_service: UserService = Depends(users_services),
) -> User:
    user = await user_service.get_user_by_id(user_role.user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not exist')

    role = await role_service.get_role_by_id(user_role.role_id)
    if not role:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Role not exist')

    result = await role_service.delete_user_role(user, role)

    return result
