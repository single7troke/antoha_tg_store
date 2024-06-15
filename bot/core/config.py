import logging
import os

from pydantic_settings import BaseSettings


class Buttons(BaseSettings):
    back: str = '<- Назад'
    catalog: str = 'Каталог курсов'
    about: str = 'Обо мне'


class BotConfig(BaseSettings):
    pass


class AppConfig(BaseSettings):
    pass


class Cache(BaseSettings):
    pass


class DB(BaseSettings):
    pass


class Config(BaseSettings):
    log_lvl: int = logging.INFO
    admin_commands: list = ["admin", "user_list", "new_user"]
    admin_roles: list = ["admin", "superuser"]
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    web_app_url: str = "http://app:8000/api/v1/"
    # path_to_pem_file: str = "/etc/ssl/certs/YOURPUBLIC.pem"
    server_ip: str = ""
    server_url: str = ""
    tg_bot_token: str
    buttons: Buttons = Buttons()
    bot: BotConfig = BotConfig()
    app: AppConfig = AppConfig()
    db: DB = DB()
    cache: Cache = Cache()
