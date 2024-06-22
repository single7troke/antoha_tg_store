import logging
import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='app_')
    name: str = 'web_app_name'


class Cache(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='redis_')
    host: str
    port: int


class DB(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='db_')


class Config(BaseSettings):
    log_lvl: int = logging.INFO
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # path_to_pem_file: str = "/etc/ssl/certs/YOURPUBLIC.pem"
    server_ip: str = ""
    server_url: str = ""
    app: AppConfig = AppConfig()
    db: DB = DB()
    cache: Cache = Cache()
