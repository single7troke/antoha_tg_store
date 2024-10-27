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


@router.post("/yookassa_callback", description="Yookassa callback")  # TODO сделать ограничение на доступ к этому хендлеру
async def payment_callback(
        request: Request,
        data: Dict[Any, Any],
        cache: RedisDB = Depends(get_redis_db),
):
    domain = request.url.hostname
    full_url = str(request.url)
    print(domain)
    print(full_url)

    payment_data = data['object']
    user_id = payment_data['metadata']['tg_id']
    price_type = payment_data['metadata']['price_type']
    ts = payment_data['metadata']['ts']
    course_id = int(payment_data['metadata']['course_id'])

    key = CacheKeyConstructor.user(user_id)

    data_from_cache = await cache.get(key)
    user = bytes_to_user(data_from_cache)

    if user.courses[course_id].paid:
        # TODO если статус succeeded нужна проверка что оплатил пользователь
        #  и если он оплатил курс еще раз(
        #  это возможно если в браузере осталась ссылка на оплату рассширенного курса, а он платалил обычный,
        #  а потом оплатил еще и расширенный),то вернуть платеж
        return {'status': 'ok'}

    if payment_data['status'] == 'succeeded':
        # TODO либо тут отменять второй созданный платеж если он создан и если это вообще можно сделать.
        # TODO отслеживать покупку расширенного курса
        user.courses[course_id].paid = price_type
        user.courses[course_id].payment_ids[price_type] = payment_data['id']
        await cache.create(key, pickle.dumps(user))

    return {'status': 'ok'}
