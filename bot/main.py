import argparse
import asyncio
import json
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import BotCommand, FSInputFile
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from api import user_router, main_menu
from core.config import Config
# from middleware.user_access import UserAccessMiddleware, AdminAccessMiddleware

config = Config()
parser = argparse.ArgumentParser()
parser.add_argument('--webhook', action=argparse.BooleanOptionalAction)
args = parser.parse_args()


async def welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    """
    await message.answer(f"Привет <b>{message.from_user.first_name}</b>!\n\n")
    await main_menu(message)


async def description(message: types.Message):
    """
    This handler will be called when user sends `/about` command
    """
    await message.answer("<b>Как этим пользоваться.</b>\n\n"
                         "Нажми на меню и выбери команду.\n\n"
                         "<b>Ближаешее мероприятие</b> - выведет описание ближайшего мероприятия.\n\n"
                         "<b>Список мероприятий</b> - выведет список всех мероприятий\n"
                         "в виде клавиатуры с датами мероприятий.\n"
                         "Нажами на интересующую дату чтобы узнать детали мероприятия.\n\n"
                         "Бот присылает сообщение если в календаре появилось/удалилось мероприятие\n"
                         )


async def admin_description(message: types.Message):
    """
    This handler will be called when user sends `/admin` command
    """
    await message.answer("<b>Описание функционала администратора.</b>\n\n"
                         "Команды:\n\n"
                         "<b>/new_user</b> Добавляет нового пользователя в список тех,\n"
                         "кому разрешено пользоваться ботом.\n"
                         "1. Вводим id ползователя, который он должен предоставить(9ти значное число)\n"
                         "2. Вводим имя пользователя(на свое усмотрение, не длиннее 20 символов).\n\n"
                         "<b>/user_list</b> выведет список всех пользователей\n"
                         "в виде клавиатуры с именами пользователей.\n"
                         "Нажми на пользователя и подтверди его удаление.\n\n"
                         )


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="menu", description="Меню"),
    ]

    await bot.set_my_commands(commands=commands)


async def polling_setup(bot: Bot, dp: Dispatcher):
    try:
        await bot.delete_webhook()
        await set_commands(bot)
        await dp.start_polling(bot)
    except Exception as e:
        raise e


async def webhook_setup(bot: Bot):
    await bot.delete_webhook()
    await set_commands(bot)
    cert = FSInputFile(config.path_to_pem_file)
    await bot.set_webhook(url=config.server_url,
                          ip_address=config.server_ip,
                          certificate=cert)
    info = await bot.get_webhook_info()
    info = json.loads(info.json())
    logging.info(f'webhook info:\n{json.dumps(info, indent=4)}')


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s %(message)s",
                        datefmt="%Y/%m/%d %H:%M:%S",
                        level=config.log_lvl)

    default = DefaultBotProperties(parse_mode='HTML')
    bot = Bot(token=config.tg_bot_token, default=default)
    dp = Dispatcher()
    dp.message.register(welcome, Command(commands=["start"]))
    # dp.message.register(description, Command(commands=["about"]))
    # dp.message.register(admin_description, Command(commands=["admin"]))
    # dp.include_router(google_calendar.router)
    dp.include_router(user_router)
    # dp.message.middleware(AdminAccessMiddleware())
    # dp.message.outer_middleware(UserAccessMiddleware())

    webhook = args.webhook
    if webhook:
        logging.info("Run webhook")
        dp.startup.register(webhook_setup)
        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/calendar_bot")
        setup_application(app, dp, bot=bot)
        web.run_app(app)
    else:
        logging.info("Run polling")
        asyncio.run(polling_setup(bot=bot, dp=dp))
