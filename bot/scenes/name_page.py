from oms_dir import Page
from aiogram.types import Message
from modules.ws_client import get_session, create_user, get_users
from os import getenv

class UserName(Page):

    __page_name__ = 'name-enter'

    async def text_handler(self, message: Message) -> None:
        """ Обработка и получение сообщения на странице
        """

        scene_data = self.scene.get_data('scene')
        session_id = scene_data['session']

        text = message.text
        users = await get_users(session_id=session_id)

        flag_name = True
        for i in users:
            if i['username'] == text:
                flag_name = False
                break

        if flag_name:
            await create_user(
                user_id=message.from_user.id,
                username=text,
                password=getenv("UPDATE_PASSWORD"),
                session_id=session_id
            )
            await self.scene.update_page('company-option')
        else:
            self.content = self.__page__.content
            self.content += "\nИмя занято"

            await self.scene.update_page(self.__page_name__)

        await message.delete()