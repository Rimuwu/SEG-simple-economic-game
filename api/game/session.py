import asyncio
from datetime import datetime, timedelta
import random
from typing import Optional
from game.stages import stage_game_updater
from global_modules.models.cells import CellType, Cells
from global_modules.models.events import Events
from modules.db import just_db
from modules.generate import generate_code
from enum import Enum
from global_modules.db.baseclass import BaseClass
from global_modules.load_config import ALL_CONFIGS, Settings
from collections import Counter
from modules.logs import game_logger
from modules.websocket_manager import websocket_manager
from modules.sheduler import scheduler
import random

# Глобальные конфиги для оптимизации
settings: Settings = ALL_CONFIGS['settings']
cells: Cells = ALL_CONFIGS['cells']
cells_types = cells.types
EVENTS: Events = ALL_CONFIGS['events']

GAME_TIME = settings.time_on_game_stage * 60
CHANGETURN_TIME = settings.time_on_change_stage * 60
TURN_CELL_TIME = settings.turn_cell_time_minutes * 60

class SessionStages(Enum):
    FreeUserConnect = "FreeUserConnect" # Подключаем пользователей
    CellSelect = "CellSelect" # Выбираем клетки
    Game = "Game" # Ход
    ChangeTurn = "ChangeTurn" # Смена хода
    End = "End" # Конец игры


