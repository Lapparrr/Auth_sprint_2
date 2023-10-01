from functools import wraps

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, Request, status, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas.auth import AuthRequest
from src.db.postgres import get_session
from src.models.data import UserInDb
from src.models.role import RoleEnum
from src.services.auth import AuthService, get_auth_service


class AuthException(HTTPException):
    pass


def roles_required(roles_list: list[RoleEnum]):
    def decorator(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            user: UserInDb = kwargs.get('request').custom_user
            if not user or not bool({role.name for role in user.roles} & {x.value for x in roles_list}):
                raise AuthException(
                    detail='This operation is forbidden for you',
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            return await function(*args, **kwargs)
        return wrapper
    return decorator


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(
        self, request: Request,
        db: AsyncSession = Depends(get_session),
        auth_service: AuthService = Depends(get_auth_service)
    ) -> UserInDb | None:
        authorize = AuthJWT(req=request)
        await authorize.jwt_optional()
        user_email = await authorize.get_jwt_subject()
        if not user_email:
            return None
        user = await auth_service.get_by_mail(user_email)
        return UserInDb.from_orm(user)


async def get_current_user_global(
    request: AuthRequest, user: AsyncSession = Depends(JWTBearer())
):
    request.custom_user = user
