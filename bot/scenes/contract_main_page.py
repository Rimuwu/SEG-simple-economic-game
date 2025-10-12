from oms import Page
from aiogram.types import Message, CallbackQuery
from modules.ws_client import *
from oms.utils import callback_generator


class ContractMainPage(Page):
    __page_name__ = "contract-main-page"
    
    async def content_worker(self):
        data = self.scene.get_data('scene')
        company_id = data.get('company_id')
        session_id = data.get('session')
        
        return "Test"