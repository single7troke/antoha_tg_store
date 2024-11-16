import logging
import os

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


config: Config | None = None


def get_config() -> Config:
    global config
    if not config:
        config = Config()
    return config
