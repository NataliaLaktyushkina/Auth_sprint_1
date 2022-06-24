import asyncio
from dataclasses import dataclass
from typing import Optional

import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch

from utils import settings

app_settings = settings.get_settings()

@dataclass
class HTTPResponse:
    body: dict
    headers: [str]
    status: int


@pytest.fixture(scope='session')
async def session():
    async with aiohttp.ClientSession() as session:
        yield session


@pytest.fixture(scope='session')
async def redis_client():
    client = await aioredis.create_redis_pool((app_settings.REDIS_HOST, app_settings.REDIS_PORT), minsize=10, maxsize=20)
    # Clean cache
    client.flushall()
    yield client
    await client.wait_closed()


@pytest.fixture(scope='session', autouse=True)
def event_loop():
    """Create an instance of the default event loop for each test case."""
    # loop = asyncio.get_event_loop_policy().new_event_loop()
    # yield loop
    # loop.close()
    yield asyncio.get_event_loop()


@pytest.fixture
def make_get_request(session):
    async def inner(method: str, params: Optional[dict] = None) -> HTTPResponse:
        params = params or {}
        url = app_settings.URL_API_V1 + method
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner


