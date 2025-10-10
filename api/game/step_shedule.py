import asyncio
from global_modules.models.cells import Cells
from global_modules.db.baseclass import BaseClass
from modules.json_database import just_db
from game.session import session_manager
from global_modules.load_config import ALL_CONFIGS, Resources, Improvements, Settings, Capital, Reputation
from modules.function_way import *

RESOURCES: Resources = ALL_CONFIGS["resources"]
CELLS: Cells = ALL_CONFIGS['cells']
IMPROVEMENTS: Improvements = ALL_CONFIGS['improvements']
SETTINGS: Settings = ALL_CONFIGS['settings']
CAPITAL: Capital = ALL_CONFIGS['capital']
REPUTATION: Reputation = ALL_CONFIGS['reputation']

class StepSchedule(BaseClass):

    __tablename__ = "step_schedule"
    __unique_id__ = "id"
    __db_object__ = just_db

    def __init__(self, _id: int = 0):
        self.id: int = _id

        self.session_id: str = ""
        self.in_step: int = 0
        self.functions: list = [
            ]  # Список функций для выполнения в этом шаге

    def create(self, session_id: str, in_step: int) -> 'StepSchedule':
        if schedule := just_db.find_one(
            self.__tablename__, 
            session_id=session_id, in_step=in_step,
            to_class=StepSchedule
            ):
            return schedule # type: ignore

        self.session_id = session_id
        self.in_step = in_step
        self.id = just_db.max_id_in_table(self.__tablename__) + 1

        self.save_to_base()
        self.reupdate()
        return self

    def add_function(self, function, **kwargs):
        """ Добавляет функцию в расписание шага
        """
        if not function or not callable(function):
            raise ValueError("Function must be a callable.")

        if not self.id:
            raise ValueError("Schedule must be saved before adding functions.")

        session = session_manager.get_session(self.session_id)
        if not session:
            just_db.delete(self.__tablename__, id=self.id)
            raise ValueError("Invalid session for adding function.")

        if not session.step <= self.in_step:
            raise ValueError("Invalid step for adding function.")

        self.functions.append({
            "function": func_to_str(function),
            "args": kwargs
        })
        self.save_to_base()
        self.reupdate()
        return True

    async def execute(self):
        """ Выполняет все функции в расписании шага
        """
        session = session_manager.get_session(self.session_id)

        if not session:
            just_db.delete(self.__tablename__, id=self.id)
            print(f'Session {self.session_id} not found. Deleting schedule {self.id}.')
            return False

        if session.step != self.in_step:
            return False

        for func_entry in self.functions:
            func_name = func_entry.get("function")
            args = func_entry.get("args", {})

            if not func_name:
                print("Function name is missing.")
                continue

            # Импортируем функцию по имени
            function = str_to_func(func_name)

            if not callable(function):
                print(f"{func_name} is not callable.")
                continue

            # Выполняем функцию
            try:
                if asyncio.iscoroutinefunction(function):
                    await function(**args)
                else:
                    function(**args)
            except Exception as e:
                print(f"Error executing function {func_name}: {e}")

        just_db.delete(self.__tablename__, id=self.id)
        return True