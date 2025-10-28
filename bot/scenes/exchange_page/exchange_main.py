from utils.oneuser_page import OneUserPage
from modules.ws_client import get_exchanges
from global_modules import Resources, ALL_CONFIGS
from oms.utils import callback_generator


RESOURCES: Resources = ALL_CONFIGS["resources"]

class ExchangeMain(OneUserPage):
    __for_blocked_pages__ = ["exchange-sellect-confirm", "exchange-create-page"]
    __page_name__ = "exchange-main-page"
    
    
    async def data_preparate(self):
        await self.scene.update_key("exchange-main-page", "page_number", 0)
        await self.scene.update_key("exchange-main-page", "state", "all") #all, our
    
    
    async def buttons_worker(self):
        data = self.scene.get_data("scene")
        session = data.get("session")
        company = data.get("company_id")
        state = self.scene.get_key("exchange-main-page", "state")
        self.row_width = 3
        buttons = []
        all_ex_page_container = []
        our_ex_page_container = []
        cur_page = self.scene.get_key("exchange-main-page", "page_number")
        exchanges = await get_exchanges(session_id=session)
        if len(exchanges) != 0:
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
                if ex["company_id"] != company:
                    all_ex_page_container.append({
                        "text": text,
                        "callback_data": callback,
                        "next_line": True
                    })
                elif ex["company_id"] == company:
                    our_ex_page_container.append({
                        "text": text,
                        "callback_data": callback,
                        "next_line": True
                    })
        
        if len(all_ex_page_container) != 0 and state == "all":
            buttons.append(*all_ex_page_container)
        elif len(our_ex_page_container) != 0 and state == "our":
            buttons.append(*our_ex_page_container)
        
        if len(buttons) != 0:
            buttons.append({"text": "Назад",
                            "callback_data": callback_generator(self.scene.__scene_name__, "back_page")})
        
        return buttons