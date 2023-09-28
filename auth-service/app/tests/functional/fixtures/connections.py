import pytest
import pytest_asyncio
from httpx import AsyncClient
from redis import Redis

from src.main import app
from src.main import startup, shutdown
from tests.functional.settings import test_settings
from tests.functional.utils.backoff import backoff


@backoff()
@pytest_asyncio.fixture
async def client():
    await startup()
    connection = f"https://{test_settings.service_url}"
    async with AsyncClient(app=app, base_url=connection) as client:
        yield client
    await shutdown()


@backoff()
@pytest.fixture
def redis_client():
    redis_client = Redis(host=test_settings.redis_host, port=test_settings.redis_port)
    yield redis_client
    redis_client.close()
