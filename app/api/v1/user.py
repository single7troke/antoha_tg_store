import pickle
from typing import Any, Dict

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from starlette import status

from db.redis import get_redis_db, RedisDB
from core.cache_key_constructor import CacheKeyConstructor
from core.utils import bytes_to_user
from core.config import get_config

router = APIRouter()
config = get_config()
security = HTTPBasic()


@router.get("/{user_id}", description="Return user")
async def get_user(user_id: int, request: Request, cache: RedisDB = Depends(get_redis_db)):
    key = CacheKeyConstructor.user(user_id)
    obj_from_cache = await cache.get(key)
    result = pickle.loads(obj_from_cache)
    return result


@router.get("/", description="Return user")
async def get_user_list(request: Request, cache: RedisDB = Depends(get_redis_db)):
    user_keys = await cache.find_all_with('user')
    result = dict()
    for key in user_keys:
        user = await cache.get(key)
        result[key.decode()] = bytes_to_user(user)

    return result
