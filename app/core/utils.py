import base64
from typing import Tuple, Optional, Any

from cryptography.fernet import Fernet

from .config import get_config

config = get_config()


def decrypt(text: str) -> str:
    key = base64.urlsafe_b64encode(config.secret_key.encode('utf-8'))
    cipher_suite = Fernet(key)
    decrypted_link_key = cipher_suite.decrypt(text).decode('utf-8')
    return decrypted_link_key


def get_data_from_link_key(link_key: str) -> Optional[Tuple[Any]]:
    if 'link' not in link_key:
        return False
    user_id, course_id, part_id = link_key.replace('link:::', '').split(':::')
    return user_id, course_id, part_id
