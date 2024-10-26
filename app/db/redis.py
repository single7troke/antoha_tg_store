import logging

from aioredis import Redis
from aioredis.exceptions import ConnectionError
from fastapi import Depends
from tenacity import retry, stop_after_delay, RetryCallState, retry_if_exception_type, wait_exponential, after_log

from db.abstract_cache import AbstractCache
from core.config import Config

config = Config()

logging.basicConfig(format="%(asctime)s %(message)s",
                    datefmt="%m/%d/%Y %I:%M:%S %p %Z",
                    level=config.log_lvl)
logger = logging.getLogger(__name__)
redis: Redis | None = None


async def get_redis() -> Redis:
    return redis


def no_connection(retry_state: RetryCallState):
    return ConnectionError


class RedisDB(AbstractCache):
    def __init__(self, client: Redis):
        self.redis = client

    @retry(retry=retry_if_exception_type(ConnectionError),
           wait=wait_exponential(),
           stop=stop_after_delay(15),
           after=after_log(logger, logging.INFO),
           retry_error_callback=no_connection)
    async def get(self, user_id: str):
        data = await self.redis.get(name=user_id)
        return data

    @retry(retry=retry_if_exception_type(ConnectionError),
           wait=wait_exponential(),
           stop=stop_after_delay(15),
           after=after_log(logger, logging.INFO),
           retry_error_callback=no_connection)
    async def list(self):
        data = await self.redis.keys(pattern="*")
        return data

    @retry(retry=retry_if_exception_type(ConnectionError),
           wait=wait_exponential(),
           stop=stop_after_delay(15),
           after=after_log(logger, logging.INFO),
           retry_error_callback=no_connection)
    async def create(self, user_id: str, data: bytes) -> None:
        data = await self.redis.set(name=user_id, value=data)
        return data

    async def update(self, user_id: str, data: bytes) -> None:
        data = await self.create(name=user_id, mapping=data)
        return data

    @retry(retry=retry_if_exception_type(ConnectionError),
           wait=wait_exponential(),
           stop=stop_after_delay(15),
           after=after_log(logger, logging.INFO),
           retry_error_callback=no_connection)
    async def delete(self, user_id: str) -> None:
        data = await self.redis.delete(user_id)
        return data

    @retry(retry=retry_if_exception_type(ConnectionError),
           wait=wait_exponential(),
           stop=stop_after_delay(15),
           after=after_log(logger, logging.INFO),
           retry_error_callback=no_connection)
    async def increase(self, key: str) -> int:
        data = await self.redis.incr(key, 1)
        return data

    @retry(retry=retry_if_exception_type(ConnectionError),
           wait=wait_exponential(),
           stop=stop_after_delay(15),
           after=after_log(logger, logging.INFO),
           retry_error_callback=no_connection)
    async def find_all_with(self, key_part: str) -> list:
        result = list()
        async for key in self.redis.scan_iter(f'{key_part}*'):
            result.append(key)

        return result


def get_redis_db(redis: Redis = Depends(get_redis)):
    return RedisDB(redis)
