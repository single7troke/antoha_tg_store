import uuid
from typing import Union

import requests
from yookassa import Payment, Configuration
from yookassa.domain.response import PaymentResponse

from core import get_config
from core import utils
from models import Course

config = get_config()

Configuration.account_id = config.payment.yookassa_account_id
Configuration.secret_key = config.payment.yookassa_secret_key


def create_payment(user_id: Union[str, int], course: Course) -> PaymentResponse:
    u_id = uuid.uuid4()
    payment = Payment.create({
        "amount": {
            "value": course.price,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": config.bot.link
        },
        "capture": True,
        "description": f"Заказ № {u_id}",
        'metadata': {
            'tg_user_id': str(user_id),
            'course_id': str(course.id)
        }
    }, u_id)

    return payment

