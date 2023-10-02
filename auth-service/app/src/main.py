import logging

import uvicorn
from async_fastapi_jwt_auth import AuthJWT
from fastapi import FastAPI, Depends, Request, status
from fastapi.responses import ORJSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis
from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncEngine

from src.api.v1 import auth, permission, role, user
from src.core.logger import LOGGING
from src.db import redis, postgres
from src.services.dependencies import get_current_user_global
from src.settings import settings


origins = [
    "http://localhost",
    "http://localhost:8080",
    "https://oauth.yandex.ru",
    "https://oauth.yandex.ru/authorize?"
]

app = FastAPI(
    title=settings.project_name,
    version='1.0.0',
    docs_url='/auth/api/openapi',
    openapi_url='/auth/api/openapi.json',
    default_response_class=ORJSONResponse,
    dependencies=[Depends(RateLimiter(times=10, seconds=25))],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware('http')
async def before_request(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': 'X-Request-Id is required'})
    return response


@AuthJWT.load_config
def get_config():
    return settings


@AuthJWT.token_in_denylist_loader
async def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token['jti'] or decrypted_token['refresh_jti']
    entry = await redis.redis.get(jti)
    return entry and entry.decode("utf-8") == "true"


@app.on_event('startup')
async def startup():
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    await FastAPILimiter.init(redis.redis)

    postgres.engine = AsyncEngine(
        create_engine(
            settings.pg_url(), echo=settings.postgres_engine_echo, future=True
        )
    )


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()


app.include_router(auth.router, prefix='/auth/api/v1/auth')
app.include_router(
    permission.router,
    prefix='/auth/api/v1/permission',
    dependencies=[Depends(get_current_user_global)]
)
app.include_router(
    role.router, prefix='/auth/api/v1/role', dependencies=[Depends(get_current_user_global)]
)
app.include_router(
    user.router, prefix='/auth/api/v1/user', dependencies=[Depends(get_current_user_global)]
)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
