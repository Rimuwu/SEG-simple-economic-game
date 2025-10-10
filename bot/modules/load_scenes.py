from typing import Type
from oms import scene_manager
from oms.manager import SceneManager
from modules.db import db
from bot_instance import bot

def load_scenes_from_db(manager: SceneManager):

    results = db.find('scenes')
    for result in results:
        manager.load_scene_from_db(
            result['user_id'],
            result['scene_path'],
            result['page'],
            result['message_id'],
            result['data'],
            bot,
            False
        )