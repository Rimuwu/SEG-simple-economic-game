from modules.baseclass import BaseClass
from modules.json_database import just_db
from game.session import session_manager

class Cities(BaseClass):
    
    __tablename__ = "cities"
    __unique_id__ = "id"

    def __init__(self, _id: int = 0):
        self._id: int = _id
        self.location: str = ""

        self.products: dict = {}

