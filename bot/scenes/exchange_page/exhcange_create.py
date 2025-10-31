from utils.filter_item import ItemFilter
from oms.utils import callback_generator
from modules.ws_client import create_exchange_offer
import json
from global_modules.load_config import ALL_CONFIGS, Resources

RESOURCES: Resources = ALL_CONFIGS["resources"]


class ExchangeCreate(ItemFilter):
    __for_blocked_pages__ = ["exchange-sellect-confirm", "exchange-main-page"]
    __page_name__ = "exchange-create-page"
    
    async def data_preparate(self):
        if await self.scene.get_key("exchange-create-page", "settings") is None:
            await self.scene.update_key("exchange-create-page", "settings", json.dumps({"sell_resource": None,
                                                                                        "sell_amount_per_trade": None,
                                                                                        "count_offers": None,
                                                                                        "offer_type": "money",
                                                                                        "price": None,
                                                                                        "barter_resource": None,
                                                                                        "barter_amount": None}
                                                                                       ))
    
    async def content_worker(self):
        data = await self.scene.get_key("exchange-create-page", "settings")
        settings = json.loads(data)
        sell_resource = "Не выбран"
        barter_resource = "Не выбрано"
        if settings["sell_resource"] is not None:
            res1 = RESOURCES.get_resource(settings["sell_resource"])
            sell_resource = f"{res1.emoji} {res1.label}"
        if settings["barter_resource"] is not None:
            res2 = RESOURCES.get_resource(settings["barter_resource"])
            barter_resource = f"{res2.emoji} {res2.label}"
        if settings["offer_type"] == "money":
            content = (self.content + "Цена за сделку: {price}").format(
                                sell_resource=sell_resource,
                                sell_amount_per_trade=settings["sell_amount_per_trade"] or "Не установлено",
                                count_offers=settings["count_offers"] or "Не установлено",
                                offer_type="За деньги",
                                price=settings["price"] or "Не установлено"
                                )
        else:
            content = (self.content + "\nЗа ресурс: {barter_resource}\nКоличество за сделку: {barter_amount}").format(
                                sell_resource=sell_resource,
                                sell_amount_per_trade=settings["sell_amount_per_trade"] or "Не установлено",
                                count_offers=settings["count_offers"] or "Не установлено",
                                offer_type="Бартер",
                                barter_resource=barter_resource,
                                barter_amount=settings["barter_amount"] or "Не установлено"
                                )
        return content
    
    async def buttons_worker(self):
        data = await self.scene.get_key("exchange-create-page", "settings")
        settings = json.loads(data)
        self.row_width = 2
        buttons = []
        buttons.append({"text": f""})