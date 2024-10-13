import logging
import time
import uuid
from typing import Union, Optional, Dict, Any

import requests.exceptions
from yookassa import Payment, Configuration
from yookassa.domain.response import PaymentResponse

from core import get_config
from models import Course

config = get_config()

Configuration.account_id = config.payment.yookassa_account_id
Configuration.secret_key = config.payment.yookassa_secret_key


def create_payment(
        user: Dict[Any, Any],
        course: Course,
        price_type: str,
        email: str,
        payment_number: int
) -> Optional[PaymentResponse]:
    u_id = uuid.uuid4()
    ts = int(time.time())
    try:
        payment = Payment.create({
            "amount": {
                "value": course.prices[price_type],
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": config.bot.link
            },
            "receipt": {
                "customer": {
                    "email": email
                },
                "items": [{
                    "description": "some course description",  # TODO нужно название курса для чека
                    "amount": {
                        "value": course.prices[price_type],
                        "currency": 'RUB'
                    },
                    "vat_code": 1,
                    "quantity": 1
                }]
            },
            "capture": True,
            "description": f"Заказ № {payment_number:05}",
            'metadata': {
                'tg_id': str(user['id']),
                'tg_first_name': str(user['first_name']),
                'tg_last_name': str(user['last_name']),
                'tg_username': str(user['username']),
                'price_type': str(price_type),
                'ts': str(ts),
                'course_id': str(course.id),
                'email': email
            }
        }, u_id)

        return payment
    except Exception as e:
        logging.error(e)
        return None


def get_payment(payment_id: str) -> Optional[PaymentResponse]:
    try:
        payment = Payment.find_one(payment_id)
        return payment
    except requests.exceptions.HTTPError as e:
        logging.error(e)
        return None