class Session(BaseClass):

    __tablename__ = "sessions"
    __unique_id__ = "session_id"
    __db_object__ = just_db

    def __init__(self, session_id: str = ""): 
        self.session_id = session_id
        self.cells: list[str] = []
        self.map_size: dict = {"rows": 7, "cols": 7}
        self.map_pattern: str = "random"
        self.cell_counts: dict = {}
        self.stage: str = SessionStages.FreeUserConnect.value
        self.step: int = 0
        self.max_steps: int = 15
        self.change_turn_schedule_id: int = 0

        self.event_type: Optional[str] = None
        self.event_start: Optional[int] = None
        self.event_end: Optional[int] = None

    async def start(self):
        if not self.session_id:
            self.session_id = generate_code(32, use_letters=True, use_numbers=True, use_uppercase=True)
        self.stage = SessionStages.FreeUserConnect.value

        # Инициализируем цены для всех предметов
        await self.initialize_all_item_prices()

        await self.insert()
        return self

    async def update_stage(self, new_stage: SessionStages, 
                     whitout_shedule: bool = False):
        if not isinstance(new_stage, SessionStages):
            raise ValueError("new_stage должен быть экземпляром SessionStages Enum")

        if self.stage == SessionStages.End.value:
            raise ValueError("Нельзя изменить стадию из завершающей стадии.")

        elif self.step >= self.max_steps:
            new_stage = SessionStages.End

        elif new_stage == SessionStages.CellSelect:
            await self.generate_cells()

        elif new_stage == SessionStages.Game:
            from game.company import Company
            from game.logistics import Logistics

            if self.step == 0:
                companies = await self.companies
                for company in companies:
                    company: Company

                    if len(await company.users) == 0:
                        await company.delete()
                        game_logger.warning(f"Company {company.name} has no users and has been deleted.")
                        continue

                    elif not company.cell_position:
                        free_cells = await self.get_free_cells()

                        if not free_cells: 
                            await company.delete()
                            game_logger.warning(f"No free cells available to assign to company {company.name}. Company has been deleted.")
                            continue

                        cell = random.choice(free_cells)
                        await company.set_position(cell[0], cell[1])

                        await company.save_to_base()
                        await company.reupdate()
                        game_logger.info(f"Assigned cell {company.cell_position} to company {company.name}")

                if not whitout_shedule:

                    sh_id = await scheduler.schedule_task(
                        stage_game_updater, 
                        datetime.now() + timedelta(seconds=GAME_TIME),
                        kwargs={"session_id": self.session_id}
                    )
                    self.change_turn_schedule_id = sh_id
                    await self.save_to_base()

            for company in await self.companies:
                if company is not None:
                    await company.on_new_game_stage(self.step + 1)

            # Обновляем города
            for city in await self.cities:
                await city.on_new_game_stage()

            # Обновляем логистику
            logistics_list: list[Logistics] = await just_db.find(Logistics.__tablename__,
                                          to_class=Logistics, session_id=self.session_id) # type: ignore
            for logistics in logistics_list:
                await logistics.on_new_turn()

            # Генерируем события каждые 5 этапов
            await self.events_generator()

            self.step += 1
            await self.execute_step_schedule(self.step)

        elif new_stage == SessionStages.End:
            await self.end_game()

        old_stage = self.stage
        self.stage = new_stage.value

        await self.save_to_base()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-update_session_stage",
            "data": {
                "session_id": self.session_id,
                "new_stage": self.stage,
                "old_stage": old_stage
            }
        }))

        return self

    async def execute_step_schedule(self, step):
        from game.step_shedule import StepSchedule

        schedules: list[StepSchedule] = await just_db.find(
            "step_schedule", session_id=self.session_id, in_step=step,
            to_class=StepSchedule
        ) # type: ignore

        for schedule in schedules:
            asyncio.create_task(schedule.execute())
        return True

    async def create_step_schedule(self, in_step: int, 
                             function, **kwargs):
        from game.step_shedule import StepSchedule

        if in_step < 0:
            raise ValueError("in_step должен быть неотрицательным целым числом.")

        schedule = await StepSchedule().create(
            session_id=self.session_id, in_step=in_step)
        await schedule.add_function(function, **kwargs)

        return schedule

    def can_user_connect(self):
        return self.stage == SessionStages.FreeUserConnect.value

    async def can_add_company(self):
        col_companies = len(await self.companies)
        if col_companies >= settings.max_companies:
            return False

        return self.stage == SessionStages.FreeUserConnect.value

    def can_select_cells(self):
        return self.stage == SessionStages.CellSelect.value

    async def all_companies_have_cells(self):
        for company in await self.companies:
            if not company.cell_position:
                return False
        return True

    @property
    async def companies(self) -> list['Company']:
        from game.company import Company

        return [comp for comp in await just_db.find(
            "companies", to_class=Company, session_id=self.session_id)
                        ]

    @property
    async def users(self) -> list['User']:
        from game.user import User

        return [us for us in await just_db.find(
            "users", to_class=User, session_id=self.session_id)
                     ]

    @property
    async def cities(self) -> list['Citie']:
        from game.citie import Citie

        return [city for city in await just_db.find(
            "cities", to_class=Citie, session_id=self.session_id)
                     ]

    @property
    async def item_prices(self) -> list['ItemPrice']:
        from game.item_price import ItemPrice

        return [item_price for item_price in await just_db.find(
            "item_price", to_class=ItemPrice, session_id=self.session_id)
                     ]

    def get_cell_with_label(self, label: str, 
                            rows: int = 0,
                            cols: int = 0,
                            x_operation: int = 0,
                            y_operation: int = 0
                            ) -> list[int]:
        """
        label 
            - center, получить центральную клетку
            - random, получить случайную клетку
            - right-top, получить клетку в правом верхнем углу
            - left-top, получить клетку в левом верхнем углу
            - right-bottom, получить клетку в правом нижнем углу
            - left-bottom, получить клетку в левом нижнем углу

        x_operation 
            - смещение по X от найденной клетки
        y_operation
            - смещение по Y от найденной клетки
        """

        if label == "center":
            result_row = rows // 2
            result_col = cols // 2
        elif label == "random":
            result_row = random.randint(0, rows - 1)
            result_col = random.randint(0, cols - 1)
        elif label == "right-top":
            result_row = 0
            result_col = cols - 1
        elif label == "left-top":
            result_row = 0
            result_col = 0
        elif label == "right-bottom":
            result_row = rows - 1
            result_col = cols - 1
        elif label == "left-bottom":
            result_row = rows - 1
            result_col = 0
        else:
            result_row = rows
            result_col = cols

        # Применяем смещения
        result_row += y_operation
        result_col += x_operation

        # Проверяем границы
        result_row = max(0, min(result_row, rows - 1))
        result_col = max(0, min(result_col, cols - 1))

        return [result_row, result_col]

    async def generate_cells(self):
        if self.cells:
            raise ValueError("Клетки уже были сгенерированы для этой сессии.")

        # Ограничения на размер карты
        for r in range(self.map_size["rows"]):
            for c in range(self.map_size["cols"]):
                self.cells.append('null')

        # Установка объектов со стандартной позицией
        for cell_key, cell_info in cells.types.items():
            cell_info: CellType

            for location in cell_info.locations:
                if not location.start_point:
                    continue

                x, y = self.get_cell_with_label(
                    label=location.start_point,
                    rows=self.map_size["rows"],
                    cols=self.map_size["cols"],
                    x_operation=location.x,
                    y_operation=location.y
                )
                index = x * self.map_size["cols"] + y
                self.cells[index] = cell_key
 

        # Заполнение остальных клеток
        if self.map_pattern == "random":
            # Заполнение остальных клеток равномерно случайными типами
            types = list(
                key for key, value in cells.types.items() if value.pickable
            )
            null_indices = [i for i, cell in enumerate(self.cells) if cell == 'null']

            if null_indices and types:
                # Создаем равномерное распределение типов для null клеток
                types_cycle = (types * ((len(null_indices) // len(types)) + 1))[:len(null_indices)]
                random.shuffle(types_cycle)

                for i, index in enumerate(null_indices):
                    self.cells[index] = types_cycle[i]

        # Подсчёт каждого типа клетки
        self.cell_counts = dict(Counter(self.cells))
        game_logger.info(f"Cell counts: {self.cell_counts}")

        await self.save_to_base()
        
        # Создаём города на клетках с типом 'city'
        await self._create_cities()
        
        return self.cells

    async def _create_cities(self):
        """Создаёт города на клетках типа 'city'"""
        from game.citie import Citie, NAMES

        cities_count = self.cell_counts['city']
        city_names = random.sample(NAMES, cities_count)
        city_index = 0

        for index, cell_type in enumerate(self.cells):
            if cell_type == 'city':
                # Вычисляем координаты из индекса
                x = index // self.map_size["cols"]
                y = index % self.map_size["cols"]
                
                # Проверяем, нет ли уже города на этой позиции
                existing_city = await just_db.find_one(
                    "cities", 
                    session_id=self.session_id, 
                    cell_position=f"{x}.{y}"
                )

                if not existing_city:
                    city = await Citie().create(self.session_id, x, y,
                                          city_names[city_index]
                                        )
                    city_index += 1

                    game_logger.info(f"Created city at position {x}.{y} with branch {city.branch}")

    async def can_select_cell(self, x: int, y: int):
        """ Проверяет, можно ли выбрать клетку с координатами (x, y) для компании.
        """
        if not self.can_select_cells():
            raise ValueError("Текущая стадия сессии не позволяет выбирать клетки.")

        index = x * self.map_size["cols"] + y
        cell_type_key = self.cells[index]
        cell_type = cells.types.get(cell_type_key)

        if not cell_type or not cell_type.pickable or await self.get_company_oncell(x, y):
            return False

        return True

    async def get_company_oncell(self, x: int, y: int):
        """ Возвращает компанию, которая занимает клетку с координатами (x, y)
        """
        company = await just_db.find_one(
            "companies", session_id=self.session_id, cell_position=f"{x}.{y}")
        return company

    async def get_free_cells(self):
        """ Возвращает список свободных клеток (без компаний)
        """
        free_cells = []
        for x in range(self.map_size["rows"]):
            for y in range(self.map_size["cols"]):
                if await self.can_select_cell(x, y):
                    free_cells.append((x, y))
        return free_cells

    async def get_item_price(self, item_id: str) -> int:
        """ Получить цену предмета в данной сессии
        """
        from game.item_price import ItemPrice
        
        item_price_data: dict = await just_db.find_one(
                        "item_price", 
                        id=item_id, 
                        session_id=self.session_id) # type: ignore
        if not item_price_data:
            item_price_obj = await ItemPrice().create(self.session_id, item_id)
            return await item_price_obj.get_effective_price()
        else:
            item_price_obj = ItemPrice(item_id)
            await item_price_obj.load_from_base(item_price_data)
            return await item_price_obj.get_effective_price()

    async def initialize_all_item_prices(self):
        """ Инициализировать цены для всех предметов из конфига
        """
        from game.item_price import ItemPrice
        
        resources = ALL_CONFIGS["resources"]
        for item_id in resources.resources.keys():
            existing_price = await just_db.find_one("item_price", id=item_id, session_id=self.session_id)
            if not existing_price:
                await ItemPrice().create(self.session_id, item_id)

        return True

    async def update_item_price(self, item_id: str, new_price: int):
        """ Обновить цену предмета
        """
        from game.item_price import ItemPrice
        
        item_price_data: dict = await just_db.find_one(
                        "item_price", 
                        id=item_id, 
                        session_id=self.session_id) # type: ignore

        if not item_price_data:
            item_price = await ItemPrice().create(self.session_id, item_id)
        else:
            item_price = ItemPrice(item_id)
            await item_price.load_from_base(item_price_data)
            
        await item_price.add_price(new_price)
        return item_price

    async def get_all_item_prices_dict(self) -> dict[str, int]:
        """ Получить словарь всех цен предметов в сессии
        """
        prices_dict = {}
        for item_price in await self.item_prices:
            prices_dict[item_price.id] = item_price.get_effective_price()
        return prices_dict

    async def delete(self):
        for company in await self.companies: await company.delete()
        for user in await self.users: await user.delete()
        for city in await self.cities: await city.delete()
        for item_price in await self.item_prices: await item_price.delete()

        await just_db.delete('logistics', 
                       session_id=self.session_id)

        await just_db.delete("step_schedule", 
                       session_id=self.session_id)

        await just_db.delete(self.__tablename__, session_id=self.session_id)
        await session_manager.remove_session(self.session_id)

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-session_deleted",
            "data": {
                "session_id": self.session_id
            }
        }))
        return True

    async def leaders(self) -> dict:
        from game.company import Company

        capital_winner = None
        reputation_winner = None
        economic_winner = None

        max_capital = 0
        companies = await self.companies
        for company in companies:
            company: Company
            if company.balance > max_capital:
                max_capital = company.balance
                capital_winner = company

        for company in companies:
            company: Company
            if company.reputation > (reputation_winner.reputation if reputation_winner else 0):
                reputation_winner = company

        for company in companies:
            company: Company
            if company.economic_power > (economic_winner.economic_power if economic_winner else 0):
                economic_winner = company

        return {
            "capital": capital_winner,
            "reputation": reputation_winner,
            "economic": economic_winner
        }

    async def end_game(self):
        leaders = await self.leaders()

        # Объявление победителей
        if leaders["capital"]:
            game_logger.info(f"Capital winner: {leaders['capital'].name} with {leaders['capital'].balance}")
        if leaders["reputation"]:
            game_logger.info(f"Reputation winner: {leaders['reputation'].name} with {leaders['reputation'].reputation}")
        if leaders["economic"]:
            game_logger.info(f"Economic winner: {leaders['economic'].name} with {leaders['economic'].economic_power}")

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-game_ended",
            "data": {
                "session_id": self.session_id,
                "winners": {
                    "capital": leaders["capital"].to_dict() if leaders["capital"] else None,
                    "reputation": leaders["reputation"].to_dict() if leaders["reputation"] else None,
                    "economic": leaders["economic"].to_dict() if leaders["economic"] else None
                }
            }
        }))

    async def get_time_to_next_stage(self) -> int:
        """ Возвращает время в секундах до следующей стадии игры.
            Если стадия не связана со временем, возвращает 0.
        """
        from modules.sheduler import scheduler

        get_schedule: dict = await scheduler.get_scheduled_tasks(
            self.change_turn_schedule_id
            ) # type: ignore
        if get_schedule:
            return int((datetime.fromisoformat(
                get_schedule['execute_at']) - datetime.now()).total_seconds())
        return 0

    async def set_event(self, event_id: str, start_step: int, end_step: int):
        """ Устанавливает событие в сессии и запускает шедулер этапов для его удаления
        
        Args:
            event_id: ID события из конфига
            start_step: этап начала события
            end_step: этап окончания события
        """
        from game.stages import clear_session_event
        
        # Проверяем, что событие существует в конфиге
        if not EVENTS or event_id not in EVENTS.events:
            raise ValueError(f"Событие '{event_id}' не найдено в конфигурации")
            
        self.event_type = event_id
        self.event_start = start_step
        self.event_end = end_step

        await self.save_to_base()

        game_logger.info(f"Event '{event_id}' set for session {self.session_id} from step {start_step} to {end_step}")

        # Запускаем шедулер для удаления события
        await self.create_step_schedule(
            end_step,
            clear_session_event,
            session_id=self.session_id
        )

        return True

    def get_event(self) -> dict:
        """ Выдает данные события в полном объёме для работы кода
        
        Returns:
            dict с полной информацией о событии включая эффекты
        """
        if not self.event_type:
            return {}

        if not EVENTS or self.event_type not in EVENTS.events:
            return {}

        event_config = EVENTS.events[self.event_type]

        return {
            "id": self.event_type,
            "name": event_config.name,
            "description": event_config.description,
            "type": event_config.type.value,
            "category": event_config.category.value,
            "cell_type": event_config.cell_type,
            "predictability": event_config.predictability,
            "effects": event_config.effects.__dict__,
            "start_step": self.event_start,
            "end_step": self.event_end,
            "current_step": self.step,
            "is_active": self.event_start <= self.step <= self.event_end if self.event_start and self.event_end else False,
            "steps_until_start": max(0, self.event_start - self.step) if self.event_start else 0,
            "steps_until_end": max(0, self.event_end - self.step) if self.event_end else 0
        }
    
    def get_event_effects(self) -> dict:
        """ Возвращает только эффекты текущего события для применения в игре
        
        Returns:
            dict с эффектами события или пустой dict если события нет
        """
        event_data = self.get_event()
        if event_data and event_data.get("is_active"):
            return {k: v for k, v in event_data.get("effects", {}).items() if v is not None}
        return {}

    def public_event_data(self) -> dict:
        """ Выдает публичную информацию о событии для сайта

        Показывает событие если:
        - Оно уже идёт
        - Оно начинается на следующем ходе  
        - Оно предсказуемое
        
        Returns:
            dict с публичной информацией о событии
        """
        if not self.event_type or self.event_start is None or self.event_end is None:
            return {}

        if not EVENTS or self.event_type not in EVENTS.events:
            return {}
            
        event_config = EVENTS.events[self.event_type]
        
        # Проверяем, должно ли событие быть публичным
        is_currently_active = self.event_start <= self.step <= self.event_end
        starts_next_turn = self.event_start == self.step + 1
        
        # Предсказуемые события показываем заранее (за 2 хода)
        is_predictable_and_soon = event_config.predictability and (self.event_start - self.step) <= 2
        
        if is_currently_active or starts_next_turn or is_predictable_and_soon:
            return {
                "id": self.event_type,
                "name": event_config.name,
                "description": event_config.description,
                "category": event_config.category.value,
                "start_step": self.event_start,
                "end_step": self.event_end,
                "is_active": is_currently_active,
                "starts_next_turn": starts_next_turn,
                "predictable": event_config.predictability
            }

        return {}

    async def events_generator(self):
        """ Генерирует случайное событие каждые 5 этапов начиная со второго
        
        Проверяет что событие не запущено и:
        - Откладывает предсказуемые события на 2 хода
        - Запускает непредсказуемые события сразу
        """
        # Проверяем, нужно ли генерировать событие
        if self.step < 2:  # Начинаем со второго этапа
            return False
            
        if (self.step - 2) % 5 != 0:  # Каждые 5 этапов
            return False
            
        if self.event_type:  # Уже есть активное событие
            return False

        # Получаем список доступных событий
        available_events = list(EVENTS.events.values())
        if not available_events:
            return False
            
        # Выбираем случайное событие
        event = random.choice(available_events)
        
        # Определяем длительность события
        if event.duration.min is not None and event.duration.max is not None:
            duration = random.randint(event.duration.min, event.duration.max)
        elif event.duration.min is not None:
            duration = event.duration.min
        elif event.duration.max is not None:
            duration = event.duration.max
        else:
            duration = 2  # По умолчанию 2 хода
        
        # Определяем время начала события
        if event.predictability:
            start_step = self.step + 2  # Предсказуемые - через 2 хода
        else:
            start_step = self.step  # Непредсказуемые - сразу
            
        end_step = start_step + duration
        
        # Проверяем, что событие не выйдет за пределы игры
        if end_step >= self.max_steps:
            return False
            
        # Устанавливаем событие
        await self.set_event(event.id, start_step, end_step)
        
        game_logger.info(f"Generated event '{event.id}' for session {self.session_id}")
        
        # Отправляем уведомление
        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-event_generated",
            "data": {
                "session_id": self.session_id,
                "event": self.public_event_data()
            }
        }))
        
        return True

    async def to_dict(self):
        return {
            "id": self.session_id,
            "companies": [company.to_dict() for company in await self.companies],
            "users": [user.to_dict() for user in await self.users],
            "cities": [city.to_dict() for city in await self.cities],
            "item_prices": [item_price.to_dict() for item_price in await self.item_prices],
            "cells": self.cells,
            "map_size": self.map_size,
            "map_pattern": self.map_pattern,
            "cell_counts": self.cell_counts,
            "stage": self.stage,
            "step": self.step,
            "max_steps": self.max_steps,
            "time_to_next_stage": await self.get_time_to_next_stage(),

            "event": {
                "type": self.event_type,
                "start": self.event_start,
                "end": self.event_end
            }
        }


class SessionsManager():
    def __init__(self):
        self.sessions = {}

    async def create_session(self, session_id: str = ""):
        session = await Session(session_id=session_id).start()
        if session.session_id in self.sessions:
            raise ValueError("Сессия с этим ID уже существует в памяти.")
        self.sessions[session.session_id] = session
        return session

    async def get_session(self, session_id) -> Session | None:
        session = self.sessions.get(session_id)
        if session: return await session.reupdate()
        return None

    async def remove_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]
        await just_db.delete("sessions", session_id=session_id)

    async def load_from_base(self):
        ss: list[dict] = await just_db.find("sessions") # type: ignore
        for s in ss:
            session = Session(s['session_id'])
            await session.load_from_base(s)
            self.sessions[session.session_id] = session

session_manager = SessionsManager()
