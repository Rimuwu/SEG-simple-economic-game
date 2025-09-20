from modules.ws_hadnler import message_handler
from modules.json_database import just_db

@message_handler(
    "get-users", 
    doc="Обработчик получения списка пользователей. Отправляет ответ на request_id.", 
    datatypes=[
        "company_id: Optional[int]", 
        "session_id: Optional[int]", 
        "request_id: str"
        ])
async def handle_get_users(client_id: str, message: dict):
    """Обработчик получения списка пользователей"""

    conditions = {
        "company_id": message.get("company_id"),
        "session_id": message.get("session_id")
    }

    # Получаем список пользователей из базы данных
    users = just_db.find('users',
                         **{k: v for k, v in conditions.items() if v is not None})

    return users

@message_handler(
    "get-user", 
    doc="Обработчик получения пользователя. Отправляет ответ на request_id.", 
    datatypes=[
        "id: Optional[int]", 
        "username: Optional[str]", 
        "company_id: Optional[int]", 
        "session_id: Optional[str]",
        "request_id: str"
        ])
async def handle_get_user(client_id: str, message: dict):
    """Обработчик получения списка пользователей"""

    conditions = {
        "id": message.get("id"),
        "username": message.get("username"),
        "company_id": message.get("company_id"),
        "session_id": message.get("session_id")
    }

    # Получаем пользователя из базы данных
    user = just_db.find_one('users',
                         **{k: v for k, v in conditions.items() if v is not None})

    return user