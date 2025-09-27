from oms_dir import Page
from aiogram.types import Message, CallbackQuery
from modules.ws_client import get_company, get_users

class MainPage(Page):

    __page_name__ = 'main-page'

    async def content_worker(self) -> str:
        """ Генерация контента для главной страницы
        """
        scene_data = self.scene.get_data('scene')
        company_data = scene_data.get('company', {})
        session_id = scene_data.get('session')
        
        if not company_data and session_id:
            # Пытаемся получить данные компании пользователя
            user_company = await get_company(session_id=session_id)
            if user_company:
                company_data = user_company
                # Обновляем данные в сцене
                self.scene.set_data('scene', {
                    **scene_data,
                    'company': company_data
                })

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
            
            content = f"""🏢 **{company_name}**

👥 Участников: {participants_count}
🔑 Код для присоединения: {secret_code}

Выберите действие из меню ниже:"""
        else:
            content = "❌ Ошибка: данные компании не найдены"
            
        return content

    async def text_handler(self, message: Message) -> None:
        """ Обработка текстовых сообщений на главной странице
        """
        # На главной странице обычно не обрабатываем текст
        await message.delete()

    async def callback_handler(self, callback: CallbackQuery, args: list) -> None:
        """ Обработка колбэков на главной странице
        """
        # Здесь можно добавить обработку специфичных колбэков главной страницы
        # Пока что просто подтверждаем колбэк
        await callback.answer()