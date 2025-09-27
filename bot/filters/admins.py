from aiogram.filters import BaseFilter
from aiogram.types import Message
import os

# Список ID администраторов
ADMIN_IDS = [admin_id for admin_id in os.getenv("ADMIN_IDS", "").strip().split(",")]

class AdminFilter(BaseFilter):
    def __init__(self, status: bool = True):
        self.status: bool = status
    async def __call__(self, message: Message) -> bool:
        is_admin = str(message.from_user.id) in ADMIN_IDS
        return is_admin if self.status else not is_admin