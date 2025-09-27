from scenes.start_page import Start
from scenes.name_page import UserName
from oms_dir import Scene
from modules.db import db
from oms_dir.models.scene import scenes_loader

class GameManger(Scene):
    
    __scene_name__ = 'scene-manager'
    __pages__ = [
        Start,
        UserName
    ]

    async def save_to_db(self):

        exist = db.find_one('scenes',
                            user_id=self.user_id)
        if not exist:
            db.insert('scenes',
                      {
                        'page': self.page,
                        'scene': self.__scene_name__,
                        'message_id': self.message_id,
                        'user_id': self.user_id,
                        'data': self.data
                      }
                      )
        else:
            db.update('scenes',
                {'user_id': self.user_id},
                {
                    'page': self.page,
                    'scene': self.__scene_name__,
                    'message_id': self.message_id,
                    'user_id': self.user_id,
                    'data': self.data
                }
            )

    async def load_from_db(self):

        data = db.find_one('scenes',
                                user_id=self.user_id)
        if not data:
            raise ValueError('Нет данных в базе')

        self.page = data.get('page', self.start_page)
        self.message_id = data.get('message_id', 0)
        self.scene = scenes_loader.get_scene(
            self.__scene_name__) # type: ignore
        self.user_id = data.get('user_id')
        self.data = data.get('data')