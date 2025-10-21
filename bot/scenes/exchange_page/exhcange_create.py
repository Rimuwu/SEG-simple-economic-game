from utils.filter_item import ItemFilter


class ExchangeCreate(ItemFilter):
    __for_blocked_pages__ = ["exchange-sellect-confirm", "exchange-main-page"]
    __page_name__ = "exchange-create-page"