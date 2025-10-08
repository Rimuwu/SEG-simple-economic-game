import asyncio
import logging

from global_modules.logs import Logger

from modules.db import db
from modules.ws_client import ws_client
from bot_instance import bot, dp
from modules.load_scenes import load_scenes_from_db

from oms import register_handlers, scene_manager
import handlers

# Настройка логирования
bot_logger = Logger.get_logger("bot")
logging.basicConfig(level=logging.INFO)


async def main():
    """Главная функция для запуска бота"""
    bot_logger.info("Запуск бота...")

    try:
        # db.drop_all()
        db.create_table('messages')
        db.create_table('scenes')

        register_handlers(dp)

        await ws_client.connect() # Подключаемся к WebSocket серверу
        await dp.start_polling(bot)
    finally:
        await ws_client.disconnect() # Отключаемся от сервера
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())