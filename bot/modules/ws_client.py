import os
import time
from global_modules.api_client import create_client
from global_modules.logs import Logger

# Настройка логирования
bot_logger = Logger.get_logger("bot")

# Создаем WebSocket клиента
ws_client = create_client(
    client_id=f"bot_client_{int(time.time())}", 
    uri=os.getenv("WS_SERVER_URI", "ws://localhost:8000/ws/connect"),
    logger=bot_logger
)