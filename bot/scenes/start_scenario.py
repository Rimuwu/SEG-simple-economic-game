from scenes.game_info_page import GameInfo
from oms import Scene
from modules.db import db


class StartManager(Scene):
    __scene_name__ = 'start-scene-manager'
    __pages__ = [
        GameInfo
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