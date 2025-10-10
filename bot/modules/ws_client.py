import os
import time
from typing import Optional, Literal, Any
from global_modules.api_client import create_client
from global_modules.logs import Logger


UPDATE_PASSWORD = os.getenv("UPDATE_PASSWORD", "default_password")

# Настройка логирования
bot_logger = Logger.get_logger("bot")

# Создаем WebSocket клиента
ws_client = create_client(
    client_id=f"bot_client_{int(time.time())}", 
    uri=os.getenv("WS_SERVER_URI", "ws://localhost:8000/ws/connect"),
    logger=bot_logger
)

# Функции для работы с компаниями
async def get_companies(session_id: Optional[int] = None, in_prison: Optional[bool] = None, cell_position: Optional[str] = None):
    """Получение списка компаний"""
    return await ws_client.send_message(
        "get-companies",
        session_id=session_id,
        in_prison=in_prison,
        cell_position=cell_position,
        wait_for_response=True,
        timeout=50
    )

async def get_company(id: Optional[int] = None, name: Optional[str] = None, reputation: Optional[int] = None, 
                     balance: Optional[int] = None, in_prison: Optional[bool] = None, 
                     session_id: Optional[str] = None, cell_position: Optional[str] = None):
    """Получение компании"""
    return await ws_client.send_message(
        "get-company",
        id=id,
        name=name,
        reputation=reputation,
        balance=balance,
        in_prison=in_prison,
        session_id=session_id,
        cell_position=cell_position,
        wait_for_response=True
    )

async def create_company(name: str, who_create: int):
    """Создание компании"""
    return await ws_client.send_message(
        "create-company",
        name=name,
        who_create=who_create,
        password=UPDATE_PASSWORD,
        wait_for_response=True
    )

async def update_company_add_user(user_id: int, secret_code: int):
    """Добавление пользователя в компанию"""
    return await ws_client.send_message(
        "update-company-add-user",
        user_id=user_id,
        secret_code=secret_code,
        password=UPDATE_PASSWORD,
        wait_for_response=True
    )

async def set_company_position(company_id: int, x: int, y: int):
    """Обновление местоположения компании"""
    return await ws_client.send_message(
        "set-company-position",
        company_id=company_id,
        x=x,
        y=y,
        password=UPDATE_PASSWORD,
        wait_for_response=True
    )

async def update_company_left_user(user_id: int, company_id: str):
    """Выход пользователя из компании"""
    return await ws_client.send_message(
        "update-company-left-user",
        user_id=user_id,
        company_id=company_id,
        password=UPDATE_PASSWORD,
        wait_for_response=True
    )

async def delete_company(company_id: str):
    """Удаление компании"""
    return await ws_client.send_message(
        "delete-company",
        company_id=company_id,
        password=UPDATE_PASSWORD,
        wait_for_response=True
    )

async def get_company_cell_info(company_id: int):
    """Получение информации о ячейке компании"""
    return await ws_client.send_message(
        "get-company-cell-info",
        company_id=company_id,
        wait_for_response=True
    )

async def get_company_improvement_info(company_id: int):
    """Получение информации о улучшениях компании"""
    return await ws_client.send_message(
        "get-company-improvement-info",
        company_id=company_id,
        wait_for_response=True
    )

async def update_company_improve(company_id: str, improvement_type: str):
    """Улучшение компании"""
    return await ws_client.send_message(
        "update-company-improve",
        company_id=company_id,
        improvement_type=improvement_type,
        password=UPDATE_PASSWORD,
        wait_for_response=True
    )

async def company_take_credit(company_id: str, amount: int, period: int):
    """Получение кредита компанией"""
    return await ws_client.send_message(
        "company-take-credit",
        company_id=company_id,
        amount=amount,
        period=period,
        password=UPDATE_PASSWORD,
        wait_for_response=True
    )

async def company_pay_credit(company_id: str, credit_index: int, amount: int):
    """Погашение кредита компанией"""
    return await ws_client.send_message(
        "company-pay-credit",
        company_id=company_id,
        credit_index=credit_index,
        amount=amount,
        password=UPDATE_PASSWORD,
        wait_for_response=True
    )

async def company_pay_taxes(company_id: str, amount: int):
    """Погашение налогов компанией"""
    return await ws_client.send_message(
        "company-pay-taxes",
        company_id=company_id,
        amount=amount,
        password=UPDATE_PASSWORD,
        wait_for_response=True
    )

async def company_complete_free_factories(company_id: int, new_resource: str, count: int, 
                                        find_resource: Optional[str] = None, 
                                        produce_status: Optional[bool] = None):
    """Массовая перекомплектация свободных фабрик компании"""
    return await ws_client.send_message(
        "company-complete-free-factories",
        company_id=company_id,
        find_resource=find_resource,
        new_resource=new_resource,
        count=count,
        produce_status=produce_status,
        password=UPDATE_PASSWORD,
        wait_for_response=True
    )

