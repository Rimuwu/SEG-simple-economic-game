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
    # asyncio.create_task(initial_setup())

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
    user2.add_to_company(company.secret_code)

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

    company.set_position(0, 0)

    session.update_stage(SessionStages.Game)
    company.reupdate()

    fs = company.get_factories()
    # fs[0].set_produce(True)
    # fs[0].set_auto(True)
    
    # for factory in fs:
    #     if factory.complectation == None:
    #         factory.pere_complete(
    #             random.choice(['generator', 'body_armor', 'tent'])
    #         )
    print('===' * 50)
    print(len(fs))
    
    company.complete_free_factories(
        find_resource=None,
        new_resource='generator',
        count=10
    )

    session.update_stage(SessionStages.Game)
    company.reupdate()
    
    session.update_stage(SessionStages.Game)
    company.reupdate()


    # company.add_resource('wood', 10)
    # # company.add_resource('oil', 90)


    # try:
    #     company.add_resource('wood', 5)
    # except Exception as e:
    #     print(e)

    # company.remove_resource('wood', 5)
    
    # print(
    #     company.get_max_warehouse_size()
    # )

    # company.improve('warehouse')
    
    # print(
    #     company.get_max_warehouse_size()
    # )
    
    # print('===' * 50)

    # company.add_balance(10000)

    # session.update_stage(SessionStages.Game)
    # company.reupdate()

    # company.take_credit(5000, 5)

    # company.add_balance(10000)

    # session.update_stage(SessionStages.Game)
    # company.reupdate()
    
    # company.add_balance(10000)

    # company.pay_taxes(600)

    # session.update_stage(SessionStages.Game)
    # company.reupdate()
    
    # company.pay_taxes(1200)
    # company.pay_credit(0, 5040)

    # session.update_stage(SessionStages.Game)
    # company.reupdate()
    
    # company.pay_credit(0, 5040)

    # company.remove_reputation(20)

    # for i in range(15):
    #     session.update_stage(SessionStages.Game)
    #     await sleep(0.5)

