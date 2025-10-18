from .oneuser_page import OneUserPage
from global_modules.load_config import ALL_CONFIGS, Resources
from oms.utils import callback_generator


RESOURCES: Resources = ALL_CONFIGS["resources"]

class ItemFilter(OneUserPage):
    
    async def content_worker(self):
        return ""
    
    
    async def buttons_worker(self):
        self.row_width = 3
        buttons = []
        k = 0
        for key, res in RESOURCES.get_raw_resources().items():
            if k == 1:
                buttons.append({
                    "text": f"{res.emoji} {res.label}",
                    "callback_data": callback_generator(
                    self.scene.__scene_name__,
                    "item_select",
                    key
                    ),
                    "next_line": True
                    })
                k = 0
            else:
                k += 1
                buttons.append({
                    "text": f"{res.emoji} {res.label}",
                    "callback_data": callback_generator(
                    self.scene.__scene_name__,
                    "item_select",
                    key
                    )})
        
        buttons.append({
            "text": "⬅️ Назад",
            "callback_data": callback_generator(
                self.scene.__scene_name__,
                "back_page"
            ),
            "ignore_row": True
            })
        buttons.append({
            "text": "Вперёд ➡️",
            "callback_data": callback_generator(
                self.scene.__scene_name__,
                "next_page"
            )})
        return buttons