import base64
import json
import pickle
from typing import List, Dict

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from cryptography.fernet import Fernet
from email_validator import validate_email, EmailNotValidError

from models.models import Course, CourseOption, User
from .config import get_config
from .payments import get_payment

config = get_config()


def get_download_link(link_key: str) -> str:
    encrypted_link_key = encrypt(link_key)
    link = f'{config.server_url}/api/v1/files/{encrypted_link_key}'
    return link


def encrypt(key_to_link: str) -> str:
    key = base64.urlsafe_b64encode(config.secret_key.encode('utf-8'))
    cipher_suite = Fernet(key)
    encrypted_link_key = cipher_suite.encrypt(key_to_link.encode('utf-8')).decode('utf-8')
    return encrypted_link_key


def remaining_time(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    hms = f"{hours:02}:{minutes:02}:{secs:02}"
    return hms


def get_course_id_and_course_part_id(s: str) -> List[int]:
    return [int(i) for i in s.split('---')]


def bytes_to_user(data: bytes) -> User:
    user = pickle.loads(data)
    return user


async def clear_messages(bot: Bot, chat_id: int, message_id: int) -> None:
    while True:
        try:
            await bot.delete_message(chat_id, message_id)
            message_id -= 1
        except TelegramBadRequest:
            return


def is_valid_email(email: str) -> bool:
    try:
        valid = validate_email(email)
        return True
    except EmailNotValidError as e:
        return False


def course_already_payed(user: User):
    for course_type, payment_id in user.courses[COURSE.id].payment_ids.items():
        if get_payment(payment_id).status == 'succeeded':
            return course_type


def load_course_from_descriptor() -> Course:
    with open(f'{config.path_to_files}/course_descriptor.json', 'r') as file:
        data = json.load(file)
        course = Course(
            id=data['id'],
            name=data['name'],
            prices=data['prices'],
            description=data['description'],
            parts=data['parts'],
            options=[CourseOption(
                name=option['name'],
                price=option['price'],
                payed=option['payed'],
                description=option['description']
            ) for option in data['options']]
        )
        return course


COURSE = load_course_from_descriptor() # TODO переделать
