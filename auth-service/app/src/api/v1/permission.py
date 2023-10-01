import uuid
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_pagination import Page

from src.api.v1.schemas.auth import AuthRequest
from src.models.data import PermissionCreate
from src.models.permission import Permission
from src.models.role import RoleEnum
from src.services.dependencies import roles_required
from src.services.permission import PermissionService, permission_services

router = APIRouter()


@router.post(
    '/create',
    status_code=HTTPStatus.OK,
    tags=['permissions'],
    description='Create new permission',
    summary="Создать разрешение",
    response_model=Permission,
)
@roles_required(roles_list=[RoleEnum.ADMIN])
async def create_permission(
    request: AuthRequest,
    permission: PermissionCreate,
    service: PermissionService = Depends(permission_services),
) -> Permission:
    result = await service.create_permission(
        name=permission.name, description=permission.description
    )
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Permission is taken'
        )

    return result


@router.get(
    '/list',
    response_model=Page[Permission],
    status_code=HTTPStatus.OK,
    tags=['permissions'],
    description='List Permissions',
    summary="Список разрешений",
)
@roles_required(roles_list=[RoleEnum.ADMIN])
async def get_permission(
    request: AuthRequest,
    page: int = Query(1),
    items_per_page: int = Query(10),
    service: PermissionService = Depends(permission_services),
) -> Page[Permission]:
    result = await service.get_permissions()
    skip_pages = page - 1
    return Page(
        items=result[skip_pages: skip_pages + items_per_page],
        total=len(result),
        page=page,
        size=items_per_page,
    )


@router.delete(
    '/delete',
    status_code=HTTPStatus.NO_CONTENT,
    tags=['permissions'],
    description='Delete Permission',
    summary="Удалить разрешение",
)
@roles_required(roles_list=[RoleEnum.ADMIN])
async def delete_permission(
    request: AuthRequest,
    permission_id: Annotated[uuid.UUID, Query()],
    service: PermissionService = Depends(permission_services),
) -> None:
    result = await service.delete_permission(permission_id=permission_id)

    if not result:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Permission not exist'
        )
