import asyncio

import aioredis
import backoff

from logger import logger
from settings import get_settings

settings = get_settings()


@backoff.on_predicate(backoff.constant)
async def check_redis():
    redis_client = await aioredis.create_redis_pool((settings.REDIS_HOST, settings.REDIS_PORT), minsize=10, maxsize=20)
    return await redis_client.ping()

loop = asyncio.get_event_loop()
logger.info('Waiting for redis')
status = loop.run_until_complete(check_redis())
if status:
    logger.info('Redis is started')
