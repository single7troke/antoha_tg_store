import pickle
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from starlette import status

from db.redis import get_redis_db, RedisDB
from core.cache_key_constructor import CacheKeyConstructor
from core.utils import bytes_to_user, send_message, send_sell_notification_to_admins, delete_message
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
        data: Dict[Any, Any],
        cache: RedisDB = Depends(get_redis_db),
):
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
        if price_type == 'extended':
            await cache.increase('extended_course_sold_quantity')
        user.courses[course_id].paid = price_type
        user.courses[course_id].captured_at = payment_data['captured_at']
        user.courses[course_id].payment_ids[price_type] = payment_data['id']
        await cache.create(key, pickle.dumps(user))
        text = ('Спасибо за покупку!'
                f'\nЧек отправлен на email: {payment_data["metadata"]["email"]}'
                '\nНажмите на /menu, затем "Курс"')
        msg_id = await send_message(user_id, text)
        if msg_id:
            await delete_message(user_id, msg_id - 1)
        if user_id not in config.tg_admin_list:
            await send_sell_notification_to_admins(price_type, user_id)

    return {'status': 'ok'}
