import pytest
import requests
import uuid

from tests.functional.settings  import settings
from tests.functional.utils.queries import  SCHEMA_JSON_PERSONS, SCHEMA_JSON_MOVIES
from tests.functional.src.mixin import good_test_id,bad_test_id
#  Название теста должно начинаться со слова `test_`
#  Любой тест с асинхронными вызовами нужно оборачивать декоратором `pytest.mark.asyncio`, который следит за запуском и работой цикла событий. 
pytestmark = pytest.mark.asyncio

@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'uuid':'6da628ea-4bd1-412a-8b09-cc4d27a1015f'},
            {'status': 200, 'uuid': '6da628ea-4bd1-412a-8b09-cc4d27a1015f'}
        )
    ]
)
async def test_id_person(query_data,expected_answer,es_delete_data,es_write_data,aiohttp_get):
    await good_test_id(query_data,
                expected_answer,
                es_delete_data,
                es_write_data,
                aiohttp_get,
                SCHEMA_JSON_PERSONS,
                settings.es_index_persons,
                [
                {
                    "uuid": query_data['uuid'],
                    "full_name": "Mazzy Star",
                    "films": [{"uuid":"6da628ea-4bd1-412a-8b09-cc4d27a1025f","roles": ["director","writer"]}]
                    }
                    ],
                settings.check_url_id_persons  )
    url = settings.check_url_id_persons
    status, body = await aiohttp_get(url,'')
    assert status == expected_answer['status']
    assert body["items"][0]['uuid'] == expected_answer['uuid']

    requests.put(f"http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}" + "/"+settings.es_index_movies, json=SCHEMA_JSON_MOVIES)
    await es_delete_data(settings.es_index_movies)
    # 1. Генерируем данные для ES
    es_data = [{
            "uuid": '6da628ea-4bd1-412a-8b09-cc4d27a1025f',
            "title": "Star",
            "imdb_rating": 10,
        }]
    # 2. Отрпавляем данные для ES
    await es_write_data(es_data,settings.es_index_movies)
    url = settings.check_url_id_persons + query_data['uuid'] + '/films'
    status, body = await aiohttp_get(url,'')
    # 4. Проверяем ответ 
    assert status == expected_answer['status']
    assert body[0]['uuid'] == '6da628ea-4bd1-412a-8b09-cc4d27a1025f'


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
           {'uuid':'6da628ea-4bd1-412a-8b09-cc4d27a1013a'},
            {'status': 404, 'detail': 'person not found'}
        ),
    ]
)
async def test_bad_genre(query_data,expected_answer,es_delete_data,es_write_data,aiohttp_get):
    await bad_test_id(query_data,
                  expected_answer,
                  es_delete_data,
                  es_write_data,
                  aiohttp_get,
                  SCHEMA_JSON_PERSONS,
                  settings.es_index_persons,
                 [
                {
                    "uuid": '6da628ea-4bd1-412a-8b09-cc4d27a1015f',
                    "full_name": "Mazzy Star",
                    "films": [{"uuid":"6da628ea-4bd1-412a-8b09-cc4d27a1025f","roles": ["director","writer"]}]
                    }
                    ],
                  settings.check_url_id_persons)
    

@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'query':{'page_number':1,'page_size':1}},
            {'status': 200,'length': settings.create_number,'page_number':1,'page_size':1},
        ),
        (
            {'query':{'page_number':2,'page_size':2}},
            {'status': 200,'length': settings.create_number,'page_number':2,'page_size':2},
        )
    ]
)
async def test_paginate_person(query_data,expected_answer,es_delete_data,es_write_data,aiohttp_get):
    requests.put(f"http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}" + "/"+ settings.es_index_persons, json=SCHEMA_JSON_PERSONS)
    await es_delete_data(settings.es_index_persons)
    es_data = [{
            "uuid": str(uuid.uuid4()),
            "full_name": "Mazzy Star " + str(i),
            "films": [{"uuid":"6da628ea-4bd1-412a-8b09-cc4d27a1025f","roles": ["director","writer"]}]
        } for i in range(settings.create_number)]
    await es_write_data(es_data,settings.es_index_persons)

    url = settings.check_url_id_persons
    status, body = await aiohttp_get(url,query_data['query'])
    assert status == expected_answer['status']
    assert body['total'] == expected_answer['length']
    assert body['page_size'] == expected_answer['page_size']
    assert body['page_number'] == expected_answer['page_number']
    assert len(body['items']) == expected_answer['page_size']