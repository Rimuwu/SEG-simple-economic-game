from oms import Page
from aiogram.types import Message
from modules.ws_client import get_company

class AboutInfo(Page):
    
    __page_name__ = "about-info-menu"
    
    async def content_worker(self):
        scene_data = self.scene.get_data('scene')

        company_id = scene_data.get('company_id')
        self.content = await get_company(id=company_id)