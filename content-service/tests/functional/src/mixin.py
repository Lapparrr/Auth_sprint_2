import uuid

import requests


from tests.functional.settings  import settings


async def good_test_id(query_data,expected_answer,es_delete_data,es_write_data,aiohttp_get,SCHEMA_JSON,index,es_data,check_url_id):
    status, body = await prepare_id(query_data,
                  es_delete_data,
                  es_write_data,
                  aiohttp_get,
                  SCHEMA_JSON,
                  index,
                  es_data,
                  check_url_id)

    # 2. Проверяем ответ 
    assert status == expected_answer['status']
    assert body['uuid'] == expected_answer['uuid']



async def prepare_id(query_data,es_delete_data,es_write_data,aiohttp_get,SCHEMA_JSON,index,es_data,check_url_id):
    requests.put(f"http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}" + "/"+index, json=SCHEMA_JSON)
    await es_delete_data(index)
    # 1. Отрпавляем данные для ES
    await es_write_data(es_data,index)

    url = check_url_id + query_data['uuid']
    status, body = await aiohttp_get(url,'')
    return status, body


async def bad_test_id(query_data,expected_answer,es_delete_data,es_write_data,aiohttp_get,SCHEMA_JSON,index,es_data,check_url_id):
    status, body = await prepare_id(query_data,
                  es_delete_data,
                  es_write_data,
                  aiohttp_get,
                  SCHEMA_JSON,
                  index,
                  es_data,
                  check_url_id)

    # 2. Проверяем ответ 
    assert status == expected_answer['status']
    assert body['detail'] == expected_answer['detail']



async def prepare_with_query(query_data,es_delete_data,es_write_data,aiohttp_get,SCHEMA_JSON,index,es_data,check_url_id):
    requests.put(f"http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}" + "/"+index, json=SCHEMA_JSON)
    await es_delete_data(index)
    # 1. Отрпавляем данные для ES
    await es_write_data(es_data,index)
    url = check_url_id
    query = query_data['query']
    status, body = await aiohttp_get(url,query)
    return status, body

async def sort_test(query_data,expected_answer,es_delete_data,es_write_data,aiohttp_get,SCHEMA_JSON,index,es_data,check_url_id):
    status, body = await prepare_with_query(query_data,
                  es_delete_data,
                  es_write_data,
                  aiohttp_get,
                  SCHEMA_JSON,
                  index,
                  es_data,
                  check_url_id)

    # 2. Проверяем ответ 
    assert status == expected_answer['status']
    assert body['total'] == expected_answer['length']
    return body