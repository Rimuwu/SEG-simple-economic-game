from game.user import User
from modules import websocket_manager
from modules import check_password
from modules.ws_hadnler import message_handler
from modules.json_database import just_db
from game.company import Company

@message_handler(
    "get-companies", 
    doc="Обработчик получения списка компаний. Отправляет ответ на request_id", 
    datatypes=[
        "session_id: Optional[int]", 
        "in_prison: Optional[bool]",
        "cell_position: Optional[str]",
        "request_id: str"
        ])
async def handle_get_companies(client_id: str, message: dict):
    """Обработчик получения списка компаний"""

    conditions = {
        "in_prison": message.get("in_prison"),
        "cell_position": message.get("cell_position"),
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
        "cell_position: Optional[str]",
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
        "cell_position": message.get("cell_position")
    }

    # Получаем компанию из базы данных
    company = just_db.find_one('companies',
                         **{k: v for k, v in conditions.items() if v is not None})

    return company

@message_handler(
    "create-company", 
    doc="Обработчик создания компании. Отправляет ответ на request_id. Требуется пароль для взаимодействия.",
    datatypes=[
        "name: str",
        "who_create: int",

        "password: str",
        "request_id: str"
    ],
    messages=["api-create_company (broadcast)"]
)
async def handle_create_company(client_id: str, message: dict):
    """Обработчик создания компании"""

    password = message.get("password")
    name = message.get("name")
    who_create = message.get("who_create")

    for i in [name, password, who_create]:
        if i is None: return {"error": "Missing required fields."}

    try:
        check_password(password)
        
        user = User(_id=who_create).reupdate()
        if not user: raise ValueError("User not found.")
        company = user.create_company(name=name)

    except ValueError as e:
        return {"error": str(e)}

    data = {
        'session_id': company.session_id,
        'company': company.__dict__
    }

    await websocket_manager.broadcast({
        "type": "api-create_company",
        "data": data
    })
    return data


@message_handler(
    "update-company-add-user", 
    doc="Обработчик обновления компании. Требуется пароль для взаимодействия.",
    datatypes=[
        "user_id: int",
        "company_id: str",

        "password: str"
    ],
    messages=["api-update-company-add-user (broadcast)"]
)
async def handle_update_company_add_user(client_id: str, message: dict):
    """Обработчик обновления компании"""

    password = message.get("password")
    user_id = message.get("user_id")
    company_id = message.get("company_id")

    for i in [user_id, company_id, password]:
        if i is None: return {"error": "Missing required fields."}

    try:
        check_password(password)

        user = User(_id=user_id).reupdate()
        if not user: raise ValueError("User not found.")
        company = user.add_to_company(company_id=company_id)

    except ValueError as e:
        return {"error": str(e)}

    data = {
        'company_id': company.id,
        'user_id': user.id
    }

    await websocket_manager.broadcast({
        "type": "api-update-company-add-user",
        "data": data
    })

@message_handler(
    "set-company-position", 
    doc="Обработчик обновления компании. Требуется пароль для взаимодействия. Отправляет ответ на request_id (получилось или нет)",
    datatypes=[
        "company_id: int",
        "x: int",
        "y: int",

        "password: str",
        "request_id: str"
    ],
    messages=["api-set-company-position (broadcast)"]
)
async def handle_set_company_position(client_id: str, message: dict):
    """Обработчик обновления компании"""

    password = message.get("password")
    company_id = message.get("company_id")
    x = message.get("x")
    y = message.get("y")

    result = False
    old_position = None

    for i in [company_id, password, x, y]:
        if i is None: return {"error": "Missing required fields."}

    try:
        check_password(password)

        company = Company(_id=company_id).reupdate()
        if not company: raise ValueError("Company not found.")

        old_position = company.cell_position
        result = company.set_position(x=x, y=y)

    except ValueError as e:
        return {"error": str(e)}

    data = {
        'company_id': company.id,
        'old_position': old_position,
        'new_position': company.cell_position
    }

    await websocket_manager.broadcast({
        "type": "api-update-company-add-user",
        "data": data
    })

    return {
        "result": result, 
        "position_now": company.cell_position
            }