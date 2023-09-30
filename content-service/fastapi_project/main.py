import logging

import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from fastapi_pagination import add_pagination
from fastapi.openapi.utils import get_openapi

from dotenv import load_dotenv

load_dotenv()

from api.v1 import films, genre, person
from core.config import Settings
from core.logger import LOGGING
from db import elastic, redis

import logging

logging.basicConfig(level=logging.INFO)

config = Settings()
logging.info("Start")
logging.info("Config es host: %s", config.ELASTIC_HOST)
logging.info("Config es port: %s", config.ELASTIC_PORT)
logging.info("Config redis host: %s", config.REDIS_HOST)
logging.info("Config redis port: %s", config.REDIS_PORT)

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    description='Апи для онлайн кинотеатра',
)


@app.on_event("startup")
async def startup():
    redis.redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    elastic.es = AsyncElasticsearch(
        hosts=[f"http://{config.ELASTIC_HOST}:{config.ELASTIC_PORT}"]
    )


@app.on_event("shutdown")
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


@app.get(
    "/",
    tags=['main']
)
async def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    


# Подключаем роутер к серверу, указав префикс /v1/films
# Теги указываем для удобства навигации по документации
app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genre.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(person.router, prefix="/api/v1/persons", tags=["persons"])

add_pagination(app)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
    )
