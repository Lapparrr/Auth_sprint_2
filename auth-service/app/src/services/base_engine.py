from abc import ABC, abstractmethod
from elasticsearch import AsyncElasticsearch, NotFoundError


class AsyncSearchEngine(ABC):
    @abstractmethod
    async def get_by_id(self, index: str, id: str, data_class: any):
        pass

    @abstractmethod
    async def get_by_ids(self, index: str, search_body: dict, data_class: any):
        pass


class ElasticAsyncSearchEngine(AsyncSearchEngine):
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(self, index: str, id: str, data_class: any):
        try:
            doc = await self.elastic.get(index=index, id=id)
        except NotFoundError:
            return None
        return data_class(**doc['_source'])

    async def get_by_ids(self, index: str, search_body: dict, data_class: any):
        try:
            doc = await self.elastic.search(
                index=index,
                query=search_body['query'],
                size=search_body['size'],
                from_=search_body['from'],
                sort=search_body['sort'],
            )
        except NotFoundError:
            return None
        return [data_class(**el['_source']) for el in doc['hits']['hits']]
