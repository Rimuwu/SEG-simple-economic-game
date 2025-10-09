import asyncio
from datetime import datetime, timedelta
import random
from game.stages import stage_game_updater
from global_modules.models.cells import CellType, Cells
from modules.json_database import just_db
from modules.generate import generate_code
from enum import Enum
from global_modules.db.baseclass import BaseClass
from global_modules.load_config import ALL_CONFIGS, Settings
from collections import Counter
from global_modules.logs import main_logger
from modules.websocket_manager import websocket_manager
from modules.sheduler import scheduler

settings: Settings = ALL_CONFIGS['settings']
cells: Cells = ALL_CONFIGS['cells']
cells_types = cells.types

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

    def start(self):
        if not self.session_id:
            self.session_id = generate_code(32, use_letters=True, use_numbers=True, use_uppercase=True)
        self.stage = SessionStages.FreeUserConnect.value

        self.save_to_base()
        self.reupdate()

        return self

    def update_stage(self, new_stage: SessionStages, 
                     whitout_shedule: bool = False):
        if not isinstance(new_stage, SessionStages):
            raise ValueError("new_stage must be an instance of SessionStages Enum")

        if self.stage == SessionStages.End.value:
            raise ValueError("Cannot change stage from End stage.")

        elif self.step >= self.max_steps:
            new_stage = SessionStages.End

        elif new_stage == SessionStages.CellSelect:
            self.generate_cells()

            if not whitout_shedule:
                scheduler.schedule_task(
                    stage_game_updater, 
                    datetime.now() + timedelta(
                        seconds=settings.turn_cell_time_minutes * 60
                        ),
                    kwargs={"session_id": self.session_id}
                )

        elif new_stage == SessionStages.Game:
            self.execute_step_schedule()

            for company in self.companies:
                company.on_new_game_stage(self.step + 1)

            self.step += 1

        elif new_stage == SessionStages.End:
            self.end_game()

        old_stage = self.stage
        self.stage = new_stage.value

        self.save_to_base()
        self.reupdate()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-update_session_stage",
            "data": {
                "session_id": self.session_id,
                "new_stage": self.stage,
                "old_stage": old_stage
            }
        }))

        return self

    def execute_step_schedule(self):
        from game.step_shedule import StepSchedule

        schedules: list[StepSchedule] = just_db.find(
            "step_schedule", session_id=self.session_id, in_step=self.step,
            to_class=StepSchedule
        ) # type: ignore

        for schedule in schedules:
            asyncio.create_task(schedule.execute())
        return True

    def create_step_schedule(self, in_step: int, 
                             function, **kwargs):
        from game.step_shedule import StepSchedule

        if in_step < 0:
            raise ValueError("in_step must be a non-negative integer.")

        schedule = StepSchedule().create(
            session_id=self.session_id, in_step=in_step)
        schedule.add_function(function, **kwargs)

        return schedule

    def can_user_connect(self):
        return self.stage == SessionStages.FreeUserConnect.value

    def can_add_company(self):
        return self.stage == SessionStages.FreeUserConnect.value

    def can_select_cells(self):
        return self.stage == SessionStages.CellSelect.value

    @property
    def companies(self) -> list['Company']:
        from game.company import Company

        return [comp for comp in just_db.find(
            "companies", to_class=Company, session_id=self.session_id)
                        ]

    @property
    def users(self) -> list['User']:
        from game.user import User

        return [us for us in just_db.find(
            "users", to_class=User, session_id=self.session_id)
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

    def generate_cells(self):
        if self.cells:
            raise ValueError("Cells have already been generated for this session.")

        # Ограничения на размер карты
        for r in range(self.map_size["rows"]):
            for c in range(self.map_size["cols"]):
                self.cells.append('null')

        # Установка объектов со стандартной позицией
        for cell_key, cell_info in cells.types.items():
            cell_info: CellType

            for location in cell_info.locations:
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
        main_logger.info(f"Cell counts: {self.cell_counts}")

        self.save_to_base()
        return self.cells

    def can_select_cell(self, x: int, y: int):
        """ Проверяет, можно ли выбрать клетку с координатами (x, y) для компании.
        """
        if not self.can_select_cells():
            raise ValueError("Current session stage does not allow cell selection.")

        index = x * self.map_size["cols"] + y
        cell_type_key = self.cells[index]
        cell_type = cells.types.get(cell_type_key)

        if not cell_type or not cell_type.pickable or self.get_company_oncell(x, y):
            return False

        return True

    def get_company_oncell(self, x: int, y: int):
        """ Возвращает компанию, которая занимает клетку с координатами (x, y)
        """
        company = just_db.find_one(
            "companies", session_id=self.session_id, cell_position=f"{x}.{y}")
        return company

    def get_free_cells(self):
        """ Возвращает список свободных клеток (без компаний)
        """
        free_cells = []
        for x in range(self.map_size["rows"]):
            for y in range(self.map_size["cols"]):
                if self.can_select_cell(x, y):
                    free_cells.append((x, y))
        return free_cells

    def delete(self):
        for company in self.companies: company.delete()
        for user in self.users: user.delete()

        just_db.delete(self.__tablename__, session_id=self.session_id)
        session_manager.remove_session(self.session_id)

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-session_deleted",
            "data": {
                "session_id": self.session_id
            }
        }))
        return True

    def end_game(self):
        from game.company import Company
        
        capital_winner = None
        reputation_winner = None
        economic_winner = None

        max_capital = 0
        for company in self.companies:
            company: Company
            if company.balance > max_capital:
                max_capital = company.balance
                capital_winner = company

        for company in self.companies:
            company: Company
            if company.reputation > (reputation_winner.reputation if reputation_winner else 0):
                reputation_winner = company

        # for company in self.companies:
        #     company: Company
        #     if company.economic_power > (economic_winner.economic_power if economic_winner else 0):
        #         economic_winner = company

        # Объявление победителей
        if capital_winner:
            main_logger.info(f"Capital winner: {capital_winner.name} with {capital_winner.balance}")
        if reputation_winner:
            main_logger.info(f"Reputation winner: {reputation_winner.name} with {reputation_winner.reputation}")
        if economic_winner:
            main_logger.info(f"Economic winner: {economic_winner.name} with {economic_winner.economic_power}")

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-game_ended",
            "data": {
                "session_id": self.session_id,
                "winners": {
                    "capital": capital_winner,
                    "reputation": reputation_winner,
                    "economic": economic_winner
                }
            }
        }))

    def to_dict(self):
        return {
            "id": self.session_id,
            "companies": [company.to_dict() for company in self.companies],
            "users": [user.to_dict() for user in self.users],
            "cells": self.cells,
            "map_size": self.map_size,
            "map_pattern": self.map_pattern,
            "cell_counts": self.cell_counts,
            "stage": self.stage,
            "step": self.step,
            "max_steps": self.max_steps
        }


class SessionsManager():
    def __init__(self):
        self.sessions = {}

    def create_session(self, session_id: str = ""):
        session = Session(session_id=session_id).start()
        if session.session_id in self.sessions:
            raise ValueError("Session with this ID already exists in memory.")
        self.sessions[session.session_id] = session
        return session

    def get_session(self, session_id) -> Session | None:
        session = self.sessions.get(session_id)
        if session: return session.reupdate()
        return None

    def remove_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def load_from_base(self):
        ss = just_db.find("sessions")
        for s in ss:
            session = Session(s['session_id'])
            session.load_from_base(s)
            self.sessions[session.session_id] = session

session_manager = SessionsManager()