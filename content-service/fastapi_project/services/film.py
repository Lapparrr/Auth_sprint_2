import json
from functools import lru_cache
from typing import Optional, List

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis
from pydantic import parse_obj_as

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from services.mixin_service import MixinService


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService(MixinService):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        film_json = await self._get_from_cache(film_id)
        if not film_json:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_from_elastic_by_id("movies", film_id, Film)
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return []
            # Сохраняем фильм  в кеш
            delattr(film, "actors_names")
            delattr(film, "writers_names")
            await self._put_to_cache(
                film.uuid, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS
            )
        else:
            film = await self.prepare_data(film_json, Film)
        return film

    # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_filter(self, params: dict) -> Optional[List]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        self.params = params
        key = (
            "films_"
            + params.sort
            + params.genre
            + str(params.page_size)
            + str(params.page_number)
        )
        film_json = await self._get_from_cache(key)
        if not film_json:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            films, film_dict, count_all = await self._get_all_film_from_elastic()
            if not films:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return []
            # Сохраняем фильм  в кеш
            film_dict.append(count_all)
            await self._put_to_cache(
                key, json.dumps(film_dict), FILM_CACHE_EXPIRE_IN_SECONDS
            )
        else:
            count_all = film_json[-1]
            film_json.pop(-1)
            films = await self.prepare_data(film_json, Film)
        return films, count_all

    async def search_films(self, query: str, fields: List[str]) -> Optional[List]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        key = "search_" + query
        film_json = await self._get_from_cache(key)
        if not film_json:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            films = await self.search(
                index="movies", query=query, fields=fields, find_field="title"
            )
            if not films:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return []
            # Сохраняем фильм  в кеш
            await self._put_to_cache(
                key, json.dumps(films), FILM_CACHE_EXPIRE_IN_SECONDS
            )
        else:
            films = film_json
        return films

    async def _get_all_film_from_elastic(self):
        body = dict()
        if self.params.genre != "":
            body["query"] = {
                "nested": {
                    "path": "genre",
                    "query": {
                        "bool": {
                            "must": [{"match": {"genre.uuid": self.params.genre}}]
                        }
                    },
                }
            }
        else:
            body["query"] = {"match_all": {}}
        if self.params.sort != "":
            sort_field = self.params.sort.lstrip("-")
            order = "desc" if self.params.sort.startswith("-") else "asc"
            body["sort"] = {sort_field: {"order": order}}
        body["size"] = self.params.page_size
        body["from"] = self.params.page_number - 1
        try:
            doc = await self.elastic.search(index="movies", body=body)
        except NotFoundError:
            return None
        models = parse_obj_as(list[Film], [i["_source"] for i in doc["hits"]["hits"]])
        film_dict = [
            mod.dict(
                exclude={
                    "genre": True,
                    "actors": True,
                    "writers": True,
                    "director": True,
                    "actors_names": True,
                    "writers_names": True,
                    "description": True,
                }
            )
            for mod in models
        ]
        count_all = doc["hits"]["total"]["value"]
        return models, film_dict, count_all


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
