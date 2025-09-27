from typing import TYPE_CHECKING, Optional, Type

class SceneManager:
    _instances = {}

    @classmethod
    def get_scene(cls, user_id: int) -> Optional['Scene']:
        if not cls.has_scene(user_id): return None
        return cls._instances[user_id]

    @classmethod
    def create_scene(cls, user_id: int, scene_class: Type['Scene']) -> 'Scene':
        if user_id in cls._instances:
            raise ValueError(f"Сцена для пользователя {user_id} уже существует")
        cls._instances[user_id] = scene_class(user_id)
        return cls._instances[user_id]

    @classmethod
    def remove_scene(cls, user_id: int):
        if user_id in cls._instances:
            del cls._instances[user_id]

    @classmethod
    def has_scene(cls, user_id: int) -> bool:
        return user_id in cls._instances

manager = SceneManager()