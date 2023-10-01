import json
from functools import lru_cache
from typing import Optional, List, Dict, Union

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis
from pydantic import parse_obj_as

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person
from services.mixin_service import MixinService
import logging

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonService(MixinService):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        person_json = await self._get_from_cache(person_id)
        if not person_json:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            person = await self._get_from_elastic_by_id("persons", person_id, Person)
            if not person:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return []
            # Сохраняем фильм  в кеш
            await self._put_to_cache(
                person.uuid, person.json(), PERSON_CACHE_EXPIRE_IN_SECONDS
            )
        else:
            person = await self.prepare_data(person_json, Person)
        return person

    # get_by_id возвращает объект жанр. Он опционален, так как жанр может отсутствовать в базе
    async def get_person(self, page_params: dict) -> Optional[Person]:
        self.params = page_params
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        key = "persons_" + str(page_params.page_number) + str(page_params.page_size)
        person_json = await self._get_from_cache(key)
        if not person_json:
            # Если жанра нет в кеше, то ищем его в Elasticsearch
            person, person_dict, count_all = await self._get_person_from_elastic()
            if not person_dict:
                # Если он отсутствует в Elasticsearch, значит, жанра вообще нет в базе
                return [], count_all
            # Сохраняем жанр  в кеш
            person_dict.append(count_all)
            await self._put_to_cache(
                key, json.dumps(person_dict), PERSON_CACHE_EXPIRE_IN_SECONDS
            )
        else:
            count_all = person_json[-1]
            person_json.pop(-1)
            person = await self.prepare_data(person_json, Person)
        return person, count_all

    async def _get_person_from_elastic(self) -> List[Person]:
        try:
            doc = await self.elastic.search(
                index="persons",
                body={
                    "query": {"match_all": {}},
                    "size": self.params.page_size,
                    "from": self.params.page_number - 1,
                },
            )
            count_all = doc["hits"]["total"]["value"]
        except NotFoundError:
            return []
        print(doc["hits"]["hits"])
        models = parse_obj_as(list[Person], [i["_source"] for i in doc["hits"]["hits"]])
        person_dict = [mod.dict() for mod in models]
        return models, person_dict, count_all

    async def search_persons(
        self, index: str, query: str, fields: list
    ) -> List[Dict[str, Union[str, List[Dict[str, List[str]]]]]]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        key = "search_" + query
        person_json = await self._get_from_cache(key)
        if not person_json:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            films = await self.search(
                index="persons", query=query, fields=fields, find_field="full_name"
            )
            if not films:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return []
            # Сохраняем фильм  в кеш
            await self._put_to_cache(
                key, json.dumps(films), PERSON_CACHE_EXPIRE_IN_SECONDS
            )
        else:
            films = person_json
        return films


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
