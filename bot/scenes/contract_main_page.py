from .oneuser_page import OneUserPage
from modules.ws_client import get_contracts, create_contract, accept_contract,execute_contract, cancel_contract


Page = OneUserPage


class ContractMainPage(Page):
    __page_name__ = "contract-main-page"
    
    async def content_worker(self):
        await create_contract(
            supplier_company_id = 7,
        customer_company_id = 8,
        session_id = "коток",
        resource = "oil",
        amount_per_turn = 2,
        duration_turns = 3,
        payment_amount = 1000,
        who_creator = 7 
        )
        print(await get_contracts())
        await accept_contract(4, 8)
        await execute_contract(4)
        await cancel_contract(4, 8)
        return "Блять"