import asyncio
from modules.websocket_manager import websocket_manager
from global_modules.db.baseclass import BaseClass
from modules.json_database import just_db
from game.session import session_manager

class Company(BaseClass):

    __tablename__ = "companies"
    __unique_id__ = "id"
    __db_object__ = just_db

    def __init__(self, _id: int = 0):
        self.id: int = _id
        self.name: str = ""

        self.reputation: int = 0
        self.balance: int = 0

        self.in_prison: bool = False

        self.credits: list = []
        self.deposits: list = []

        self.improvements: dict = {}
        self.warehouses: dict = {}

        self.session_id: str = ""
        self.cell_position: str = "" # 3.1

    def create(self, name: str, session_id: str):
        self.name = name
        self.id = just_db.max_id_in_table(
            self.__tablename__) + 1

        with_this_name = just_db.find_one(
            self.__tablename__, name=name)
        if with_this_name:
            raise ValueError(f"Company with name '{name}' already exists.")

        session = session_manager.get_session(session_id)
        if not session or not session.can_add_company():
            raise ValueError("Invalid or inactive session for adding a company.")
        self.session_id = session_id

        self.name = name

        self.save_to_base()
        self.reupdate()

        return self

    def can_user_enter(self):
        session = session_manager.get_session(self.session_id)
        if not session or session.stage != "FreeUserConnect":
            return False
        return True

    @property
    def users(self):
        from game.user import User

        return [user for user in just_db.find(
            "users", to_class=User, company_id=self.id)]

    def set_position(self, x: int, y: int):
        if isinstance(x, int) is False or isinstance(y, int) is False:
            raise ValueError("Coordinates must be integers.")

        session = session_manager.get_session(self.session_id)
        if not session or not session.can_select_cell(x, y):
            return False

        self.cell_position = f"{x}.{y}"
        self.save_to_base()
        self.reupdate()
        return True

    def get_position(self):
        if not self.cell_position:
            return None
        try:
            x, y = map(int, self.cell_position.split('.'))
            return (x, y)
        except Exception:
            return None

    def delete(self):
        just_db.delete(self.__tablename__, **{self.__unique_id__: self.id})
        
        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-company_deleted",
            "data": {
                "company_id": self.id
            }
        }))
        return True