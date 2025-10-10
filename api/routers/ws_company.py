from game.user import User
from modules.websocket_manager import websocket_manager
from modules.check_password import check_password
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
    companies = just_db.find('companies', to_class=Company,
                         **{k: v for k, v in conditions.items() if v is not None})

    return [company.to_dict() for company in companies]

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
    company = just_db.find_one('companies', to_class=Company,
                         **{k: v for k, v in conditions.items() if v is not None})

    return company.to_dict()

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
        company.set_owner(user.id)

    except ValueError as e:
        return {"error": str(e)}

    return {
        'session_id': company.session_id,
        'company': company.to_dict()
    }


@message_handler(
    "update-company-add-user", 
    doc="Обработчик добавления пользователя в компанию. Требуется пароль для взаимодействия.",
    datatypes=[
        "user_id: int",
        "secret_code: int",

        "password: str"
    ],
    messages=["api-user_added_to_company (broadcast)"]
)
async def handle_update_company_add_user(client_id: str, message: dict):
    """Обработчик обновления компании"""

    password = message.get("password")
    user_id = message.get("user_id")
    secret_code = message.get("secret_code")

    for i in [user_id, secret_code, password]:
        if i is None: return {"error": "Missing required fields."}

    try:
        check_password(password)

        user = User(_id=user_id).reupdate()
        if not user: raise ValueError("User not found.")

        user.add_to_company(secret_code=secret_code)

    except ValueError as e:
        return {"error": str(e)}

@message_handler(
    "set-company-position", 
    doc="Обработчик обновления местоположения компании. Требуется пароль для взаимодействия. Отправляет ответ на request_id (получилось или нет)",
    datatypes=[
        "company_id: int",
        "x: int",
        "y: int",

        "password: str",
        "request_id: str"
    ],
    messages=["api-company_set_position (broadcast)"]
)
async def handle_set_company_position(client_id: str, message: dict):
    """Обработчик обновления компании"""

    password = message.get("password")
    company_id = message.get("company_id")
    x = message.get("x")
    y = message.get("y")

    result = False

    for i in [company_id, password, x, y]:
        if i is None: return {"error": "Missing required fields."}

    try:
        check_password(password)

        company = Company(_id=company_id).reupdate()
        if not company: raise ValueError("Company not found.")

        result = company.set_position(x=x, y=y)

    except ValueError as e:
        return {"error": str(e)}

    return {
        "result": result, 
        "position_now": company.cell_position
            }

@message_handler(
    "update-company-left-user", 
    doc="Обработчик выхода пользователя из компании. Требуется пароль для взаимодействия.",
    datatypes=[
        "user_id: int",
        "company_id: int",

        "password: str"
    ],
    messages=["api-user_left_company (broadcast)"]
)
async def handle_update_company_left_user(client_id: str, message: dict):
    """Обработчик выхода пользователя из компании"""

    password = message.get("password")
    user_id = message.get("user_id")
    company_id = message.get("company_id")

    for i in [user_id, company_id, password]:
        if i is None: return {"error": "Missing required fields."}

    try:
        check_password(password)

        user = User(_id=user_id).reupdate()
        if not user: raise ValueError("User not found.")
        user.leave_from_company()

    except ValueError as e:
        return {"error": str(e)}

@message_handler(
    "delete-company", 
    doc="Обработчик удаления компании. Требуется пароль для взаимодействия.",
    datatypes=[
        "company_id: int",

        "password: str"
    ],
    messages=["api-company_deleted (broadcast)"]
)
async def handle_delete_company(client_id: str, message: dict):
    """Обработчик удаления компании."""

    password = message.get("password")
    company_id = message.get("company_id")

    for i in [company_id, password]:
        if i is None: return {"error": "Missing required fields."}

    try:
        check_password(password)

        company = Company(_id=company_id).reupdate()
        if not company: raise ValueError("Company not found.")

        company.delete()

    except ValueError as e:
        return {"error": str(e)}

@message_handler(
    "get-company-cell-info", 
    doc="Обработчик получения информации о ячейке компании. Отправляет ответ на request_id", 
    datatypes=[
        "company_id: int", 
        "request_id: str"
        ])
async def handle_get_my_cell_info(client_id: str, message: dict):
    """Обработчик получения информации о моей ячейке"""

    conditions = {
        "company_id": message.get("company_id")
    }
    
    for i in conditions.values():
        if i is None: return {"error": "Missing required fields."}

    company = Company(_id=conditions["company_id"]).reupdate()
    if not company: return {"error": "Company not found."}

    cell_info = company.get_my_cell_info()
    if cell_info is not None:
        return {
            "data": cell_info.__dict__,
            "type": company.get_cell_type()
        }
    else:
        return None

@message_handler(
    "get-company-improvement-info", 
    doc="Обработчик получения информации о улучшениях компании. Отправляет ответ на request_id", 
    datatypes=[
        "company_id: int", 
        "request_id: str"
        ])
