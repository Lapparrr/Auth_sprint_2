import uuid

import pytest
import requests
from faker import Faker

from tests.functional.settings  import settings
from tests.functional.utils.queries import SCHEMA_JSON_MOVIES
from tests.functional.src.mixin import good_test_id,bad_test_id,sort_test
#  Название теста должно начинаться со слова `test_`
#  Любой тест с асинхронными вызовами нужно оборачивать декоратором `pytest.mark.asyncio`, который следит за запуском и работой цикла событий. 

pytestmark = pytest.mark.asyncio

@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'uuid':'6da628ea-4bd1-412a-8b09-cc4d27a1013f'},
            {'status': 200, 'uuid': '6da628ea-4bd1-412a-8b09-cc4d27a1013f'}
        ),
    ]
)
async def test_good_film(query_data,expected_answer,es_delete_data,es_write_data,aiohttp_get):
    await good_test_id(query_data,
                  expected_answer,
                  es_delete_data,
                  es_write_data,
                  aiohttp_get,
                  SCHEMA_JSON_MOVIES,
                  settings.es_index_movies,
                 [{
                    "uuid": query_data['uuid'],
                    "title": "Star",
                    "imdb_rating": 10,
                 }],
                  settings.check_url_id_film)


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'uuid':'6da628ea-4bd1-412a-8b09-cc4d27a1013a'},
            {'status': 404, 'detail': 'film not found'}
        ),
    ]
)
async def test_bad_film(query_data,expected_answer,es_delete_data,es_write_data,aiohttp_get):
    await bad_test_id(query_data,
                  expected_answer,
                  es_delete_data,
                  es_write_data,
                  aiohttp_get,
                  SCHEMA_JSON_MOVIES,
                  settings.es_index_movies,
                 [{
                    "uuid": '6da628ea-4bd1-412a-8b09-cc4d27a1013f',
                    "title": "Star",
                    "imdb_rating": 10,
                 }],
                  settings.check_url_id_film)


es_data = [{
        "uuid": str(uuid.uuid4()),
        "title": "Star " + str(i),
        "imdb_rating": i,
        "genre": [{
            "name": "Documentary_" + str(i),
            "uuid": str(uuid.uuid4())
            }]
    } for i in range(settings.create_number)]


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'query': {'sort':'imdb_rating'}},
                {'status': 200, 'length': settings.create_number ,'status_sort':0}
        ),
    ]
)
async def test_films_sort_up(query_data,expected_answer,es_delete_data,es_write_data,aiohttp_get):
    status_sort =  0
    body = await sort_test(query_data,
                        expected_answer,
                  es_delete_data,
                  es_write_data,
                  aiohttp_get,
                  SCHEMA_JSON_MOVIES,
                  settings.es_index_movies,
                  es_data,
                  settings.check_url_id_film)
    for id in range(len(body['items'])-1):
        #Здесь без if не придумал, но он не должен сильно усложнять код
        if body['items'][id]['imdb_rating'] >body['items'][id+1]['imdb_rating']:
            status_sort = 1
    assert status_sort == expected_answer['status_sort']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'query': {'sort':'-imdb_rating'}},
            {'status': 200, 'length': settings.create_number ,'status_sort':0}
        ),
    ]
)
async def test_films_sort_down(query_data,expected_answer,es_delete_data,es_write_data,aiohttp_get):
    status_sort =  0
    es_data = [{
            "uuid": str(uuid.uuid4()),
            "title": "Star " + str(i),
            "imdb_rating": i,
            "genre": [{
                "name": "Documentary_" + str(i),
                "uuid": str(uuid.uuid4())
                }]
        } for i in range(settings.create_number)]
    body = await sort_test(query_data,
                    expected_answer,
                  es_delete_data,
                  es_write_data,
                  aiohttp_get,
                  SCHEMA_JSON_MOVIES,
                  settings.es_index_movies,
                  es_data,
                  settings.check_url_id_film)
    for id in range(len(body['items'])-1):
        #Здесь без if не придумал, но он не должен сильно усложнять код
        if body['items'][id]['imdb_rating'] < body['items'][id+1]['imdb_rating']:
            status_sort = 1
    assert status_sort == expected_answer['status_sort']
 

