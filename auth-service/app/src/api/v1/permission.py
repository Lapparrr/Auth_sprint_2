import uuid
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from fastapi_pagination import Page

from src.models.data import PermissionCreate
from src.models.permission import Permission
from src.services.permission import PermissionService, permission_services

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/token")


@router.post(
    '/create',
    status_code=HTTPStatus.OK,
    tags=['permissions'],
    description='Create new permission',
    summary="Создать разрешение",
    response_model=Permission,
)
async def create_permission(
    token: Annotated[str, Depends(oauth2_scheme)],
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
async def get_permission(
    page: int = Query(1),
    items_per_page: int = Query(10),
    service: PermissionService = Depends(permission_services),
) -> Page[Permission]:
    result = await service.get_permissions()
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
    tags=['permissions'],
    description='Delete Permission',
    summary="Удалить разрешение",
)
async def delete_permission(
    token: Annotated[str, Depends(oauth2_scheme)],
    permission_id: Annotated[uuid.UUID, Query()],
    service: PermissionService = Depends(permission_services),
) -> None:
    result = await service.delete_permission(permission_id=permission_id)

    if not result:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Permission not exist'
        )
