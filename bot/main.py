import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

# from dotenv import load_dotenv # При запуске не из Docker
# load_dotenv() # Загружаем переменные окружения из .env файла

# # Добавляем корневую папку проекта в sys.path для корректного импорта модулей
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # При запуске не из Docker
from global_modules.logs import Logger

from modules.db import db
from modules.message import Message
from modules.ws_client import ws_client
from app.handlers import router

# Настройка логирования
bot_logger = Logger.get_logger("bot")

# Инициализация бота и диспетчера с хранилищем для FSM
storage = MemoryStorage()
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(storage=storage)

@dp.message(Command("sessions"))
async def sessions_command(message: types.Message):
    """Обработчик команды /sessions"""
    try:
        # Отправляем запрос на получение списка сессий
        response = await ws_client.send_message(
            "get-sessions",
            stage='FreeUserConnect',
            wait_for_response=True,
            )
        for session in response:
            await message.answer(
                f"ID: {session['session_id']}, Stage: {session['stage']}, Created At: {session['created_at']}"
                )
        else:
            if not response:
                await message.answer("Нет активных сессий.")
    except Exception as e:
        await message.answer(f"Ошибка при выполнении команды /sessions: {str(e)}")

# http://localhost:8000/ws/status - тут можно посмотреть статус вебсокета и доступные типы для отправки сообщений через send_message
@dp.message(Command("ping"))
async def ping_command(message: types.Message):
    """Обработчик команды /ping"""
    try:
        # Отправляем ping через клиент
        response = await ws_client.send_message(
            "ping", {'from': message.from_user.id})
        print(f"Ответ от сервера: {response}")
    except Exception as e:
        await message.answer(f"Ошибка при выполнении ping: {str(e)}")

@dp.message(Command("save_my_message"))
async def save_my_message_command(message: types.Message):
    """Обработчик команды /save_my_message"""

    msg = Message(_id=message.message_id)
    msg.user_id = message.from_user.id
    msg.save_to_base()

    # or

    msg = Message().create(
        _id=message.message_id, user_id=message.from_user.id
        )

    # Тут не будет создано 2 записи, т.к. id сообщения будет уникальным в базе 

@ws_client.on_message('pong')
async def on_pong(message: dict):
    """Обработчик ответа pong от сервера"""
    print(f"Получен pong от сервера: {message}")

    from_id = message.get('content', {}).get('from')

    await bot.send_message(from_id, "Pong! 🏓")

@ws_client.on_event("connect")
async def on_connect():
    print("🔗 Подключено к WebSocket серверу")

@ws_client.on_event("disconnect")
async def on_disconnect():
    print("❌ Отключено от WebSocket сервера")

    for _ in range(15, 0, -1):
        print(f"🔄 Попытка подключения...")
        await ws_client.connect(max_attempts=10)
        if ws_client.is_connected():
            print("✅ Повторное подключение успешно!")
            return

        print(f"❌ Не удалось подключиться, повтор через 1 секунду...")
        await asyncio.sleep(1)

    print("❌ Не удалось подключиться после 15 попыток, выход.")

async def main():
    """Главная функция для запуска бота"""
    bot_logger.info("Запуск бота...")
    dp.include_router(router)

    try:

        db.create_table('messages') # После запуска посмотреть файл data/bot_database.json

        await ws_client.connect() # Подключаемся к WebSocket серверу
        await dp.start_polling(bot)
    finally:
        await ws_client.disconnect() # Отключаемся от сервера
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())