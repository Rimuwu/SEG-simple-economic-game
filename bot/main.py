import asyncio
import os
import time
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# from dotenv import load_dotenv # При запуске не из Docker
# load_dotenv() # Загружаем переменные окружения из .env файла

# # Добавляем корневую папку проекта в sys.path для корректного импорта модулей
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # При запуске не из Docker
from global_modules.api_client import create_client
from global_modules.logs import Logger

# Настройка логирования
bot_logger = Logger.get_logger("bot")

# Инициализация бота и диспетчера
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# Создаем WebSocket клиента
ws_client = create_client(
            client_id=f"bot_client_{int(time.time())}", 
            uri=os.getenv("WS_SERVER_URI", "ws://localhost:8000/ws/connect"),
            logger=bot_logger)

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
        await ws_client.connect()
        if ws_client.is_connected():
            print("✅ Повторное подключение успешно!")
            return

        print(f"❌ Не удалось подключиться, повтор через 1 секунду...")
        await asyncio.sleep(1)

    print("❌ Не удалось подключиться после 15 попыток, выход.")

async def main():
    """Главная функция для запуска бота"""
    bot_logger.info("Запуск бота...")

    try:
        await ws_client.connect() # Подключаемся к WebSocket серверу
        await dp.start_polling(bot)
    finally:
        await ws_client.disconnect() # Отключаемся от сервера
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())