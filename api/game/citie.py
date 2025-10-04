
import asyncio
from global_modules.models.cells import Cells
from global_modules.db.baseclass import BaseClass
from global_modules.models.resources import Production, Resource
from modules.json_database import just_db
from global_modules.load_config import ALL_CONFIGS, Resources, Improvements, Settings, Capital, Reputation
from modules.function_way import *
from modules.websocket_manager import websocket_manager

RESOURCES: Resources = ALL_CONFIGS["resources"]
CELLS: Cells = ALL_CONFIGS['cells']
IMPROVEMENTS: Improvements = ALL_CONFIGS['improvements']
SETTINGS: Settings = ALL_CONFIGS['settings']
CAPITAL: Capital = ALL_CONFIGS['capital']
REPUTATION: Reputation = ALL_CONFIGS['reputation']

class Factory(BaseClass):

    __tablename__ = "cities"
    __unique_id__ = "id"
    __db_object__ = just_db

    def __init__(self, id: int = 0):
        self.id: int = id

    def create(self):
        """ Создание новой фабрики
        """

        self.save_to_base()
        self.reupdate()

        asyncio.create_task(websocket_manager.broadcast({
           
        }))

        return self

    def on_new_game_stage(self):
        pass

    def to_dict(self) -> dict:
        return {
       
        }

    def delete(self):
        """ Удаление города
        """


        return True