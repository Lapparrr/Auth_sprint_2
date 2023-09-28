import json
from elasticsearch import NotFoundError
from typing import List, Dict, Union


class MixinService:
    async def _get_from_elastic_by_id(self, index, id: str, some_class):
        try:
            doc = await self.elastic.get(index=index, id=id)
        except NotFoundError:
            return None
        return some_class(**doc["_source"])

    async def _put_to_cache(self, key, data, keep_time):
        # Сохраняем данные о жанре, используя команду set
        # Выставляем время жизни кеша — keep_time
        # https://redis.io/commands/set/
        await self.redis.set(key, data, keep_time)

    async def _get_from_cache(self, key):
        # Try to get the data from the cache using the get command
        data = await self.redis.get(key)
        if not data:
            return None
        # Decode the data and load it as a JSON object
        my_new_string_value = data.decode("utf-8")
        my_json = json.loads(my_new_string_value)

        return my_json

    async def prepare_data(self, my_json, some_class):
        # Check if the JSON object is a list, and then unpack it using ** for each item
        if isinstance(my_json, list):
            return [some_class(**item) for item in my_json]
        else:
            return some_class(**my_json)

    async def search(
        self, index: str, query: str, fields: List[str], find_field: str
    ) -> List[Dict[str, Union[str, float]]]:
        count_movies = await self.elastic.search(index=index)
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": [find_field],
                    "fuzziness": "auto",
                }
            },
            "sort": [{"_score": "desc"}],
            "_source": fields,
            "size": count_movies["hits"]["total"]["value"] - 1,
        }

        response = await self.elastic.search(index=index, body=body)
        hits = response["hits"]["hits"]
        search_results = [hit["_source"] for hit in hits]
        return search_results
