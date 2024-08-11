import base64
import json
from typing import List, Dict

from cryptography.fernet import Fernet

from models.models import Course
from .config import get_config

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


def load_courses_from_descriptor() -> Dict[int, Course]:
    data = {}
    with open(f'{config.path_to_files}/course_descriptor.json', 'r') as file:
        for k, v in json.load(file).items():
            data[int(k)] = Course(id=v['id'], name=v['name'], price=v['price'], description=v['description'],
                                  parts={int(i): j for i, j in v['parts'].items() if v['parts']})
        return data


COURSES = load_courses_from_descriptor()
