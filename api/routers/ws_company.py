from modules.ws_hadnler import message_handler
from modules.json_database import just_db

@message_handler(
    "get-companies", 
    doc="Обработчик получения списка компаний. Отправляет ответ на request_id", 
    datatypes=[
        "session_id: Optional[int]", 
        "in_prison: Optional[bool]",
        "cell_positions: Optional[str]",
        "request_id: str"
        ])
async def handle_get_companies(client_id: str, message: dict):
    """Обработчик получения списка компаний"""

    conditions = {
        "in_prison": message.get("in_prison"),
        "cell_positions": message.get("cell_positions"),
        "session_id": message.get("session_id")
    }

    # Получаем список компаний из базы данных
    companies = just_db.find('companies',
                         **{k: v for k, v in conditions.items() if v is not None})

    return companies

@message_handler(
    "get-company", 
    doc="Обработчик получения компании. Отправляет ответ на request_id.", 
    datatypes=[
        "id: Optional[int]", 
        "name: Optional[str]", 
        "reputation: Optional[int]", 
        "balance: Optional[int]",
        "in_prison: Optional[bool]",
        "session_id: Optional[str]",
        "cell_positions: Optional[str]",
        "request_id: str"
        ])
async def handle_get_company(client_id: str, message: dict):
    """Обработчик получения компании"""

    conditions = {
        "id": message.get("id"),
        "name": message.get("name"),
        "reputation": message.get("reputation"),
        "balance": message.get("balance"),
        "in_prison": message.get("in_prison"),
        "session_id": message.get("session_id"),
        "cell_positions": message.get("cell_positions")
    }

    # Получаем компанию из базы данных
    company = just_db.find_one('companies',
                         **{k: v for k, v in conditions.items() if v is not None})

    return company