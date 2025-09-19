

from modules.websocket_manager import websocket_manager
from modules.ws_hadnler import message_handler
from global_modules.logs import main_logger
from game.session import Session

@message_handler(
    "ping", 
    doc="Обработчик ping сообщений", 
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

# @message_handler("create_user")
# async def handle_create_session(client_id: str, message: dict):

# @message_handler(
#     "create_session",
#     doc="Создать новую сессию. Возвращает session_id"
# )
# async def handle_create_session(client_id: str, message: dict):
#     """Обработчик создания сессии"""

#     session = Session().start()
#     return session.session_id
