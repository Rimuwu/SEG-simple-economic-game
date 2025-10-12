from oms import Page
from aiogram.types import Message, CallbackQuery
from modules.ws_client import *
from oms.utils import callback_generator


class LogisticsMenu(Page):
    
    __page_name__ = "logistics-menu"
    
    async def data_preparate(self):
        self.scene.update_key("logistics-menu", "stage", "main") #main, me, to, get
    
    async def content_worker(self):
        return "Text"
    
    async def buttons_worker(self):
        buttons = []
        return buttons