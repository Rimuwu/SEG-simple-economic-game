from scenes.start_page import Start
from scenes.name_page import UserName
from scenes.company_create_page import CompanyCreate
from scenes.company_join_page import CompanyJoin
from scenes.main_page import MainPage
from scenes.wait_game_page import WaitStart
from scenes.select_cell_page import SelectCell
from scenes.about_info_page import AboutInfo
from scenes.factory_menu_page import FactoryMenu
from scenes.factory_rekit_groups import FactoryRekitGroups
from scenes.factory_rekit_count import FactoryRekitCount
from scenes.factory_rekit_resource import FactoryRekitResource
from scenes.factory_rekit_produce import FactoryRekitProduce
from oms import Scene
from modules.db import db


class GameManager(Scene):

    __scene_name__ = 'scene-manager'
    __pages__ = [
        Start,
        UserName,
        CompanyCreate,
        CompanyJoin,
        MainPage,
        WaitStart,
        SelectCell,
        AboutInfo,
        FactoryMenu,
        FactoryRekitGroups,
        FactoryRekitCount,
        FactoryRekitResource,
        FactoryRekitProduce
    ]
    
    @staticmethod
    async def insert_to_db(user_id: int, data: dict):
        db.insert('scenes', data)

    @staticmethod
    async def load_from_db(user_id: int) -> dict:
        data = db.find_one('scenes', user_id=user_id) or {}
        return data

    @staticmethod
    async def update_to_db(user_id: int, data: dict):
        db.update('scenes', {'user_id': user_id}, data)

    @staticmethod
    async def delete_from_db(user_id: int):
        db.delete('scenes', user_id=user_id)
    
    # Функция для вставки сцены в БД
    # В функцию передаёт user_id: int, data: dict
    __insert_function__ = insert_to_db

    # Функция для загрузки сцены из БД
    # В функцию передаёт user_id: int, вернуть должна dict
    __load_function__ = load_from_db

    # Функция для обновления сцены в БД
    # В функцию передаёт user_id: int, data: dict
    __update_function__ = update_to_db
    
    # Функция для удаления сцены из БД
    # В функцию передаёт user_id: int
    __delete_function__ = delete_from_db