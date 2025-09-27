import asyncio
from typing import Literal, Optional, Type
from modules.utils import list_to_inline
from oms_dir.manager import manager
from oms_dir.models.scene import scenes_loader, SceneModel
from oms_dir.page import Page
from bot_instance import bot

from aiogram.types import Message, CallbackQuery

CALLBACK_PREFIX = 'scene'
CALLBACK_SEPARATOR = ':'

def callback_generator(scene_name: str, c_type: str, *args):
    """ prefix:type:name:*args
    """
    sep = CALLBACK_SEPARATOR
    return f'{CALLBACK_PREFIX}{sep}{c_type}{sep}{scene_name}{sep}{":".join(args)}'

class Scene:

    __scenes_path__: str = "scenes"
    __scene_name__: str = ''
    __pages__: list[Type[Page]] = [] # Регистрация страниц сцены

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.message_id: int = 0
        self.data: dict = {
            'scene': {}
        }

        self.scene: SceneModel = scenes_loader.get_scene(
            self.__scene_name__) # type: ignore

        if not self.scene:
            print(scenes_loader.scenes)
            raise ValueError(f"Сцена {self.__scene_name__} не найдена")

        self.pages = {}
        for page in self.__pages__:
            self.pages[
                page.__page_name__
            ] = page(self.scene, this_scene=self)
            self.data[
                page.__page_name__
            ] = {}

        self.page = self.start_page

        if not self.scene:
            raise ValueError(f"Сцена {self.__scene_name__} не найдена")

    def __call__(self, *args, **kwargs):
        # self.__init__(*args, **kwargs)
        return self

    @property
    def start_page(self) -> str:
        return list(self.scene.pages.keys())[0]

    async def start(self):
        await self.save_to_db()
        await self.send_message()

    # Это вызываем для получения данных
    async def data_getter(self) -> None:
        """ Функция для запроса данных у источника
        """
        pass

    # Это вызываем для установки данных
    async def data_setter(self, **kwargs) -> None:
        """ Функция для установки данных в источник
        """
        pass

    async def update_page(self, page_name: str):
        print(
            'from:', self.page,
            'to:', page_name
        )
        self.page = page_name
        await self.save_to_db()
        await self.update_message()

    def get_page(self, page_name: str):
        return self.pages.get(page_name, None)

    @property
    def current_page(self) -> Page:
        return self.pages.get(self.page, self.standart_page(self.page))

    def standart_page(self, page_name: str) -> Page:
        sp = Page(self.scene, page_name, this_scene=self)
        return sp

    async def preparate_message_data(self):
        page = self.current_page
        text: str = await page.content_worker()
        buttons: list[dict] = await page.buttons_worker()

        to_pages: dict[str, str] = page.to_pages
        for page_name, title in to_pages.items():
            buttons.append({
                'text': title,
                'callback_data': callback_generator(self.__scene_name__, 
                                                    'to_page', page_name)
            })

        inl_markup = list_to_inline(buttons)
        return text, inl_markup

    async def send_message(self):
        content, markup = await self.preparate_message_data()

        message = await bot.send_message(self.user_id, content, 
                                             reply_markup=markup)
        self.message_id = message.message_id
        await self.save_to_db()

    async def update_message(self):
        content, markup = await self.preparate_message_data()

        await bot.edit_message_text(
            chat_id=self.user_id,
            message_id=self.message_id,
            text=content,
            reply_markup=markup
        )

    async def save_to_db(self):
        pass

        # update_db(self.user_id, 
        #           {
        #               'page': self.page,
        #               'scene': self.__scene_name__,
        #               'message_id': self.message_id
        #           })

    async def load_from_db(self):
        pass

        # data = get_from_db(self.user_id)
        # if not data: return

        # self.page = data.get('page', self.start_page)
        # self.message_id = data.get('message_id', 0)
        # self.scene: SceneModel = scenes_loader.get_scene(
        #     self.__scene_name__) # type: ignore


    async def text_handler(self, message: Message) -> None:
        """Обработчик текстовых сообщений"""

        page = self.current_page
        await page.text_handler(message)

    async def callback_handler(self, callback: CallbackQuery, args: list) -> None:
        """Обработчик колбэков"""
        page = self.current_page
        await page.callback_handler(callback, args)


    def get_data(self, element: str) -> Optional[dict]:
        """ Элементы - это страницы или сцена, то есть либо scene, либо название странц
        """

        if element in self.data:
            return self.data[element]

        return None

    def set_data(self, element: str, value: dict) -> bool:

        if element in self.data:
            self.data[element] = value
            asyncio.create_task(self.save_to_db())
            return True
        return False

    async def end(self):
        await bot.delete_message(self.user_id, self.message_id)
        manager.remove_scene(self.user_id)