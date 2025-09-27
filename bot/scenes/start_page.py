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

        if not response:
            self.content = self.__page__.content
            self.content += "\nНеправильный код сессии"

            await self.scene.update_page(self.__page_name__)
        else:

            self.scene.set_data('scene', {
                'session': text
            })
            await self.scene.update_page(
                'name-enter'
            )
        
        await message.delete()