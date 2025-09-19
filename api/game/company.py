from modules.baseclass import BaseClass
from modules.json_database import just_db
from game.session import session_manager

class Company(BaseClass):

    __tablename__ = "companies"
    __unique_id__ = "company_id"

    def __init__(self):
        self.company_id: int = 0
        self.name: str = ""
        
        self.reputation: int = 0
        self.balance: int = 0
        
        self.in_prison: bool = False
        
        self.credits: list = []
        self.deposits: list = []

        self.improvements: dict = {}
        self.warehouses: dict = {}
        self.users_id: list = []

        self.users_enter: bool = True

    def create(self, name: str = ""):
        self.name = name
        self.company_id = just_db.max_id_in_table(
            self.__tablename__) + 1

        with_this_name = just_db.find_one(
            self.__tablename__, name=name)
        if with_this_name:
            raise ValueError(f"Company with name '{name}' already exists.")

        self.name = name

        self.save_to_base()
        self.reupdate()

        return self

    def add_user(self, user_id):

        if not self.users_enter:
            raise ValueError("Adding users is disabled for this company.")

        if user_id not in self.users_id:
            self.users_id.append(user_id)
            self.save_to_base()
            self.reupdate()
            return True
        return False
