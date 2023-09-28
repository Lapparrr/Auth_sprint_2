import logging

import uvicorn
from async_fastapi_jwt_auth import AuthJWT
from fastapi import FastAPI, Depends
from fastapi.responses import ORJSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from redis.asyncio import Redis
from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncEngine

from src.api.v1 import auth, permission, role, user
from src.core.logger import LOGGING
from src.db import redis, postgres
from src.settings import settings

app = FastAPI(
    title=settings.project_name,
    version='1.0.0',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    dependencies=[Depends(RateLimiter(times=10, seconds=25))],
)


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


app.include_router(auth.router, prefix='/api/v1/auth')
app.include_router(permission.router, prefix='/api/v1/permission')
app.include_router(role.router, prefix='/api/v1/role')
app.include_router(user.router, prefix='/api/v1/user')


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
