
import asyncio
import random
from typing import Optional
from global_modules.models.cells import Cells
from global_modules.db.baseclass import BaseClass
from global_modules.models.resources import Production, Resource
from modules.json_database import just_db
from global_modules.load_config import ALL_CONFIGS, Resources, Improvements, Settings, Capital, Reputation
from modules.function_way import determine_city_branch
from modules.websocket_manager import websocket_manager

RESOURCES: Resources = ALL_CONFIGS["resources"]
CELLS: Cells = ALL_CONFIGS['cells']
IMPROVEMENTS: Improvements = ALL_CONFIGS['improvements']
SETTINGS: Settings = ALL_CONFIGS['settings']
CAPITAL: Capital = ALL_CONFIGS['capital']
REPUTATION: Reputation = ALL_CONFIGS['reputation']

NAMES = [
    "Золотогорск",
    "Лесной Град",
    "Речной Край",
    "Горный Хребет",
    "Солнечный Берег",
    "Тёмный Лес",
    "Светлый Путь",
    "Железный Город",
    "Кристалльный Остров",
    "Огненная Долина",
    "Ледяной Пик",
    "Морской Ветер",
    "Пустынный Оазис",
    "Небесный Город",
    "Земляной Вал",
    "Водный Мир",
    "Воздушный Замок",
    "Каменный Щит",
    "Деревянный Лабиринт",
    "Металлический Гигант",
    "Хлопковый Рай",
    "Нефтяной Клад",
    "Дубовый Лес",
    "Стальной Пик",
    "Шелковый Путь",
    "Угольный Бассейн",
    "Рубиновый Город",
    "Изумрудный Остров",
    "Сапфировый Берег",
    "Алмазный Край",
    "Бриллиантовый Вал",
    "Жемчужный Мир",
    "Янтарный Замок",
    "Ониксовый Щит",
    "Малахитовый Лабиринт",
    "Обсидиановый Гигант",
    "Топазовый Рай",
    "Аметистовый Клад",
    "Гранатовый Лес",
    "Аквамариновый Пик",
    "Лазуритовый Ветер",
    "Турмалиновый Оазис",
    "Опаловый Город",
    "Гелиодоровый Долина",
    "Цирконовый Пик",
    "Корундовый Ветер",
    "Спинелевый Оазис",
    "Танзанитовый Город",
    "Александритовый Край",
    "Берилловый Вал"
]

