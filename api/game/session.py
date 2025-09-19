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
    
    __tablename__ = "sessions"
    __unique_id__ = "session_id"

    def __init__(self, session_id: str = ""): 
        self.session_id = session_id
        self.companies_id = []
        self.cells: dict = {}

    def start(self):
        if not self.session_id:
            self.session_id = generate_code(32, use_letters=True, use_numbers=True, use_uppercase=True)
        self.stage = SessionStages.WaitWebConnect.value

        self.save_to_base()
        self.reupdate()

        return self

    def update_stage(self, new_stage: SessionStages):
        if not isinstance(new_stage, SessionStages):
            raise ValueError("new_stage must be an instance of SessionStages Enum")

        if new_stage == SessionStages.CellSelect:
            # if len(self.companies_id) < 2:
            #     raise ValueError("At least two companies are required to move to CellSelect stage.")
            self.on_cellselect_stage()

        self.stage = new_stage.value
        self.save_to_base()
        self.reupdate()
        return self

    def on_cellselect_stage(self):
        for company_id in self.companies_id:
            just_db.update("companies", 
                           {"company_id": company_id},
                           {'users_enter': False}
                           )

    def add_company(self, company_id):
        if self.stage is not SessionStages.FreeUserConnect.value:
            raise ValueError("Cannot add company at this stage.")

        if company_id not in self.companies_id:
            self.companies_id.append(company_id)
            self.save_to_base()
            self.reupdate()
            return True
        return False


class SessionsManager():
    def __init__(self):
        self.sessions = {}

    def create_session(self):
        session = Session().start()
        self.sessions[session.session_id] = session
        return session

    def get_session(self, session_id):
        return self.sessions.get(session_id)

    def remove_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]

session_manager = SessionsManager()