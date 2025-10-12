from asyncio import sleep
import asyncio
from pprint import pprint
import random
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

from game.logistics import Logistics
from game.stages import stage_game_updater
from global_modules.api_configurate import get_fastapi_app
from modules.logs import *
from modules.json_database import just_db
from modules.sheduler import scheduler
from game.session import session_manager
from game.exchange import Exchange
from game.citie import Citie
from os import getenv
from global_modules.logs import main_logger

# Импортируем роуты
from routers import connect_ws

debug = getenv("DEBUG", "False").lower() == "true"

@asynccontextmanager
async def lifespan(app: FastAPI):

    game_logger.info("====================== GAME is starting up...")
    websocket_logger.info("====================== GAME is starting up...")
    main_logger.info("====================== GAME is starting up...")
    routers_logger.info("====================== GAME is starting up...")

    # Startup
    websocket_logger.info("Creating missing tables on startup...")
    # just_db.drop_all() # Тестово

    just_db.create_table('sessions') # Таблица сессий
    just_db.create_table('users') # Таблица пользователей
    just_db.create_table('companies') # Таблица компаний
    just_db.create_table('game_history') # Таблица c историей ходов
    just_db.create_table('time_schedule') # Таблица с задачами по времени
    just_db.create_table('step_schedule') # Таблица с задачами по шагам
    just_db.create_table('contracts') # Таблица с контрактами
    just_db.create_table('cities') # Таблица с городами
    just_db.create_table('exchanges') # Таблица с биржей
    just_db.create_table('factories') # Таблица с заводами
    just_db.create_table('item_price') # Таблица с ценами на товары
    just_db.create_table('logistics') # Таблица с логистикой

    websocket_logger.info("Loading sessions from database...")
    session_manager.load_from_base()

    await sleep(5)
    websocket_logger.info("Starting task scheduler...")

    asyncio.create_task(scheduler.start())
    if debug:
        asyncio.create_task(test1())

    yield

    websocket_logger.info("API is shutting down...")

    websocket_logger.info("Stopping task scheduler...")
    scheduler.stop()
    scheduler.cleanup_shutdown_tasks()

app = get_fastapi_app(
    title="API",
    version="6.6.6",
    description="SEG API",
    debug=False,
    lifespan=lifespan,
    limiter=False,
    middlewares=[],
    routers=[
        connect_ws.router
    ],
    api_logger=websocket_logger
)

@app.get("/")
async def root(request: Request):
    return {"message": f"{app.description} is running! v{app.version}"}

async def test1():
    
    from game.user import User
    from game.session import Session, session_manager, SessionStages
    from game.company import Company
    from game.contract import Contract

    await asyncio.sleep(2)

    print("🚀 Тестирование бартерного контракта с полным отслеживанием...")

    # Очистка и создание сессии
    if session_manager.get_session('AFRIKA'):
        session = session_manager.get_session('AFRIKA')
        session.delete()

    session = session_manager.create_session('AFRIKA')
    
    session.update_stage(SessionStages.FreeUserConnect, True)
    
    # Создание пользователей и компаний
    print("👥 Создаём поставщика и заказчика...")
    user1: User = User().create(_id=1, username="MetalSupplier", session_id=session.session_id)
    user2: User = User().create(_id=2, username="WoodCustomer", session_id=session.session_id)

    supplier = user1.create_company("MetalCorp")  # Поставщик металла
    supplier.set_owner(1)

    customer = user2.create_company("WoodCorp")   # Заказчик металла, поставщик дерева
    customer.set_owner(2)

    session.update_stage(SessionStages.CellSelect, True)
    for company in [supplier, customer]:
        company.reupdate()
    
    # Размещение компаний на карте
    supplier.set_position(0, 0)
    customer.set_position(2, 3)
    
    session.update_stage(SessionStages.Game, True)
    for company in [supplier, customer]:
        company.reupdate()
    
    # ПОЛНАЯ ОЧИСТКА ИНВЕНТАРЯ
    print("🧹 Полностью очищаем инвентарь...")
    supplier.warehouses = {}
    customer.warehouses = {}
    supplier.balance = 0
    customer.balance = 0
    
    supplier.reputation = 100
    customer.reputation = 100
    supplier.save_to_base()
    customer.save_to_base()

    print("💰")

    supplier.add_resource("metal", 50)  # Металл для поставки
    customer.add_resource("wood", 50)  # Металл для поставки
    customer.add_balance(5000, 0.0)  # Деньги для оплаты контракта

    ex = Exchange().create(
        company_id=supplier.id,
        session_id=session.session_id,
        sell_resource="metal",
        sell_amount_per_trade=10,
        count_offers=5,
        offer_type='barter',
        barter_resource="wood",
        barter_amount=5,
    )
    
    ex.buy(
        customer.id,
        5
    )
    
    session.update_stage(SessionStages.Game, True)
    session.update_stage(SessionStages.Game, True)
    session.update_stage(SessionStages.Game, True)
