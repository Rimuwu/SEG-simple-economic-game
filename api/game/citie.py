from global_modules.db.baseclass import BaseClass
from modules.json_database import just_db
from game.session import session_manager

class Cities(BaseClass):
    
    __tablename__ = "cities"
    __unique_id__ = "id"
    __db_object__ = just_db

    def __init__(self, _id: int = 0):
        self._id: int = _id
        self.location: str = ""

        self.products: dict = {}

