import argparse
import asyncio
import json
import logging

import aioredis
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import BotCommand, FSInputFile
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

import api
from db import redis
from core import get_config
from middleware.admin_access import AdminAccessMiddleware

config = get_config()
parser = argparse.ArgumentParser()
parser.add_argument('--webhook', action=argparse.BooleanOptionalAction)
args = parser.parse_args()


async def welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    """
    await api.main_menu(message)


async def description(message: types.Message):
    """
    This handler will be called when user sends `/about` command
    """
    await message.answer('asdf')


async def admin_description(message: types.Message):
    """
    This handler will be called when user sends `/admin` command
    """
    await message.answer('asf')


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="menu", description="Меню"),
    ]

    await bot.set_my_commands(commands=commands)


async def create_redis_client():
    logging.warning('Creating redis connection')
    try:
        client = await aioredis.from_url(
            url=f"redis://{config.cache.host}:{config.cache.port}",
            encoding="utf-8",
            # decode_responses=True
        )
        return client
    except Exception as e:
        raise e


async def polling_setup(bot: Bot, dp: Dispatcher):
    try:
        logger.info('Starting in polling mode')
        await bot.delete_webhook()
        await set_commands(bot)
        await dp.start_polling(bot)
    except Exception as e:
        raise e


async def webhook_setup(bot: Bot):
    try:
        logger.info("Starting in webhook mode")
        await bot.delete_webhook()
        await set_commands(bot)
        cert = FSInputFile(config.path_to_pem_file)
        await bot.set_webhook(url=f'https://{config.server_ip}{config.bot.webhook_path}',
                              ip_address=config.server_ip,
                              certificate=cert)
        info = await bot.get_webhook_info()
        info = json.loads(info.json())
        logger.info(f'Webhook info:\n{json.dumps(info, indent=4)}')
    except Exception as e:
        raise e

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(name)s:%(funcName)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logger = logging.getLogger(__name__)

    default = DefaultBotProperties(parse_mode='HTML')
    bot = Bot(token=config.bot.token, default=default)
    dp = Dispatcher()
    dp.message.register(welcome, Command(commands=["start"]))
    dp.include_router(api.user_router)
    dp.include_router(api.admin_router)
    dp.message.middleware(AdminAccessMiddleware())
    # dp.message.outer_middleware(UserAccessMiddleware())

    @dp.startup()
    async def on_startup(*args, **kwargs):
        redis.redis = await create_redis_client()
        receipt_number = await redis.redis.exists('receipt_number')
        if not receipt_number:
            await redis.redis.set('receipt_number', 0)

        payment_number_exists = await redis.redis.exists('extended_course_sold_quantity')
        if not payment_number_exists:
            await redis.redis.set('extended_course_sold_quantity', 0)

    webhook = args.webhook
    if webhook:
        dp.startup.register(webhook_setup)
        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=config.bot.webhook_path)
        setup_application(app, dp, bot=bot)
        web.run_app(app, host='0.0.0.0', port=8081)
    else:
        asyncio.run(polling_setup(bot=bot, dp=dp))
