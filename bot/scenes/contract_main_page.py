from .oneuser_page import OneUserPage
from modules.ws_client import get_contracts, create_contract, accept_contract,execute_contract, cancel_contract, get_company_contracts
from oms.utils import callback_generator


Page = OneUserPage


class ContractMainPage(Page):
    __page_name__ = "contract-main-page"
    
    async def content_worker(self):
        data = self.scene.get_data('scene')
        company_id = data.get('company_id')
        contracts_as_supplier = await get_company_contracts(company_id=company_id, as_supplier=True)
        contracts_as_customer = await get_company_contracts(company_id=company_id, as_customer=True)
        
        text = "📄 *Контракты*\n\n"
        text += f"🔹 *Контракты, где вы поставщик:* {len(contracts_as_supplier)}\n"
        text += f"🔹 *Контракты, где вы заказчик:* {len(contracts_as_customer)}\n\n"
        text += "Выберите действие:"

        return text

    async def buttons_worker(self):
        data = self.scene.get_data('scene')
        company_id = data.get('company_id')
        contracts_as_supplier = await get_company_contracts(company_id=company_id, as_supplier=True)
        contracts_as_customer = await get_company_contracts(company_id=company_id, as_customer=True)
        buttons = []
        if len(contracts_as_supplier) > 0 or len(contracts_as_customer) > 0:
            pass

        # await create_contract(
        #     supplier_company_id = 7,
        # customer_company_id = 8,
        # session_id = "коток",
        # resource = "oil",
        # amount_per_turn = 2,
        # duration_turns = 3,
        # payment_amount = 1000,
        # who_creator = 7 
        # )
        # print(await get_contracts())
        # await accept_contract(4, 8) # or await cancel_contract(4, 8)
        # await execute_contract(4)