from asyncio import sleep
import asyncio
from pprint import pprint
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
from game.citie import Citie

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
    just_db.create_table('item_price') # Таблица с ценами на товары

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
    supplier.save_to_base()
    customer.save_to_base()

    # Настройка начальных ресурсов для тестирования контракта
    print("💰 Настраиваем начальные ресурсы...")
    
    # Даём поставщику металл для поставки и заказчику деньги для оплаты
    supplier.add_resource("metal", 100)  # Металл для поставки
    customer.add_balance(5000)  # Деньги для оплаты контракта
    
    print(f"Поставщик {supplier.name}: металл = {supplier.warehouses.get('metal', 0)}, баланс = {supplier.balance}")
    print(f"Заказчик {customer.name}: баланс = {customer.balance}")

    # СОЗДАНИЕ ТЕСТОВОГО КОНТРАКТА
    print("\n📋 Создаём тестовый контракт...")
    
    try:
        # Создаём контракт: поставщик будет поставлять 10 единиц металла за 100 монет каждый ход в течение 3 ходов
        contract = Contract().create(
            supplier_company_id=supplier.id,
            customer_company_id=customer.id, 
            session_id=session.session_id,
            resource="metal",           # Поставляемый ресурс
            amount_per_turn=10,        # Количество за ход
            duration_turns=3,          # Длительность в ходах
            payment_amount=100         # Оплата за ход
        )
        
        print(f"✅ Контракт создан! ID: {contract.id}")
        print(f"   Поставляется: {contract.amount_per_turn} {contract.resource} за {contract.payment_amount} монет/ход")
        print(f"   Длительность: {contract.duration_turns} ходов")
        print(f"   Общая стоимость: {contract.payment_amount * contract.duration_turns} монет")
        
        # ПРИНЯТИЕ КОНТРАКТА
        print("\n🤝 Поставщик принимает контракт...")
        contract.accept_contract()
        
        supplier.reupdate()
        customer.reupdate()
        
        print(f"Поставщик {supplier.name}: баланс = {supplier.balance} (+{contract.payment_amount * contract.duration_turns})")
        print(f"Заказчик {customer.name}: баланс = {customer.balance} (-{contract.payment_amount * contract.duration_turns})")
        
        # ВЫПОЛНЕНИЕ КОНТРАКТА ПО ХОДАМ
        print("\n🚚 Начинаем выполнение контракта...")
        
        for turn in range(1, contract.duration_turns + 1):
            print(f"\n--- ХОД {turn} ---")
            
            # Увеличиваем счётчик ходов в сессии
            session.step += 1
            session.save_to_base()
            
            # Выполняем поставку
            try:
                contract.reupdate()  # Обновляем данные контракта
                if turn != 2:
                    contract.execute_turn(session.step)
                
                supplier.reupdate()
                customer.reupdate()
                
                print(f"✅ Поставка выполнена!")
                print(f"   Поставщик {supplier.name}: металл = {supplier.warehouses.get('metal', 0)} (-{contract.amount_per_turn})")
                print(f"   Заказчик {customer.name}: металл = {customer.warehouses.get('metal', 0)} (+{contract.amount_per_turn})")
                print(f"   Осталось ходов: {contract.remaining_turns}")
                
            except Exception as e:
                print(f"❌ Ошибка при выполнении поставки: {e}")
                break
        
        print("\n🎉 Тестирование контракта завершено!")
        
        # Проверяем итоговое состояние
        supplier.reupdate()
        customer.reupdate()
        
        print(f"\nИтоговое состояние:")
        print(f"Поставщик {supplier.name}:")
        print(f"  - Металл: {supplier.warehouses.get('metal', 0)}")
        print(f"  - Баланс: {supplier.balance}")
        print(f"  - Репутация: {supplier.reputation}")
        
        print(f"Заказчик {customer.name}:")
        print(f"  - Металл: {customer.warehouses.get('metal', 0)}")
        print(f"  - Баланс: {customer.balance}")
        print(f"  - Репутация: {customer.reputation}")
        
        # Проверяем, удалился ли контракт после завершения
        try:
            contract.reupdate()
            print(f"Контракт всё ещё существует: ID {contract.id}, осталось ходов: {contract.remaining_turns}")
        except:
            print("✅ Контракт успешно удалён после завершения")
        
    except Exception as e:
        print(f"❌ Ошибка при создании/выполнении контракта: {e}")
        import traceback
        traceback.print_exc()

    