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


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = config.payment.yookassa_account_id
    correct_password = config.payment.yookassa_secret_key

    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@router.post("", description="Payment callback")  # TODO сделать ограничение на доступ к этому хендлеру
async def payment_callback(
        data: Dict[Any, Any],
        cache: RedisDB = Depends(get_redis_db),
        credentials: HTTPBasicCredentials = Depends(verify_credentials)
):
    payment_data = data['object']
    print(payment_data)
    user_id = payment_data['metadata']['tg_user_id']
    price_type = payment_data['metadata']['price_type']
    ts = payment_data['metadata']['ts']
    course_id = int(payment_data['metadata']['course_id'])

    key = CacheKeyConstructor.user(user_id)

    data_from_cache = await cache.get(key)
    user = bytes_to_user(data_from_cache)

    user.courses[course_id].payment_data = payment_data
    await cache.create(key, pickle.dumps(user))

    return {'status': 'ok'}


# @router.get("", description="Return user's role if user exists, else False")
# async def get_user(request: Request, cache: RedisDB = Depends(get_redis_db)):
#     print(cache.redis)
#     data = await cache.get('key')
#     data = pickle.loads(data)
#
#     return {
#         # 'qwer': request.headers,
#         #     'body': await request.body(),
#         #     'items': request.items,
#             'data': data,
#             }
