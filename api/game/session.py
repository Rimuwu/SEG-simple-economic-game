import random
from modules.json_database import just_db
from modules.generate import generate_code
from enum import Enum
from modules.baseclass import BaseClass

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

        self.save_data()