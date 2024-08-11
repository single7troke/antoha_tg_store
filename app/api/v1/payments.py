import pickle
from typing import Any, Dict

from fastapi import APIRouter, Depends, Request

from db.redis import get_redis_db, RedisDB
from core.cache_key_constructor import CacheKeyConstructor

router = APIRouter()


@router.post("", description="Payment callback")
async def payment_callback(data: Dict[Any, Any], cache: RedisDB = Depends(get_redis_db)):

    payment_data = data['object']
    print(payment_data)
    user_id = payment_data['metadata']['tg_user_id']
    course_id = int(payment_data['metadata']['course_id'])
    key = CacheKeyConstructor.user(user_id)

    user_from_cache = await cache.get(key)
    user_from_cache = pickle.loads(user_from_cache)

    if payment_data['status'] == 'canceled':
        user_from_cache.courses[course_id].pop(course_id, None)
        print('Проблемы с оплатой')
        print(payment_data['cancellation_details']['reason'])
        return {'status': 'ok'}

    user_from_cache.courses[course_id].payment_data = payment_data
    await cache.create(key, pickle.dumps(user_from_cache))

    return {'status': 'ok'}


@router.get("", description="Return user's role if user exists, else False")
async def get_user(request: Request, cache: RedisDB = Depends(get_redis_db)):
    print(cache.redis)
    data = await cache.get('key')
    data = pickle.loads(data)

    return {
        # 'qwer': request.headers,
        #     'body': await request.body(),
        #     'items': request.items,
            'data': data,
            }
