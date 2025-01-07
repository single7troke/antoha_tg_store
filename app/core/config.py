import logging
import os
from typing import Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    name: str = 'web_app_name'
    path_to_files: str = '/var/www/course/files'
    log_lvl: int = logging.INFO
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # path_to_pem_file: str = "/etc/ssl/certs/RPUBLIC.pem"
    server_ip: str = ""
    secret_key: str
    dev_mode: bool = False
    db: DB = DB()
    cache: Cache = Cache()
    payment: Payment = Payment()
    tg_token: str
    tg_admin_list: Union[str, list]

    @field_validator('tg_admin_list')
    def make_list_from_string(cls, v: str):
        return [i for i in v.split(',')]


config: Config | None = None


def get_config() -> Config:
    global config
    if not config:
        config = Config()
    return config
