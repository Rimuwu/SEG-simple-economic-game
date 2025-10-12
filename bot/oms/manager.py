import asyncio
from typing import Optional, Type, TYPE_CHECKING
from aiogram import Bot
from .utils import str_to_func

if TYPE_CHECKING:
    from oms import Scene

class SceneManager:
    _instances = {}

    @classmethod
    def get_scene(cls, user_id: int) -> Optional['Scene']:
        if not cls.has_scene(user_id): return None
        return cls._instances[user_id]

    @classmethod
    def create_scene(cls, user_id: int, 
                     scene_class: Type['Scene'],
                     bot_instance: 'Bot'
                     ) -> 'Scene':
        if user_id in cls._instances:
            raise ValueError(f"Сцена для пользователя {user_id} уже существует")
        cls._instances[user_id] = scene_class(user_id, bot_instance)
        return cls._instances[user_id]

    @classmethod
    def remove_scene(cls, user_id: int):
        if user_id in cls._instances:
            del cls._instances[user_id]

    @classmethod
    def has_scene(cls, user_id: int) -> bool:
        return user_id in cls._instances

    @classmethod
    def load_scene_from_db(cls, 
                            user_id: int,
                            scene_path: str,
                            page: str,
                            message_id: int,
                            data: dict,
                            bot_instance: 'Bot',
                            update_message: bool = False
                            ):
        """ Загрузка сцены из БД по параметрам.
        """

        if user_id in cls._instances:
            raise ValueError(f"Сцена для пользователя {user_id} уже существует")

        scene_class: Type[Scene] = str_to_func(scene_path)

        cls._instances[user_id] = scene_class(
            user_id=user_id,
            bot_instance=bot_instance
        )
        
        # ВАЖНО: создаём глубокую копию data для каждого пользователя!
        import copy
        cls._instances[user_id].__dict__.update({
            'page': page,
            'message_id': message_id,
            'data': copy.deepcopy(data)
        })

        if update_message:
            asyncio.create_task(
                cls._instances[user_id].update_message()
            )

        return cls._instances[user_id]

    @classmethod
    def get_for_params(cls, 
                       scene: Optional[str], 
                       page: Optional[str]
                       ) -> list['Scene']:
        """ Получение всех сцен, соответствующих параметрам.
        """
        results = []
        for user_id, instance in cls._instances.items():
            instance: 'Scene'

            page_name: str = instance.current_page.__page_name__

            if scene and page:
                if instance.__scene_name__ == scene and page_name == page:
                    results.append(instance)
            elif scene:
                if instance.__scene_name__ == scene:
                    results.append(instance)
            elif page:
                if page_name == page:
                    results.append(instance)

        return results


scene_manager = SceneManager()