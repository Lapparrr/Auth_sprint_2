import uuid

import pytest
import requests
from faker import Faker

from tests.functional.settings  import settings
from tests.functional.utils.queries import SCHEMA_JSON_MOVIES, SCHEMA_JSON_PERSONS
#  Название теста должно начинаться со слова `test_`
#  Любой тест с асинхронными вызовами нужно оборачивать декоратором `pytest.mark.asyncio`, который следит за запуском и работой цикла событий. 

pytestmark = pytest.mark.asyncio

@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'query':{'query': 'Star','page':1,'size':settings.create_number-1}},
                {'status': 200, 'length': settings.create_number-1}
        ),
         (
                {'query':{'query': 'Star','page':2,'size':50}},
                {'status': 200, 'length': 0}
        ),
         (
                {'query':{'query': 'Star','page':1,'size':1}},
                {'status': 200, 'length': 1}
        ),
        (
                {'query':{'query': 'Mashed potato'}},
                {'status': 200, 'length': 0}
        ),
         (
                {'query':{'query': 'sTaR'}},
                {'status': 200, 'length': settings.create_number-1}
        ),
    ]
)
async def test_search_films(query_data,expected_answer,es_delete_data,es_write_data,aiohttp_get):
    requests.put(f"http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}" + "/"+settings.es_index_movies, json=SCHEMA_JSON_MOVIES)
    await es_delete_data(settings.es_index_movies)
    # 1. Генерируем данные для ES
    fake = Faker()
    es_data = [{
            "uuid": str(uuid.uuid4()),
            "title": "Star " + str(i),
            "imdb_rating": fake.random.randint(10, 100) / 10,
        } for i in range(settings.create_number)]
    # 2. Отрпавляем данные для ES
    await es_write_data(es_data,settings.es_index_movies)
    

    url = settings.check_url_search_film

    status, body = await aiohttp_get(url,query_data['query'])
    # 4. Проверяем ответ 

    assert status == expected_answer['status']
    assert  len(body['items']) == expected_answer['length']




@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
         (
                {'query':{'query': 'Star','page':1,'size':settings.create_number-1}},
                {'status': 200, 'length': settings.create_number-1}
        ),
         (
                {'query':{'query': 'Star','page':2,'size':50}},
                {'status': 200, 'length': 0}
        ),
         (
                {'query':{'query': 'Star','page':1,'size':1}},
                {'status': 200, 'length': 1}
        ),
        (
                {'query':{'query': 'Potato'}},
                {'status': 200, 'length': 0}
        ),
         (
                {'query':{'query': 'StAr'}},
                {'status': 200, 'length': settings.create_number-1}
        ),
    ]
)
async def test_search_person(query_data,expected_answer,es_delete_data,es_write_data,aiohttp_get):
    requests.put(f"http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}" + "/"+settings.es_index_persons, json=SCHEMA_JSON_PERSONS)
    await es_delete_data(settings.es_index_persons)
    # 1. Генерируем данные для ES
    es_data = [{
            "uuid": str(uuid.uuid4()),
            "full_name": "Mazzy Star " + str(i)
        } for i in range(settings.create_number)]
    # 2. Отрпавляем данные для ES
    await es_write_data(es_data,settings.es_index_persons)
    

    url = settings.check_url_search_person
    status, body = await aiohttp_get(url,query_data['query'])
    # 4. Проверяем ответ 

    assert status == expected_answer['status']
    assert  len(body['items']) == expected_answer['length']