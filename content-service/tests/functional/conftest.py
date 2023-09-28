import json

import asyncio
from typing import Optional
from typing import List
import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch


from tests.functional.settings import settings


@pytest.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=[f"http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}"])
    yield client
    await client.close()


@pytest.fixture
def es_write_data(es_client):
    async def inner(data: List[dict],index):
        bulk_query = list()
        for row in data:
            bulk_query.extend(
                [
                 json.dumps({"index": {"_index": index, "_id": row["uuid"]}}),
                json.dumps(row),
                ]
            )
        str_query = '\n'.join(bulk_query) + '\n'
        response = await es_client.bulk(operations=str_query, refresh=True)
        await es_client.close()
        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')
    return inner 

@pytest.fixture
def es_delete_data(es_client):
    async def inner(index):
        await es_client.delete_by_query(
            index=[index],
            body={"query": {"match_all": {}}},)
        await es_client.close() 
    return inner 


@pytest.fixture(scope='session')
async def aiohttp_client():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def aiohttp_get(aiohttp_client):
    async def inner(
        endpoint: str,
        query: Optional[dict] = None,
    ):
        url = f'{settings.service_url}{endpoint}'
        async with aiohttp_client.get(url, params=query) as response:
            body = await response.json()
            status = response.status
        return (status, body)
        
    return inner

@pytest.fixture(scope="session")
def event_loop():
    """Avoid RuntimeError: Event loop is closed"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()