async def handle_get_company_improvement_info(client_id: str, message: dict):
    """Обработчик получения информации о улучшениях компании"""

    conditions = {
        "company_id": message.get("company_id")
    }

    for i in conditions.values():
        if i is None: return {"error": "Missing required fields."}

    company = Company(_id=conditions["company_id"]).reupdate()
    if not company: return {"error": "Company not found."}

    imp = company.get_improvements()
    return imp

@message_handler(
    "update-company-improve", 
    doc="Обработчик улучшения компании. Требуется пароль для взаимодействия.",
    datatypes=[
        "company_id: int",
        "improvement_type: str",

        "password: str"
    ],
    messages=["api-company_improvement_upgraded (broadcast)"]
)
async def handle_update_company_improve(client_id: str, message: dict):
    """Обработчик улучшения компании"""

    password = message.get("password")
    company_id = message.get("company_id")
    improvement_type = message.get("improvement_type")

    for i in [company_id, improvement_type, password]:
        if i is None: return {"error": "Missing required fields."}

    try:
        check_password(password)

        company = Company(_id=company_id).reupdate()
        if not company: raise ValueError("Company not found.")

        company.improve(improvement_type)

    except ValueError as e:
        return {"error": str(e)}

@message_handler(
    "company-take-credit", 
    doc="Обработчик получения кредита компанией. Требуется пароль для взаимодействия. Отправляет ответ на request_id.",
    datatypes=[
        "company_id: int",
        "amount: int",
        "period: int",

        "request_id: str",
        "password: str"
    ],
    messages=["api-company_credit_taken (broadcast)"]
)
async def handle_company_take_credit(client_id: str, message: dict):
    """Обработчик получения кредита компанией"""

    password = message.get("password")
    company_id = message.get("company_id")
    amount = message.get("amount")
    period = message.get("period")

    for i in [company_id, amount, period, password]:
        if i is None: return {"error": "Missing required fields."}

    try:
        check_password(password)

        company = Company(_id=company_id).reupdate()
        if not company: raise ValueError("Company not found.")

        credit_data = company.take_credit(amount, period)

    except ValueError as e:
        return {"error": str(e)}

    return credit_data

@message_handler(
    "company-pay-credit", 
    doc="Обработчик погашения кредита компанией. Требуется пароль для взаимодействия.",
    datatypes=[
        "company_id: int",
        "credit_index: int",
        "amount: int",

        "password: str"
    ],
    messages=["api-company_credit_paid (broadcast)"]
)
async def handle_company_pay_credit(client_id: str, message: dict):
    """Обработчик погашения кредита компанией"""

    password = message.get("password")
    company_id = message.get("company_id")
    credit_index = message.get("credit_index")
    amount = message.get("amount")

    for i in [company_id, credit_index, amount, password]:
        if i is None: return {"error": "Missing required fields."}

    try:
        check_password(password)

        company = Company(_id=company_id).reupdate()
        if not company: raise ValueError("Company not found.")

        company.pay_credit(credit_index, amount)

    except ValueError as e:
        return {"error": str(e)}

@message_handler(
    "company-take-deposit", 
    doc="Обработчик создания вклада компанией. Требуется пароль для взаимодействия. Отправляет ответ на request_id.",
    datatypes=[
        "company_id: int",
        "amount: int",
        "period: int",

        "request_id: str",
        "password: str"
    ],
    messages=["api-company_deposit_taken (broadcast)"]
)
async def handle_company_take_deposit(client_id: str, message: dict):
    """Обработчик создания вклада компанией"""

    password = message.get("password")
    company_id = message.get("company_id")
    amount = message.get("amount")
    period = message.get("period")

    for i in [company_id, amount, period, password]:
        if i is None: return {"error": "Missing required fields."}

    try:
        check_password(password)

        company = Company(_id=company_id).reupdate()
        if not company: raise ValueError("Company not found.")

        deposit_data = company.take_deposit(amount, period)

    except ValueError as e:
        return {"error": str(e)}

    return deposit_data

@message_handler(
    "company-withdraw-deposit", 
    doc="Обработчик снятия вклада компанией. Требуется пароль для взаимодействия.",
    datatypes=[
        "company_id: int",
        "deposit_index: int",

        "password: str"
    ],
    messages=["api-company_deposit_withdrawn (broadcast)"]
)
async def handle_company_withdraw_deposit(client_id: str, message: dict):
    """Обработчик снятия вклада компанией"""

    password = message.get("password")
    company_id = message.get("company_id")
    deposit_index = message.get("deposit_index")

    for i in [company_id, deposit_index, password]:
        if i is None: return {"error": "Missing required fields."}

    try:
        check_password(password)

        company = Company(_id=company_id).reupdate()
        if not company: raise ValueError("Company not found.")

        company.withdraw_deposit(deposit_index)

    except ValueError as e:
        return {"error": str(e)}

    return {"success": True}

@message_handler(
    "company-pay-taxes", 
    doc="Обработчик погашения налогов компанией. Требуется пароль для взаимодействия.",
    datatypes=[
        "company_id: int",
        "amount: int",

        "password: str"
    ],
    messages=["api-company_tax_paid (broadcast)"]
)
async def handle_company_pay_taxes(client_id: str, message: dict):
    """Обработчик погашения налогов компанией"""

    password = message.get("password")
    company_id = message.get("company_id")
    amount = message.get("amount")

    for i in [company_id, amount, password]:
        if i is None: return {"error": "Missing required fields."}

    try:
        check_password(password)

        company = Company(_id=company_id).reupdate()
        if not company: raise ValueError("Company not found.")

        company.pay_taxes(amount)

    except ValueError as e:
        return {"error": str(e)}

