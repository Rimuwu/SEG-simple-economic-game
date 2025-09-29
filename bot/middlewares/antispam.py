import time
from typing import Awaitable, Callable, Any

from aiogram.types import CallbackQuery
from aiogram import BaseMiddleware
from bot_instance import dp

DEFAULT_RATE_LIMIT = 0.5

class CallbackQueryAntiFloodMiddleware(BaseMiddleware):
    def __init__(self, timeout: float=DEFAULT_RATE_LIMIT):
        super().__init__()
        self.timeout = timeout
        self.last_query = {}

    async def __call__(self, 
                handler: Callable[[CallbackQuery, dict[str, Any]], Awaitable[Any]],
                message: CallbackQuery,
                data: dict[str, Any]):

        now = time.time()
        if message.from_user.id not in self.last_query:
            self.last_query[message.from_user.id] = now
            # await message.answer()  # always answer callback query
            return await handler(message, data)

        if now - self.last_query[message.from_user.id] < self.timeout:
            self.last_query[message.from_user.id] = now

            await message.answer('Куда так быстро, отдохни буквально 1 секунду', True)
            return

        self.last_query[message.from_user.id] = now
        # await message.answer()  # always answer callback query
        return await handler(message, data)

dp.callback_query.middleware(CallbackQueryAntiFloodMiddleware())