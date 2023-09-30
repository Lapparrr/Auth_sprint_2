import pytest


from tests.functional.settings  import settings
from tests.functional.utils.queries import  SCHEMA_JSON_GENRES
from tests.functional.src.mixin import good_test_id,bad_test_id
#  Название теста должно начинаться со слова `test_`
#  Любой тест с асинхронными вызовами нужно оборачивать декоратором `pytest.mark.asyncio`, который следит за запуском и работой цикла событий. 
pytestmark = pytest.mark.asyncio

@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'uuid':'6da628ea-4bd1-412a-8b09-cc4d27a1014f'},
            {'status': 200, 'uuid': '6da628ea-4bd1-412a-8b09-cc4d27a1014f'}
        )
    ]
)
async def test_good_genre(query_data,expected_answer,es_delete_data,es_write_data,aiohttp_get):
    await good_test_id(query_data,
                expected_answer,
                es_delete_data,
                es_write_data,
                aiohttp_get,
                SCHEMA_JSON_GENRES,
                settings.es_index_genres,
            [{
                "uuid": query_data['uuid'],
                "name": "western",
                "films":[
                    {
                        "id_film":'6da628ea-4bd1-412a-8b09-cc4d27a1010f',
                        "rating":10.0
                    }
                ]
                }],
                settings.check_url_id_genres )

    url = settings.check_url_id_genres
    status, body = await aiohttp_get(url,'')
    assert status == expected_answer['status']
    assert body[0]['uuid'] == expected_answer['uuid']

@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'uuid':'6da628ea-4bd1-412a-8b09-cc4d27a1013a'},
            {'status': 404, 'detail': 'genre not found'}
        ),
    ]
)
async def test_bad_genre(query_data,expected_answer,es_delete_data,es_write_data,aiohttp_get):
    await bad_test_id(query_data,
                  expected_answer,
                  es_delete_data,
                  es_write_data,
                  aiohttp_get,
                  SCHEMA_JSON_GENRES,
                  settings.es_index_genres,
                 [{
                "uuid": '6da628ea-4bd1-412a-8b09-cc4d27a1014f',
                "name": "western",
                "films":[
                    {
                        "id_film":'6da628ea-4bd1-412a-8b09-cc4d27a1010f',
                        "rating":10.0
                    }
                ]
                }],
                  settings.check_url_id_genres)