async def get_company_users(company_id: int):
    """Получение списка пользователей компании"""
    return await ws_client.send_message(
        "get-company-users",
        company_id=company_id,
        wait_for_response=True
    )

# Функции для работы с фабриками
async def get_factories(company_id: int, complectation: Optional[str] = None, 
                       produce: Optional[bool] = None, is_auto: Optional[bool] = None):
    """Получение списка фабрик"""
    return await ws_client.send_message(
        "get-factories",
        company_id=company_id,
        complectation=complectation,
        produce=produce,
        is_auto=is_auto,
        wait_for_response=True
    )

async def get_factory(factory_id: int):
    """Получение информации о фабрике"""
    return await ws_client.send_message(
        "get-factory",
        factory_id=factory_id,
        wait_for_response=True
    )

async def factory_recomplectation(factory_id: int, new_complectation: str):
    """Перекомплектация фабрики"""
    return await ws_client.send_message(
        "factory-recomplectation",
        factory_id=factory_id,
        new_complectation=new_complectation,
        password=UPDATE_PASSWORD,
        wait_for_response=True
    )

async def factory_set_produce(factory_id: int, produce: bool):
    """Установка статуса производства фабрики"""
    return await ws_client.send_message(
        "factory-set-produce",
        factory_id=factory_id,
        produce=produce,
        wait_for_response=True
    )

async def factory_set_auto(factory_id: int, is_auto: bool):
    """Установка статуса автоматического производства фабрики"""
    return await ws_client.send_message(
        "factory-set-auto",
        factory_id=factory_id,
        is_auto=is_auto,
        wait_for_response=True
    )

# Функции для работы с сессиями
async def get_sessions(stage: Optional[str] = None):
    """Получение списка сессий"""
    return await ws_client.send_message(
        "get-sessions",
        stage=stage,
        wait_for_response=True
    )

async def get_session(session_id: Optional[str] = None, stage: Optional[str] = None):
    """Получение сессии"""
    return await ws_client.send_message(
        "get-session",
        session_id=session_id,
        stage=stage,
        wait_for_response=True
    )

async def create_session(session_id: Optional[str] = None):
    """Создание сессии"""
    return await ws_client.send_message(
        "create-session",
        session_id=session_id,
        password=UPDATE_PASSWORD,
        wait_for_response=True
    )

async def update_session_stage(session_id: Optional[str] = None, 
                              stage: Literal['FreeUserConnect', 'CellSelect', 'Game', 'End'] = 'FreeUserConnect'):
    """Обновление стадии сессии"""
    return await ws_client.send_message(
        "update-session-stage",
        session_id=session_id,
        stage=stage,
        password=UPDATE_PASSWORD,
        wait_for_response=True
    )

async def get_sessions_free_cells(session_id: str):
    """Получение свободных клеток сессии"""
    return await ws_client.send_message(
        "get-sessions-free-cells",
        session_id=session_id,
        wait_for_response=True
    )

async def delete_session(session_id: str, really: bool = False):
    """Удаление сессии"""
    return await ws_client.send_message(
        "delete-session",
        session_id=session_id,
        password=UPDATE_PASSWORD,
        really=really,
        wait_for_response=True
    )

# Функции для работы с пользователями
async def get_users(company_id: Optional[int] = None, session_id: Optional[str] = None):
    """Получение списка пользователей"""
    return await ws_client.send_message(
        "get-users",
        company_id=company_id,
        session_id=session_id,
        wait_for_response=True
    )

async def get_user(id: Optional[int] = None, username: Optional[str] = None, 
                  company_id: Optional[int] = None, session_id: Optional[str] = None):
    """Получение пользователя"""
    return await ws_client.send_message(
        "get-user",
        id=id,
        username=username,
        company_id=company_id,
        session_id=session_id,
        wait_for_response=True
    )

async def create_user(user_id: int, username: str, session_id: str):
    """Создание пользователя"""
    return await ws_client.send_message(
        "create-user",
        user_id=user_id,
        username=username,
        password=UPDATE_PASSWORD,
        session_id=session_id,
        wait_for_response=True
    )

async def update_user(user_id: int, username: Optional[str] = None, company_id: Optional[int] = None):
    """Обновление пользователя"""
    return await ws_client.send_message(
        "update-user",
        user_id=user_id,
        username=username,
        company_id=company_id,
        password=UPDATE_PASSWORD,
        wait_for_response=True
    )

async def delete_user(user_id: int):
    """Удаление пользователя"""
    return await ws_client.send_message(
        "delete-user",
        user_id=user_id,
        password=UPDATE_PASSWORD,
        wait_for_response=True
    )

# Утилитарные функции
async def ping(timestamp: str = "", content: Any = None):
    """Ping сообщение"""
    return await ws_client.send_message(
        "ping",
        timestamp=timestamp,
        content=content,
        wait_for_response=True
    )
