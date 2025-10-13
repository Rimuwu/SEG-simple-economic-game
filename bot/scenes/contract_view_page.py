from .oneuser_page import OneUserPage
from modules.ws_client import get_company_contracts, accept_contract, get_contract


Page = OneUserPage


class ContractView(Page):
    __for_blocked_pages__ = ["contract-main-page"]
    
    async def data_preparate(self):
        if self.scene.get_key(self.__page_name__, "stage") is None:
            self.scene.update_key(self.__page_name__, "stage", "main") #view
        if self.scene.get_key(self.__page_name__, "contract_id") is None:
            self.scene.update_key(self.__page_name__, "contract_id", -1)
    
    
    async def content_worker(self):
        datap = self.scene.get_data(self.__page_name__)
        data = self.scene.get_data("scene")
        compnay_id = data.get("company_id")
        session_id = data.get("session")
        stage = datap.get("stage", "main")
        content = ''
        if stage == "main":
            content = "Нажмите на кнопку для просмтотра информации о контракте"
        elif stage == "view":
            contract_id = datap.get("contract_id")
            if contract_id == -1:
                return "Ошибка перехода на страницу, контракт не выбран"
            contract = await get_contract(),