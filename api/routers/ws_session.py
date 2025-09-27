from modules import websocket_manager
from modules.ws_hadnler import message_handler
from modules.json_database import just_db
from game.session import session_manager, Session, SessionStages
from modules.check_password import check_password

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

@message_handler(
    "create-session", 
    doc="Обработчик создания сессии. Отправляет ответ на request_id. Требуется пароль для взаимодействия.",
    datatypes=[
        "session_id: Optional[str]",
        "password: str",
        "request_id: str"
    ]
)
async def handle_create_session(client_id: str, message: dict):
    """Обработчик создания сессии"""

    session_id = message.get("session_id", "")
    password = message.get("password", "")
    
    try:
        check_password(password)
    except ValueError as e:
        return {"error": str(e)}

    try:
        session = session_manager.create_session(session_id=session_id)
    except ValueError as e:
        return {"error": str(e)}

    return {"session": session.__dict__}

@message_handler(
    "update-session-stage", 
    doc="Обработчик обновления стадии сессии. Требуется пароль для взаимодействия.",
    datatypes=[
        "session_id: Optional[str]",
        "stage: Literal['FreeUserConnect', 'CellSelect', 'Game', 'End']",
        "password: str",
    ],
    messages=["api-update_session_stage (broadcast)"]
)
async def handle_update_session_stage(client_id: str, message: dict):
    """Обработчик обновления стадии сессии"""

    session_id = message.get("session_id", "")
    stage: str = message.get("stage", "")
    password = message.get("password", "")

    stages_to_types = {
        "FreeUserConnect": SessionStages.FreeUserConnect,
        "CellSelect": SessionStages.CellSelect,
        "Game": SessionStages.Game,
        "End": SessionStages.End
    }

    try:
        check_password(password)

        session = session_manager.get_session(session_id=session_id)
        if not session: raise ValueError("Session not found.")

        if stage not in stages_to_types:
            raise ValueError("Invalid stage value.")

        session.update_stage(stages_to_types[stage])
    except ValueError as e:
        return {"error": str(e)}


@message_handler(
    "get-sessions-free-cells", 
    doc="Обработчик получения свободных клеток сессии. Отправляет ответ на request_id",
    datatypes=[
        "session_id: str",
        "request_id: str",
    ]
)
async def handle_get_sessions_free_cells(
    client_id: str, message: dict):
    """Обработчик получения свободных клеток сессии"""

    session_id = message.get("session_id", "")

    try:
        session = session_manager.get_session(session_id=session_id)
        if not session: raise ValueError("Session not found.")

        free_cells = session.get_free_cells()
        return {"free_cells": free_cells}

    except ValueError as e:
        return {"error": str(e)}

@message_handler(
    "delete-session", 
    doc="Обработчик удаления сессии. ВНИМАНИЕ! Это приведёт к удалению всех привязанных игроков и компаний. Требуется пароль для взаимодействия. Требуется `really=true` для подтверждения удаления.",
    datatypes=[
        "session_id: str",
        "password: str",
        "really: bool"
    ],
    messages=["api-session_deleted (broadcast)"]
)
async def handle_delete_session(
    client_id: str, message: dict):
    """Обработчик удаления сессии"""

    session_id = message.get("session_id", "")
    password = message.get("password", "")
    really = message.get("really", False)

    try:
        check_password(password)

        session = session_manager.get_session(session_id=session_id)
        if not session: raise ValueError("Session not found.")

        if not really:
            raise ValueError("Confirmation required to delete session.")

        session.delete()
    except ValueError as e:
        return {"error": str(e)}