from aiogram.filters import BaseFilter
from aiogram.types import Message
from ..manager import scene_manager


class InScene(BaseFilter):
    def __init__(self, status: bool = True):
        self.status: bool = status

    async def __call__(self, message: Message) -> bool:
        is_in_scene = scene_manager.has_scene(message.from_user.id)
        return is_in_scene if self.status else not is_in_scene