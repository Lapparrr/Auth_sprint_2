from http import HTTPStatus

from async_fastapi_jwt_auth.exceptions import RevokedTokenError
from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response

from src.api.v1.schemas.auth import LoginResponse, AuthRequest
from src.api.v1.schemas.user import UserResponse
from src.core.config import logger
from src.models.data import UserSingUp, UserLogin
from src.models.role import RoleEnum
from src.models.user import User
from src.services.auth import AuthService, get_auth_service
from src.services.dependencies import roles_required, get_current_user_global, JWTBearer

router = APIRouter()


@router.post(
    '/signup',
    status_code=HTTPStatus.OK,
    tags=['auth'],
    description='Register new user',
    summary="Регистрация нового пользователя",
    response_model=UserResponse,
)
async def register(
    user_create: UserSingUp,
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    user_found = await auth_service.get_by_mail(user_create.email)
    logger.info(f"/signup - email: {user_create.email}")
    if user_found:
        logger.info(f"/signup - email: {user_create.email}, found")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Mail is taken')

    try:
        user = await auth_service.add_user(
            user=user_create, role_name=RoleEnum.REGISTERED
        )
        logger.info(f"Signup successful for login: {user_create.login}")
        return user
    except Exception as ex:
        logger.error(f"Signup failed due to error: {ex}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(ex))


@router.post(
    '/login',
    status_code=HTTPStatus.OK,
    tags=['auth'],
    description='Login user',
    summary="Авторизация пользователя",
    response_model=LoginResponse,
)
async def login(
    user: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponse | Response:
    logger.info(f"/login user - email: {user.email}")
    user_found = await auth_service.get_by_mail(user.email)
    if user_found:
        logger.info(f"/login user - email: {user.email}, found")
    else:
        logger.error("user not found")
        return Response(
            status_code=HTTPStatus.UNAUTHORIZED, content="Invalid login or password"
        )
    try:
        await auth_service.check_password(user=user)
        refresh_token = await auth_service.create_refresh_token(user_found.email)
        refresh_jti = await auth_service.auth.get_jti(refresh_token)
        access_token = await auth_service.create_access_token(
            payload=user_found.email,
            user_claims={
                "refresh_jti": refresh_jti,
                "roles": [role.name for role in user_found.roles],
            }
        )
        return LoginResponse(access_token=access_token, refresh_token=refresh_token)
    except ValueError as ex:
        logger.error(f"login failed due to error: {ex}")
        return Response(
            status_code=HTTPStatus.UNAUTHORIZED, content="invalid login or password"
        )


@router.post(
    '/logout',
    status_code=HTTPStatus.OK,
    tags=['auth'],
    description='Logout user',
    summary="Выход пользователя из сиcтемы",
    dependencies=[Depends(get_current_user_global)],
)
@roles_required(roles_list=[RoleEnum.ADMIN, RoleEnum.REGISTERED, RoleEnum.SUBSCRIBER])
async def logout(
    request: AuthRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> Response:
    logger.info("/logout user - get access and refresh tokens")
    try:
        await auth_service.auth.jwt_required()
    except RevokedTokenError as ex:
        logger.info("/logout user - access_token has been revoked", exc_info=ex)
        return Response(status_code=HTTPStatus.UNAUTHORIZED)
    subject = await auth_service.auth.get_jwt_subject()
    logger.info(f"/ get user - login: {subject}")
    logger.info(f"/Set expire tokens to redis")
    await auth_service.revoke_both_tokens()
    return Response(status_code=HTTPStatus.OK)


@router.post(
    '/refresh_token',
    status_code=HTTPStatus.OK,
    tags=['auth'],
    description='Refresh user tokens',
    summary="Обновление токенов пользователя",
    response_model=LoginResponse,
)
async def refresh_token(
    auth_service: AuthService = Depends(get_auth_service),
) -> Response | LoginResponse:
    logger.info("/refresh user - get access and refresh tokens")
    try:
        await auth_service.auth.jwt_refresh_token_required()
    except RevokedTokenError as ex:
        logger.info("/logout user - refresh_token has been revoked", exc_info=ex)
        return Response(status_code=HTTPStatus.UNAUTHORIZED)

    jwt_subject = await auth_service.auth.get_jwt_subject()
    logger.info(f"/ get user - login: {jwt_subject}")
    user = await auth_service.get_by_mail(jwt_subject)
    if not user:
        return Response(status_code=HTTPStatus.UNAUTHORIZED)

    await auth_service.revoke_both_tokens()
    new_refresh_token = await auth_service.create_access_token(payload=jwt_subject)
    new_access_token = await auth_service.create_access_token(
        payload=jwt_subject,
        user_claims={
            "refresh_jti": new_refresh_token,
            "roles": [role.name for role in user.roles],
        }
    )

    return LoginResponse(access_token=new_access_token, refresh_token=new_refresh_token)


@router.post(
    '/sync',
    status_code=HTTPStatus.OK,
    tags=['auth'],
    description='Sync admin user',
    summary="Синхронизация администратора",
    response_model=UserResponse
)
async def register(
    user_login: UserLogin, auth_service: AuthService = Depends(get_auth_service),
) -> User:
    user_found = await auth_service.get_by_mail(user_login.email)
    logger.info(f"/sync admin - email: {user_login.email}")
    if user_found is None:
        logger.info(f"/sync admin - email: {user_login.email}, not found")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')
    if RoleEnum.ADMIN not in [role.name for role in user_found.roles]:
        logger.info(f"/sync admin: {user_login.email}, not admin")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='User not admin')
    return user_found

