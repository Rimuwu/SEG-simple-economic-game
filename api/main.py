from asyncio import sleep
import asyncio
import random
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

from game.stages import stage_game_updater
from global_modules.api_configurate import get_fastapi_app
from global_modules.logs import main_logger
from modules.json_database import just_db
from modules.sheduler import scheduler
from game.session import session_manager
from game.exchange import Exchange

# Импортируем роуты
from routers import connect_ws

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    main_logger.info("API is starting up...")
    main_logger.info("Creating missing tables on startup...")

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

    main_logger.info("Loading sessions from database...")
    session_manager.load_from_base()

    await sleep(5)
    main_logger.info("Starting task scheduler...")

    asyncio.create_task(scheduler.start())
    asyncio.create_task(test1())

    yield

    main_logger.info("API is shutting down...")

    main_logger.info("Stopping task scheduler...")
    scheduler.stop()
    scheduler.cleanup_shutdown_tasks()

app = get_fastapi_app(
    title="API",
    version="1.0.0",
    description="SEG API",
    debug=False,
    lifespan=lifespan,
    limiter=False,
    middlewares=[],
    routers=[
        connect_ws.router
    ],
    api_logger=main_logger
)

@app.get("/")
async def root(request: Request):
    return {"message": f"{app.description} is running! v{app.version}"}

async def test1():
    
    
    from game.user import User
    from game.session import Session, session_manager, SessionStages
    from game.company import Company

    await asyncio.sleep(2)

    print("Performing initial setup...")

    # try:
    if session_manager.get_session('AFRIKA'):
        session = session_manager.get_session('AFRIKA')
        session.delete()

    session = session_manager.create_session('AFRIKA')
    # return
    
    # just_db.update(
    #     'sessions', {'session_id': 'AFRIKA'}, 
    #     {'stage': 'CellSelect'}
    # )

    session.update_stage(SessionStages.FreeUserConnect, True)
    user: User = User().create(_id=1, 
                         username="TestUser", 
                         session_id=session.session_id)
    user2: User = User().create(_id=2, 
                         username="TestUser2", 
                         session_id=session.session_id)

    company = user.create_company("TestCompany")
    company.set_owner(1)

    company2 = user2.create_company("TestCompany2")
    company2.set_owner(2)

    # user2.add_to_company(company.secret_code)

    session.update_stage(SessionStages.CellSelect, True)
    company.reupdate()
    company2.reupdate()

    # free_cells = session.get_free_cells()
    # print(free_cells)

    company.set_position(0, 0)
    company2.set_position(2, 3)
    session.reupdate()

    # free_cells = session.get_free_cells()
    # print(free_cells)

    session.update_stage(SessionStages.Game, True)
    company.reupdate()
    company2.reupdate()

    # print(company.warehouses.keys())

    c_m_k_1 = list(company.warehouses.keys())[0]
    col_1 = company.warehouses[c_m_k_1]
    
    c_m_k_2 = list(company2.warehouses.keys())[0]
    col_2 = company2.warehouses[c_m_k_2]
    
    print(company.warehouses, company2.warehouses)
    print(c_m_k_1, c_m_k_2)
    
    exchange = Exchange(0).create(
        company.id, session.session_id, 
        c_m_k_1, col_1 // 2, 2, 'barter', 0,
        c_m_k_2, col_2 // 2
    )
    

    # exchange = Exchange(0).create(
    #     company.id, session.session_id, 
    #     c_m_k_1, col_1 // 2, 2, 'money', 1000
    # )
    

    company.reupdate()
    company2.reupdate()
    print(company.warehouses, company2.warehouses)

    exchange.buy(company2.id)
    
    company.reupdate()
    company2.reupdate()
    print(company.warehouses, company2.warehouses)
    
    exchange.reupdate()
    exchange.cancel_offer()
    
    
    company.reupdate()
    company2.reupdate()
    print(company.warehouses, company2.warehouses)

    # session.update_stage(SessionStages.Game)
    # company.reupdate()
    # company2.reupdate()