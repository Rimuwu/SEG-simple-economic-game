from oms import Page

class ChangeTurnPage(Page):
    __page_name__ = "change-turn-page"
    
    async def content_worker(self):
        return "*Смена хода...*\n\n"