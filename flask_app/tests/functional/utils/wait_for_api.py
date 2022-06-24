import asyncio
from http import HTTPStatus

import aiohttp
import backoff

from logger import logger
from settings import get_settings


settings = get_settings()


@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_time=60)
async def get_url(url):
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.get(url) as response:
            return response.status

loop = asyncio.get_event_loop()
logger.info('Waiting for Auth API')
status = loop.run_until_complete(get_url(settings.SERVICE_URL))
if status == HTTPStatus.OK:
    logger.info('Auth API is started')

