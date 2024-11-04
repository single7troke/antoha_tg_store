from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from core.config import Config

config = Config()


class AdminAccessMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if data.get('command') and data.get('command').command in config.bot.admin_commands:
            if int(event.from_user.id) in config.bot.admin_list:
                return await handler(event, data)

            return False

        return await handler(event, data)
