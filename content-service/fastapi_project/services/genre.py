import json
from functools import lru_cache
from typing import Optional, List

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis
from pydantic import parse_obj_as

from db.elastic import get_elastic
from db.redis import get_redis
from models.genres import Genre
from services.mixin_service import MixinService

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class GenreService(MixinService):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        genre_json = await self._get_from_cache(genre_id)
        if not genre_json:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            genre = await self._get_from_elastic_by_id("genres", genre_id, Genre)
            if not genre:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return []
            # Сохраняем фильм  в кеш
            await self._put_to_cache(
                genre.uuid, genre.json(), GENRE_CACHE_EXPIRE_IN_SECONDS
            )
        else:
            genre = await self.prepare_data(genre_json, Genre)
        return genre

    # get_by_id возвращает объект жанр. Он опционален, так как жанр может отсутствовать в базе
    async def get_genre(self) -> Optional[Genre]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        genre_json = await self._get_from_cache("genres")
        if not genre_json:
            # Если жанра нет в кеше, то ищем его в Elasticsearch
            genre = await self._get_genre_from_elastic()
            if not genre:
                # Если он отсутствует в Elasticsearch, значит, жанра вообще нет в базе
                return []
            # Сохраняем жанр  в кеш
            await self._put_to_cache(
                "genres", json.dumps(genre), GENRE_CACHE_EXPIRE_IN_SECONDS
            )
        else:
            genre = genre_json
        return genre

    async def _get_genre_from_elastic(self) -> List[Genre]:
        try:
            count_movies = await self.elastic.search(index="genres")
            if count_movies["hits"]["total"]["value"] == 1:
                count_movies["hits"]["total"]["value"] = 2
            doc = await self.elastic.search(
                index="genres",
                body={
                    "query": {"match_all": {}},
                    "size": count_movies["hits"]["total"]["value"] - 1,
                },
            )
        except NotFoundError:
            return []
        models = parse_obj_as(list[Genre], [i["_source"] for i in doc["hits"]["hits"]])
        dicts = [
            mod.dict(exclude={"films": True, "imbd_rating": True, "description": True})
            for mod in models
        ]
        return dicts


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
