from modules.ws_hadnler import message_handler
from modules.json_database import just_db

@message_handler(
    "get-sessions", 
    doc="Обработчик получения списка сессий. Отправляет ответ на request_id", 
    datatypes=[
        "stage: Optional[str]", 
        "request_id: str"
        ])
async def handle_get_sessions(client_id: str, message: dict):
    """Обработчик получения списка сессий"""

    conditions = {
        "stage": message.get("stage"),
    }

    # Получаем список сессий из базы данных
    sessions = just_db.find('sessions',
                         **{k: v for k, v in conditions.items() if v is not None})

    return sessions

@message_handler(
    "get-session", 
    doc="Обработчик получения сессии. Отправляет ответ на request_id.", 
    datatypes=[
        "session_id: Optional[str]", 
        "stage: Optional[str]",
        "request_id: str"
        ])
async def handle_get_session(client_id: str, message: dict):
    """Обработчик получения сессии"""

    conditions = {
        "session_id": message.get("session_id"),
        "stage": message.get("stage")
    }

    # Получаем сессию из базы данных
    session = just_db.find_one('sessions',
                         **{k: v for k, v in conditions.items() if v is not None})

    return session