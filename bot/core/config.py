import logging
import os
from datetime import datetime
from typing import Dict

from pydantic_settings import BaseSettings, SettingsConfigDict


class Buttons(BaseSettings):
    back: str = '<- Назад'
    catalog: str = 'Каталог курсов'
    about: str = 'Обо мне'
    buy: str = 'Купить за {price}'
    prices: str = 'Расценки'
    link_to_pay: str = 'Перейти к оплате'
    course_type: Dict[str, str] = {'standard': 'Базовый курс', 'with_support': 'Курс с проверкой домашних заданий'}


class BotConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='tg_')

    token: str
    pay_token: str
    name: str = 'bestbassbot'
    link: str = f'https://t.me/{name}'


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='app_')


class Cache(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='redis_')
    host: str
    port: int


class DB(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='db_')


class Payment(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='pay_')
    yookassa_account_id: int
    yookassa_secret_key: str


class Config(BaseSettings):
    log_lvl: int = logging.INFO
    admin_commands: list = ["admin", "user_list", "new_user"]
    admin_roles: list = ["admin", "superuser"]
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    web_app_url: str = "http://app:8000/api/v1/"
    # path_to_pem_file: str = "/etc/ssl/certs/YOURPUBLIC.pem"
    server_ip: str = ""
    server_url: str = 'http://127.0.0.1'
    path_to_files: str = '/var/www/app/files'
    secret_key: str
    sales_start_dt: datetime
    stop_selling_course_with_support_dt: datetime
    buttons: Buttons = Buttons()
    bot: BotConfig = BotConfig()
    app: AppConfig = AppConfig()
    db: DB = DB()
    cache: Cache = Cache()
    payment: Payment = Payment()


config: Config | None = None


def get_config() -> Config:
    global config
    if not config:
        config = Config()
    return config
