from asyncio import sleep
import asyncio
from datetime import datetime, timedelta
import pprint
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

from global_modules.api_configurate import get_fastapi_app
from global_modules.logs import main_logger
from modules.json_database import just_db
from modules.sheduler import scheduler

# Импортируем роуты
from routers import connect_ws

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    main_logger.info("API is starting up...")
    main_logger.info("Creating missing tables on startup...")
    
    just_db.drop_all() # Тестово

    just_db.create_table('sessions') # Таблица сессий
    just_db.create_table('users') # Таблица пользователей
    just_db.create_table('companies') # Таблица компаний
    just_db.create_table('game_history') # Таблица c историей ходов
    just_db.create_table('time_schedule') # Таблица с задачами по времени
    just_db.create_table('step_schedule') # Таблица с задачами по шагам
    just_db.create_table('contracts') # Таблица с контрактами
    just_db.create_table('cities') # Таблица с городами
    just_db.create_table('exchange') # Таблица с биржей
    just_db.create_table('factories') # Таблица с заводами
    just_db.create_table('warehouse') # Таблица с складом

    main_logger.info("Starting task scheduler...")

    await sleep(5)

    asyncio.create_task(scheduler.start())
    asyncio.create_task(initial_setup())

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


async def initial_setup():

    from game.user import User
    from game.session import Session, session_manager, SessionStages
    from game.company import Company

    await asyncio.sleep(2)

    print("Performing initial setup...")

    # try:
    session = session_manager.create_session('AFRIKA')

    session.update_stage(SessionStages.FreeUserConnect)
    user: User = User().create(_id=1, 
                         username="TestUser", 
                         session_id=session.session_id)
    user2: User = User().create(_id=2, 
                         username="TestUser2", 
                         session_id=session.session_id)

    company = user.create_company("TestCompany")
    print(company.secret_code)
    user2.add_to_company(company.secret_code)

    cells = session.generate_cells()
    rows = session.map_size['rows']
    cols = session.map_size['cols']

    # a = 0
    # for r in range(rows):
    #     row = []
    #     for c in range(cols):
    #         row.append(cells[a])
    #         a += 1
    #     pprint.pprint(row)

    session.update_stage(SessionStages.CellSelect)

    free_cells = session.get_free_cells()
    print(len(free_cells))

    print(company.get_position())
    company.set_position(0, 0)
    print(company.get_position())
    print(len(session.get_free_cells()))
    
    company.add_resource('wood', 10)
    company.add_resource('oil', 90)

    print(company.get_resources())
    
    try:
        company.add_resource('wood', 5)
    except Exception as e:
        print(e)
    
    company.remove_resource('wood', 5)
    print(company.get_resources())


    print(company.get_my_cell_info())
    print(company.get_cell_type())
    
    print(company.get_improvements())

    print(company.improvements)
    company.improve('warehouse')
    
    print(company.improvements)
    
    

