from oms_dir import Page
from aiogram.types import Message
from modules.ws_client import get_session, create_user

class Start(Page):

    __page_name__ = 'start'

    async def text_handler(self, message: Message) -> None:
        """ Обработка и получение сообщения на странице
        """

        text = message.text
        response = await get_session(text)
        await message.delete()
        if not response:
            self.content = self.__page__.content
            self.content = self.content.replace("Введиие код для подключения к игровой сессии: ", "Неверный код, введите код заново: ")
            await self.scene.update_page(self.__page_name__)

        elif response.get("stage") != "FreeUserConnect":
            self.content = self.__page__.content
            self.content = self.content.replace("Введиие код для подключения к игровой сессии: ", "Сессия в процессе игры, введите другой код: ")
            await self.scene.update_page(self.__page_name__)
        else:

            self.scene.set_data('scene', {
                'session': text
            })
            await self.scene.update_page(
                'name-enter'
            )