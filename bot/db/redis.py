import logging

from aioredis import Redis
from aioredis.exceptions import ConnectionError
from tenacity import retry, stop_after_delay, RetryCallState, retry_if_exception_type, wait_exponential, after_log

from db.abstract_cache import AbstractCache
from core import Config

config = Config()
logger = logging.getLogger(__name__)
redis: Redis | None = None


def get_redis() -> Redis:
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
    async def get(self, object_id: str):
        data = await self.redis.get(name=object_id)
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
    async def create(self, object_id: str, data: dict | bytes) -> None:
        data = await self.redis.set(name=object_id, value=data)
        return data

    async def update(self, object_id: str, data: dict | bytes) -> None:
        data = await self.create(object_id, data)
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


redis_db: RedisDB | None = None


def get_redis_db():
    global redis_db
    connection = get_redis()
    if not redis:
        raise Exception('No Redis connection')  # TODO это временное решение, нужно переделать
    if not redis_db:
        redis_db = RedisDB(connection)
    return redis_db
