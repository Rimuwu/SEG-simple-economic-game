

from modules.websocket_manager import websocket_manager
from modules.ws_hadnler import message_handler
from global_modules.logs import main_logger
from game.session import Session
from modules.json_database import just_db

@message_handler(
    "ping", 
    doc="Обработчик ping сообщений. Отправляет pong в ответ.", 
    datatypes=["timestamp: str", "content: Any"])
async def handle_ping(client_id: str, message: dict):
    """Обработчик ping сообщений"""
    pong_message = {
        "type": "pong",
        "timestamp": message.get("timestamp", ""),
        "client_id": client_id,
        "content": message.get("content", "Pong!")
    }

    await websocket_manager.send_message(client_id, pong_message)
    main_logger.debug(f"Отправлен pong клиенту {client_id}")