@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'query': {'genre':str(uuid.uuid4())}},
                {'status': 200, 'length': 1}
        ),
    ]
)
async def test_films_genre(query_data,expected_answer,es_delete_data,es_write_data,aiohttp_get):
    es_data.append({
                "uuid": str(uuid.uuid4()),
                "title": "Star " ,
                "imdb_rating": 0,
                "genre": [{
                    "name": "Documentary_",
                    "uuid": query_data['query']['genre']}]})
    await sort_test(query_data,
                    expected_answer,
                  es_delete_data,
                  es_write_data,
                  aiohttp_get,
                  SCHEMA_JSON_MOVIES,
                  settings.es_index_movies,
                  es_data,
                  settings.check_url_id_film)


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
               {'query': {'genre':str(uuid.uuid4()),'sort':'-imdb_rating'}},
                {'status': 200, 'length': 1,'status_sort':0}
        ),
    ]
)
async def test_films_genre_sort_up(query_data,expected_answer,es_delete_data,es_write_data,aiohttp_get):
    status_sort =  0
    es_data.append({
                "uuid": str(uuid.uuid4()),
                "title": "Star " ,
                "imdb_rating": 0,
                "genre": [{
                    "name": "Documentary_",
                    "uuid": query_data['query']['genre']}]})
    body = await sort_test(query_data,
                    expected_answer,
                  es_delete_data,
                  es_write_data,
                  aiohttp_get,
                  SCHEMA_JSON_MOVIES,
                  settings.es_index_movies,
                  es_data,
                  settings.check_url_id_film)
    for id in range(len(body['items'])-1):
        #Здесь без if не придумал, но он не должен сильно усложнять код
        if body['items'][id]['imdb_rating'] < body['items'][id+1]['imdb_rating']:
            status_sort = 1
    assert status_sort == expected_answer['status_sort']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'query': {'genre':str(uuid.uuid4()),'sort':'imdb_rating'}},
            {'status': 200, 'length': 1,'status_sort':0}
        ),
    ]
)
async def test_films_genre_sort_down(query_data,expected_answer,es_delete_data,es_write_data,aiohttp_get):
    status_sort =  0
    es_data.append({
                "uuid": str(uuid.uuid4()),
                "title": "Star " ,
                "imdb_rating": 0,
                "genre": [{
                    "name": "Documentary_",
                    "uuid": query_data['query']['genre']}]})
    body = await sort_test(query_data,
                    expected_answer,
                  es_delete_data,
                  es_write_data,
                  aiohttp_get,
                  SCHEMA_JSON_MOVIES,
                  settings.es_index_movies,
                  es_data,
                  settings.check_url_id_film)
    for id in range(len(body['items'])-1):
        #Здесь без if не придумал, но он не должен сильно усложнять код
        if body['items'][id]['imdb_rating'] >body['items'][id+1]['imdb_rating']:
            status_sort = 1
    assert status_sort == expected_answer['status_sort']



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
        ),
    ]
)
async def test_paginate_film(query_data,expected_answer,es_delete_data,es_write_data,aiohttp_get):
    requests.put(f"http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}" + "/"+ settings.es_index_movies, json=SCHEMA_JSON_MOVIES)
    await es_delete_data(settings.es_index_movies)
    fake = Faker()
    es_data = [{
            "uuid": str(uuid.uuid4()),
            "title": "Star " + str(i),
            "imdb_rating": fake.random.randint(10, 100) / 10,
        } for i in range(settings.create_number)]
    # 1. Отрпавляем данные для ES
    await es_write_data(es_data,settings.es_index_movies)

    url = settings.check_url_id_film
    status, body = await aiohttp_get(url,query_data['query'])
    assert status == expected_answer['status']
    assert body['total'] == expected_answer['length']
    assert body['page_size'] == expected_answer['page_size']
    assert body['page_number'] == expected_answer['page_number']
    assert len(body['items']) == expected_answer['page_size']


