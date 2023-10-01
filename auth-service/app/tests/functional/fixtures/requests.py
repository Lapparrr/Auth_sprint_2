from http import HTTPStatus

import pytest_asyncio


@pytest_asyncio.fixture
async def auth_token(client):
    print(f'🔴  response ')
    response = await client.post(
        "v1/auth/token",
        json={"username": "superuser@gmail.com", "password": "superuser"},
    )

    assert response.status_code == 200
    token = response.json()["access_token"]
    return token


@pytest_asyncio.fixture
def make_get_request(client):
    async def inner(api_url: str, query_data: dict):
        response = await client.get(url=api_url, params=query_data)
        if response.status_code != HTTPStatus.OK:
            raise Exception(
                f'Ошибка EndPoint FastApi {response.status_code} api_url={api_url} query_data {query_data}'
            )
        return response.json()

    return inner


@pytest_asyncio.fixture
def make_post_request(client):
    async def inner(api_url: str, query_data: dict):
        response = await client.post(url=api_url, json=query_data)
        if response.status_code != HTTPStatus.OK:
            raise Exception(
                f'Ошибка EndPoint FastApi {response.status_code} api_url={api_url} query_data {query_data}'
            )
        return response.json()

    return inner