@message_handler(
    "company-complete-free-factories", 
    doc="Обработчик массовой перекомплектации свободных фабрик компании. Требуется пароль для взаимодействия.",
    datatypes=[
        "company_id: int",
        "find_resource: Optional[str]",
        "new_resource: str",
        "count: int",
        "produce_status: Optional[bool]",

        "password: str"
    ],
    messages=["api-factory-start-complectation (broadcast для каждой фабрики)"]
)
async def handle_company_complete_free_factories(client_id: str, message: dict):
    """Обработчик массовой перекомплектации свободных фабрик компании"""

    password = message.get("password")
    company_id = message.get("company_id")
    find_resource = message.get("find_resource")  
    new_resource = message.get("new_resource")
    count = message.get("count")
    produce_status = message.get("produce_status", False)

    # Проверяем обязательные параметры
    for param_name, param_value in [("company_id", company_id), ("new_resource", new_resource), ("count", count), ("password", password)]:
        if param_value is None:
            return {"error": f"Missing required field: {param_name}"}

    try:
        check_password(password)

        company = Company(_id=company_id).reupdate()
        if not company: raise ValueError("Company not found.")

        # Вызываем метод массовой перекомплектации
        company.complete_free_factories(
            find_resource=find_resource,
            new_resource=new_resource,
            count=count,
            produce_status=produce_status
        )

        return {"success": True}

    except ValueError as e:
        return {"error": str(e)}


@message_handler(
    "notforgame-update-company-balance", 
    doc="Обработчик обновления баланса компании. Требуется пароль для взаимодействия. НЕ ИСПОЛЬЗОВАТЬ В ИГРОВОМ ПРОЦЕССЕ!",
    datatypes=[
        "company_id: int",
        "balance_change: int",
        "password: str"
    ],
    messages=[]
)
async def handle_notforgame_update_company_balance(
    client_id: str, message: dict):
    """Обработчик обновления баланса компании"""

    password = message.get("password", 0)
    company_id = message.get("company_id", 0)
    balance_change = message.get("balance_change", 0)

    for i in [company_id, password, balance_change]:
        if i is None: 
            return {"error": "Missing required fields."}


    try:
        check_password(password)

        company = Company(_id=company_id).reupdate()
        if not company: raise ValueError("Company not found.")

        if balance_change > 0:
            company.add_balance(balance_change)
        else:
            company.remove_balance(abs(balance_change))

    except ValueError as e:
        return {"error": str(e)}

@message_handler(
    "notforgame-update-company-items", 
    doc="Обработчик обновления предметов компании. Требуется пароль для взаимодействия. НЕ ИСПОЛЬЗОВАТЬ В ИГРОВОМ ПРОЦЕССЕ!",
    datatypes=[
        "company_id: int",
        "item_id: str",
        "quantity_change: int",
        "ignore_space: Optional[bool]",
        "password: str"
    ],
    messages=[]
)
async def handle_notforgame_update_company_items(
    client_id: str, message: dict):
    """Обработчик обновления предметов компании"""

    password = message.get("password", 0)
    company_id = message.get("company_id", 0)
    item_id = message.get("item_id", "")
    quantity_change = message.get("quantity_change", 0)
    ignore_space = message.get("ignore_space", False)

    for i in [company_id, password, item_id, quantity_change]:
        if i is None: 
            return {"error": "Missing required fields."}


    try:
        check_password(password)

        company = Company(_id=company_id).reupdate()
        if not company: raise ValueError("Company not found.")

        if quantity_change > 0:
            company.add_resource(item_id, quantity_change, ignore_space)
        else:
            company.remove_resource(item_id, 
                                    abs(quantity_change))

    except ValueError as e:
        return {"error": str(e)}

@message_handler(
    "notforgame-update-company-name", 
    doc="Обработчик обновления названия компании. Требуется пароль для взаимодействия.",
    datatypes=[
        "company_id: int",
        "new_name: str",
        "password: str"
    ],
    messages=['api-company_name_updated (broadcast)']
)
async def handle_notforgame_update_company_name(
    client_id: str, message: dict):
    """Обработчик обновления названия компании"""

    password = message.get("password", 0)
    company_id = message.get("company_id", 0)
    new_name = message.get("new_name", "")

    for i in [company_id, password, new_name]:
        if i is None: 
            return {"error": "Missing required fields."}


    try:
        check_password(password)

        company = Company(_id=company_id).reupdate()
        if not company: raise ValueError("Company not found.")

        company.name = new_name
        company.save_to_base()

        await websocket_manager.broadcast({
            "type": "api-company_name_updated",
            "data": {
                "company_id": company.id,
                "new_name": company.name
            }
        })

    except ValueError as e:
        return {"error": str(e)}

