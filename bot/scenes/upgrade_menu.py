from oms import Page
from aiogram.types import Message, CallbackQuery
from modules.ws_client import *
from oms.utils import callback_generator


class UpgradeMenu(Page):
    __page_name__ = "upgrade-menu"
    
    