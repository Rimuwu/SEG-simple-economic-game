import random
from modules.json_database import just_db
from modules.generate import generate_code
from enum import Enum
from modules.baseclass import BaseClass
import asyncio
import asyncio

class SessionStages(Enum):
    WaitWebConnect = "WaitWebConnect" # Ждём пока появится сайт для работы
    FreeUserConnect = "FreeUserConnect" # Подключаем пользователей
    CellSelect = "CellSelect" # Выбираем клетки
    Game = "Game" # Ход
    ChangeTurn = "ChangeTurn" # Смена хода
    End = "End" # Конец игры


class Session(BaseClass):

    def start(self):
        self.session_id = generate_code(32, use_letters=True, use_numbers=True, use_uppercase=True)
        self.stage = SessionStages.WaitWebConnect.value
        self.companies_id = []
        self.users_id = []

        self.save_to_base()
        self.reupdate()

        return self


class SessionsManager():
    def __init__(self):
        self.sessions = {}

    def create_session(self):
        session = Session().start()
        self.sessions[session.session_id] = session
        return session.session_id

    def get_session(self, session_id):
        return self.sessions.get(session_id)

    def remove_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]

session_manager = SessionsManager()