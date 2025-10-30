from utils.oneuser_page import OneUserPage
from modules.ws_client import get_exchanges
from global_modules import Resources, ALL_CONFIGS
from oms.utils import callback_generator
from aiogram.types import CallbackQuery
import json


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
            buttons.extend(all_ex_page_container[cur_page*5:cur_page*5+5])
        elif len(our_ex_page_container) != 0 and state == "our":
            buttons.extend(our_ex_page_container[cur_page*5:cur_page*5+5])

        if len(buttons) != 0:
            buttons.append({"text": "Назад",
                            "callback_data": callback_generator(self.scene.__scene_name__, "back_page"),
                            })
            list_butt = len(all_ex_page_container) if state == "all" else len(our_ex_page_container)
            buttons.append({"text": f"{cur_page}/{(list_butt//5 +1) if list_butt/5 > list_butt//5 else list_butt//5}",
                            "callback_data": callback_generator(self.scene.__scene_name__, "nope"),
                            })
            await self.scene.update_key("exchange-main-page", "max_page", (list_butt//5 +1) if list_butt/5 > list_butt//5 else list_butt//5)
            buttons.append({"text": "Вперёд",
                            "callback_data": callback_generator(self.scene.__scene_name__, "next_page"),
                            })
            buttons.append({"text": f"{'Все предложения' if state == 'all' else 'Ваши предложения'}",
                            "callback_data": callback_generator(self.scene.__scene_name__, "change_state"),
                            })
        
        return buttons
    
    @OneUserPage.on_callback("select_exchange")
    async def select_exchange(self, call: CallbackQuery, args: list):
        await self.scene.update_key("exchange-select-confirm-page", "selected_exchange", args[1])
        await self.scene.update_page("exchange-select-confirm-page")
    @OneUserPage.on_callback("change_state")
    async def change_state(self, call: CallbackQuery, args: list):
        state = self.scene.get_key("exchange-main-page", "state")
        if state == "all":
            await self.scene.update_key("exchange-main-page", "state", "our")
        else:
            await self.scene.update_key("exchange-main-page", "state", "all")
        await self.scene.update_key("exchange-main-page", "page_number", 0)
        await self.scene.update_message()
    @OneUserPage.on_callback("next_page")
    async def next_page(self, call: CallbackQuery, args: list):
        cur_page = await self.scene.get_key("exchange-main-page", "page_number")
        max_page = await self.scene.get_key("exchange-main-page", "max_page")
        if cur_page + 1 <= max_page:
            await self.scene.update_key("exchange-main-page", "page_number", cur_page + 1)
        else:
            await self.scene.update_key("exchange-main-page", "page_number", 0)
        await self.scene.update_message()
    @OneUserPage.on_callback("back_page")
    async def back_page(self, call: CallbackQuery, args: list):
        cur_page = await self.scene.get_key("exchange-main-page", "page_number")
        max_page = await self.scene.get_key("exchange-main-page", "max_page")
        if cur_page - 1 >= 0:
            await self.scene.update_key("exchange-main-page", "page_number", cur_page - 1)
        else:
            await self.scene.update_key("exchange-main-page", "page_number", max_page)
        await self.scene.update_message()