class Citie(BaseClass):

    __tablename__ = "cities"
    __unique_id__ = "id"
    __db_object__ = just_db

    def __init__(self, id: int = 0):
        self.id: int = id
        self.session_id: str = ""
        self.cell_position: str = ""  # "x.y"
        self.branch: str = ""  # Приоритетная ветка: 'oil', 'metal', 'wood', 'cotton'

        self.name: str = ""

        # Спрос на товары: {resource_id: {'amount': int, 'price': int}}
        self.demands: dict = {}

    def create(self, session_id: str, x: int, y: int, 
               name: Optional[str] = None):
        """ Создание нового города
        
        Args:
            session_id: ID сессии
            x: координата X
            y: координата Y
        """
        from game.session import session_manager

        session = session_manager.get_session(session_id)
        if not session:
            raise ValueError("Session not found")
        
        self.id = self.__db_object__.max_id_in_table(self.__tablename__) + 1
        self.session_id = session_id
        self.cell_position = f"{x}.{y}"
        
        # Определяем приоритетную ветку на основе соседних клеток
        self.branch = determine_city_branch(
            x, y, session_id, session.cells, session.map_size, CELLS
        )
        self.name = name if name else random.choice(NAMES)

        # Инициализируем спрос
        self._update_demands(session)

        self.save_to_base()
        self.reupdate()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-city-create",
            "data": {
                "city": self.to_dict()
            }
        }))

        return self

    def _update_demands(self, session=None):
        """Обновляет спрос города на товары
        
        Args:
            session: объект Session (опционально, для оптимизации)
        """
        if session is None:
            from game.session import session_manager
            session = session_manager.get_session(self.session_id)
        
        if not session:
            return
        
        # Получаем количество пользователей в сессии (минимум 1 для расчётов)
        users_count = max(len(session.users), 1)
        
        # Очищаем старый спрос
        self.demands = {}
        
        # Получаем все ресурсы, которые не являются сырьем
        for resource_id, resource in RESOURCES.resources.items():
            if not resource.raw:
                # Базовое количество: massModifier определяет масштаб
                # Для товаров с massModifier=100 будет ~100 единиц на игрока
                base_amount = resource.massModifier * users_count

                # Модификатор для приоритетной ветки (увеличиваем спрос на 50%)
                branch_modifier = 1.5 if resource.branch == self.branch else 1.0

                # Финальное количество с рандомизацией ±30%
                amount_variation = random.uniform(0.4, 1.6)
                amount = int(base_amount * branch_modifier * amount_variation)

                # Ограничение: минимум зависит от massModifier
                min_amount = max(1, int(
                    resource.massModifier * 0.5)
                                 )
                max_amount = int(resource.massModifier * users_count * 3)
                amount = max(min_amount, min(amount, max_amount))

                # Цена с рандомизацией ±20%
                price_variation = random.uniform(0.8, 1.2)
                price = int(resource.basePrice * price_variation)

                # Бонус к цене для приоритетной ветки (+50%)
                if resource.branch == self.branch:
                    price = int(price * 1.5)

                # # Округляем цену до целого числа, но сохраняем минимум базовую цену
                # price = max(resource.basePrice, int(price))
                
                self.demands[resource_id] = {
                    'amount': amount,
                    'price': price
                }

    def on_new_game_stage(self):
        """Вызывается при начале нового игрового хода"""
        from game.session import session_manager
        
        session = session_manager.get_session(self.session_id)
        if not session:
            return
        
        # Обновляем спрос на товары
        self._update_demands(session)
        
        self.save_to_base()
        
        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-city-update-demands",
            "data": {
                "city_id": self.id,
                "session_id": self.session_id,
                "demands": self.demands
            }
        }))

    def sell_resource(self, company_id: int, resource_id: str, amount: int) -> dict:
        """Продает ресурс городу
        
        Args:
            company_id: ID компании
            resource_id: ID ресурса
            amount: количество для продажи
            
        Returns:
            dict с результатом операции
        """
        from game.company import Company
        
        # Проверяем наличие спроса
        if resource_id not in self.demands:
            raise ValueError("City doesn't need this resource")
        
        demand = self.demands[resource_id]
        
        # Проверяем количество
        if amount > demand['amount']:
            raise ValueError(f"City needs only {demand['amount']} units")
        
        # Получаем компанию
        company = Company(company_id).reupdate()
        if not company or company.session_id != self.session_id:
            raise ValueError("Invalid company")
        
        # Проверяем наличие ресурса у компании
        if resource_id not in company.warehouses or company.warehouses[resource_id] < amount:
            raise ValueError("Not enough resources")
        
        # Проводим транзакцию
        company.remove_resource(resource_id, amount)
        
        # Начисляем деньги компании
        total_price = demand['price'] * amount
        company.add_balance(total_price)
        
        # Уменьшаем спрос
        self.demands[resource_id]['amount'] -= amount
        if self.demands[resource_id]['amount'] <= 0:
            del self.demands[resource_id]
        
        self.save_to_base()
        
        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-city-trade",
            "data": {
                "city_id": self.id,
                "company_id": company_id,
                "resource_id": resource_id,
                "amount": amount,
                "total_price": total_price
            }
        }))
        
        return {
            "success": True,
            "total_price": total_price,
            "remaining_demand": self.demands.get(resource_id, {}).get('amount', 0)
        }

    def get_position(self) -> tuple[int, int]:
        """Возвращает координаты города"""
        if not self.cell_position:
            return (0, 0)
        x, y = self.cell_position.split('.')
        return (int(x), int(y))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "cell_position": self.cell_position,
            "branch": self.branch,
            "demands": self.demands,
            
            "name": self.name
        }

    def delete(self):
        """ Удаление города
        """
        self.__db_object__.delete(self.__tablename__, id=self.id)
        
        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-city-delete",
            "data": {
                "city_id": self.id,
                "session_id": self.session_id
            }
        }))

        return True