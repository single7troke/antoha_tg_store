import time
import uuid
from typing import Union

from yookassa import Payment, Configuration
from yookassa.domain.response import PaymentResponse

from core import get_config
from models import Course

config = get_config()

Configuration.account_id = config.payment.yookassa_account_id
Configuration.secret_key = config.payment.yookassa_secret_key


def create_payment(user_id: Union[str, int], course: Course, price_type: str) -> PaymentResponse:
    u_id = uuid.uuid4()
    ts = int(time.time() * 1e6)
    payment = Payment.create({
        "amount": {
            "value": course.prices[price_type],
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": config.bot.link
        },
        "capture": True,
        "description": f"Заказ № {ts}",
        'metadata': {
            'tg_user_id': str(user_id),
            'payment_type': str(price_type),
            'ts': str(ts)
        }
    }, u_id)

    return payment

