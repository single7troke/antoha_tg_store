import base64
import logging
import pickle
from typing import Tuple, Optional, Any

import aiohttp
from cryptography.fernet import Fernet

from models.models import User
from .config import get_config

config = get_config()


def decrypt(text: str) -> str:
    key = base64.urlsafe_b64encode(config.secret_key.encode('utf-8'))
    cipher_suite = Fernet(key)
    decrypted_link_key = cipher_suite.decrypt(text).decode('utf-8')
    return decrypted_link_key


def get_data_from_link_key(link_key: str) -> Optional[Tuple[Any, Any, Any]]:
    if 'link' not in link_key:
        return False
    user_id, course_id, part_id = link_key.replace('link:::', '').split(':::')
    return user_id, course_id, part_id


def bytes_to_user(data: bytes) -> User:
    user = pickle.loads(data)
    return user


async def send_message(chat_id: str, text: str) -> str | None:
    url = f"https://api.telegram.org/bot{config.tg_token}/sendMessage"

    params = {
        "chat_id": chat_id,
        "text": text
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            response_data = await response.json()
            if response.status == 200:
                message_id = response_data['result']['message_id']
                logging.info(f"Message sent successfully to: {chat_id}, response_data: {response_data}")
                return message_id
            else:
                logging.info(f"Failed to send message: {response_data}")


async def delete_message(chat_id: str, message_id: str) -> str:
    url = f"https://api.telegram.org/bot{config.tg_token}/deleteMessage"

    params = {
        "chat_id": chat_id,
        "message_id": message_id
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params) as response:
            if response.status == 200:
                logging.info(f"Message with ID {message_id} deleted successfully.")
            else:
                logging.info(f"Failed to delete message: {await response.text()}")


async def send_sell_notification_to_admins(course_type, user_id):
    text = f'{user_id} оплатил расширенный курс' if course_type == 'extended' else f'{user_id} оплатил базовый курс'
    for admin_id in config.tg_admin_list:
        await send_message(admin_id, text)
