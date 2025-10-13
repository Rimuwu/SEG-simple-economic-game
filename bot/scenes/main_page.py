from oms import Page
from aiogram.types import Message, CallbackQuery
from modules.ws_client import get_company, get_users

class MainPage(Page):

    __page_name__ = 'main-page'

    async def content_worker(self) -> str:
        """ Генерация контента для главной страницы
        """
        scene_data = self.scene.get_data('scene')
        company_id = scene_data.get('company_id')
        session_id = scene_data.get('session')
        
        # Получаем данные компании по company_id
        company_data = None
        if company_id:
            company_data = await get_company(id=company_id)
        elif session_id:
            # Если нет company_id, пытаемся получить первую компанию в сессии
            company_data = await get_company(session_id=session_id)
            if company_data:
                # Обновляем company_id в сцене
                await self.scene.update_key('scene', 'company_id', company_data.get('id'))

        if company_data:
            company_name = company_data.get('name', 'Неизвестная компания')
            secret_code = company_data.get('secret_code', 'Неизвестно')
            company_id = company_data.get('id')

            # Получаем количество участников
            participants_count = 1  # По умолчанию
            if company_id and session_id:
                try:
                    users = await get_users(company_id=company_id, session_id=session_id)
                    participants_count = len(users) if users else 1
                except:
                    participants_count = 1

            content = (
                f"🏢 *{company_name}*\n\n"
                f"🏦 Банковская информация:\n"
                f"- Налог: {company_data.get('tax_debt')}\n"
                f"- Кредит: {len(company_data['credits'])}\n"
                f"- Баланс: {company_data['balance']}\n\n"
                f"⭐️ Репутация: {company_data['reputation']}\n"
                f"💼 Осталось места в инвентаре: {company_data['warehouse_free_size']}/{company_data['warehouse_capacity']}\n"
                f"Выберите действие из меню ниже:"
            )
        else:
            content = "❌ Ошибка: данные компании не найдены"

        return content