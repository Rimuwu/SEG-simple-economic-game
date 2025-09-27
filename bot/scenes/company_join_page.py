from oms_dir import Page
from aiogram.types import Message
from modules.ws_client import update_company_add_user, get_company

class CompanyJoin(Page):

    __page_name__ = 'company-join'

    async def text_handler(self, message: Message) -> None:
        """ Обработка и получение сообщения на странице
        """
        secret_code = message.text.strip()
        
        if not secret_code or not secret_code.isdigit():
            await message.delete()
            self.content = self.__page__.content
            self.content = self.content.replace("Введите секретный код: ", "❌ Код должен состоять только из цифр. Введите секретный код: ")
            await self.scene.update_page(self.__page_name__)
            return

        # Получаем данные сессии
        scene_data = self.scene.get_data('scene')
        session_id = scene_data['session']
        await message.delete()
        # Пытаемся присоединиться к компании
        response = await update_company_add_user(
            user_id=message.from_user.id,
            secret_code=int(secret_code)
        )
        if response is not None and response.get('error'):
            self.content = self.__page__.content
            self.content = self.content.replace("Введите секретный код: ", f"❌ Ошибка: {response.get('error')}. Попробуйте снова: ")
            await self.scene.update_page(self.__page_name__)
            return
        # После успешного присоединения получаем данные компании
        # Ищем компании в сессии и находим нужную по пользователю
        from modules.ws_client import get_users
        users = await get_users(session_id=session_id)
        user_company_id = None
        
        for user in users or []:
            if user.get('id') == message.from_user.id:
                user_company_id = user.get('company_id')
                break
        
        if user_company_id:
            company_data = await get_company(id=user_company_id)
            if company_data:
                # Сохраняем данные компании в сцене
                self.scene.set_data('scene', {
                    **scene_data,
                    'company': company_data
                })
        
        # Переходим на главную страницу
        await self.scene.update_page('main-page')