from utils.oneuser_page import OneUserPage
from modules.ws_client import get_exchanges
from global_modules import Resources, ALL_CONFIGS
from oms.utils import callback_generator


RESOURCES: Resources = ALL_CONFIGS["resources"]

class ExchangeMain(OneUserPage):
    __for_blocked_pages__ = ["exchange-sellect-confirm", "exchange-create-page"]
    __page_name__ = "exchange-main-page"
    
    
    async def buttons_worker(self):
        data = self.scene.get_data("scene")
        session = data.get("session")
        self.row_width = 2
        buttons = []
        
        exchanges = await get_exchanges(session_id=session)
        for ex in exchanges:
            text = None
            callback = None
            sell_res = RESOURCES.get_resource(ex["sell_resource"])
            if ex["offer_type"] == "barter":
                bart_res = RESOURCES.get_resource(ex["barter_resource"])
                text = f"{ex["sell_amount_per_trade"]}x {sell_res.emoji} {sell_res.label} ⇄ {ex["barter_amount_per_trade"]}x {bart_res.emoji} {bart_res.label}"
                callback = callback_generator(
                    self.scene.__scene_name__,
                    "select_exchange",
                    ex["id"]
                )
            elif ex["offer_type"] == "money":
                text = f"{ex['sell_amount_per_trade']}x {sell_res.emoji} {sell_res.label} ⇄ {ex['sell_amount_per_trade']}💰"
                callback = callback_generator(
                    self.scene.__scene_name__,
                    "select_exchange",
                    ex["id"]
                )
            
            
        
        return buttons