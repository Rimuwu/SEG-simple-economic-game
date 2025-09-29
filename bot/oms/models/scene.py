import asyncio
from typing import Optional, Type

from aiogram import Bot
from aiogram.types import Message, CallbackQuery

from ..utils import list_to_inline, callback_generator
from ..manager import scene_manager
from .json_scene import scenes_loader, SceneModel
from .page import Page

class Scene:

    __scenes_path__: str = "scenes"
    __scene_name__: str = ''
    __pages__: list[Type[Page]] = [] # Регистрация страниц сцены

    # Функция для вставки сцены в БД
    # В функцию передаёт user_id: int, data: dict
    __insert_function__: callable = None

    # Функция для загрузки сцены из БД
    # В функцию передаёт user_id: int, вернуть должна dict
    __load_function__: callable = None

    # Функция для обновления сцены в БД
    # В функцию передаёт user_id: int, data: dict
    __update_function__: callable = None

    def __init__(self, user_id: int, bot_instance: Bot):
        self.user_id = user_id
        self.message_id: int = 0
        self.data: dict = {
            'scene': {}
        }

        self.__bot__ = bot_instance

        self.scene: SceneModel = scenes_loader.get_scene(
            self.__scene_name__) # type: ignore

        if not self.scene:
            print(scenes_loader.scenes)
            raise ValueError(f"Сцена {self.__scene_name__} не найдена")

        self.set_pages()
        self.page = self.start_page

        if not self.scene:
            raise ValueError(f"Сцена {self.__scene_name__} не найдена")

    def __call__(self, *args, **kwargs):
        # self.__init__(*args, **kwargs)
        return self

    async def start(self):
        await self.save_to_db()
        await self.send_message()


    # ===== Работа со страницами =====

    def set_pages(self):
        self.pages = {}
        for page in self.__pages__:
            self.pages[
                page.__page_name__
            ] = page(self.scene, this_scene=self)

            if page.__page_name__ not in self.data:
                self.data[
                    page.__page_name__
                ] = {}

    @property
    def start_page(self) -> str:
        return list(self.scene.pages.keys())[0]

    @property
    def current_page(self) -> Page:
        return self.pages.get(self.page, self.standart_page(self.page))

    async def update_page(self, page_name: str):

        if page_name not in self.scene.pages:
            raise ValueError(f"Страница {page_name} не найдена в сцене {self.__scene_name__}")

        self.page = page_name
        await self.save_to_db()
        await self.update_message()

    def get_page(self, page_name: str):
        if page_name not in self.pages:
            raise ValueError(f"Страница {page_name} не найдена в сцене {self.__scene_name__}")

        return self.pages.get(page_name, None)

    def standart_page(self, page_name: str) -> Page:
        sp = Page(self.scene, self, page_name)
        return sp


    # ===== Работа с сообщениями =====

    async def preparate_message_data(self):
        page = self.current_page
        text: str = await page.content_worker()
        buttons: list[dict] = await page.buttons_worker()

        to_pages: dict[str, str] = page.to_pages
        for page_name, title in to_pages.items():
            buttons.append({
                'text': title,
                'callback_data': callback_generator(
                    self.__scene_name__, 
                      'to_page', page_name
                      )
            })

        inl_markup = list_to_inline(buttons, row_width=page.row_width)
        return text, inl_markup

    async def send_message(self):
        content, markup = await self.preparate_message_data()

        message = await self.__bot__.send_message(self.user_id, content, 
                                        parse_mode=self.scene.settings.parse_mode,
                                        reply_markup=markup)
        self.message_id = message.message_id
        await self.save_to_db()

    async def update_message(self):
        content, markup = await self.preparate_message_data()

        await self.__bot__.edit_message_text(
            chat_id=self.user_id,
            message_id=self.message_id,
            text=content,
            parse_mode=self.scene.settings.parse_mode,
            reply_markup=markup
        )


    # ===== Работа с БД =====

    def data_to_save(self) -> dict:
        return {
            'user_id': self.user_id,
            'scene': self.__scene_name__,
            'page': self.page,
            'message_id': self.message_id,
            'data': self.data
        }

    def update_from_data(self, data: dict) -> None:
        self.page = data.get('page', self.start_page)
        self.message_id = data.get('message_id', 0)
        self.data = data.get('data', {'scene': {}})
        self.scene: SceneModel = scenes_loader.get_scene(
            self.__scene_name__) # type: ignore

    async def save_to_db(self) -> bool:
        if not self.__insert_function__ or not self.__update_function__:
            return False

        exist = await self.__load_function__(self.user_id)
        if not exist:
            await self.__insert_function__(user_id=self.user_id, data=self.data_to_save())
        else:
            await self.__update_function__(user_id=self.user_id, data=self.data_to_save())
        return True

    async def load_from_db(self, update_page: bool) -> bool:
        if not self.__load_function__:
            return False

        data = await self.__load_function__(user_id=self.user_id)
        if not data:
            return False

        self.update_from_data(data)
        if update_page:
            await self.update_message()
        return True


    # ===== Обработчики событий и страниц =====

    async def text_handler(self, message: Message) -> None:
        """Обработчик текстовых сообщений"""
        page = self.current_page
        await page.text_handler(message)

        if self.scene.settings.delete_after_send:
            await self.__bot__.delete_message(
                self.user_id, message.message_id
            )

    async def callback_handler(self, 
                callback: CallbackQuery, args: list) -> None:
        """Обработчик колбэков"""
        page = self.current_page
        await page.callback_handler(callback, args)


    # ===== Работа с данными сцены и страниц =====

    def get_data(self, element: str) -> Optional[dict]:
        """ Получение данных элемента

            Элементы - это страницы или сцена, то есть либо 'scene', либо название страницы
        """

        if element in self.data: return self.data[element]
        return None

    def set_data(self, element: str, value: dict) -> bool:
        """ Установка данных элемента (полная перезапись)
        """

        if element in self.data:
            self.data[element] = value
            asyncio.create_task(self.save_to_db())
            return True
        return False

    def update_key(self, element: str, key: str, value) -> bool:
        """ Обновление ключа в данных элемента
            Если ключа нет, он будет создан
            Аккуратно, value должен быть сериализуемым в JSON
        """
        if element in self.data:
            if key in self.data[element]:
                self.data[element][key] = value
            else:
                self.data[element][key] = value
            asyncio.create_task(self.save_to_db())
            return True
        return False

    def get_key(self, element: str, key: str):
        """ Получение ключа из данных элемента
        """
        if element in self.data:
            return self.data[element].get(key, None)
        return None


    # ==== Конец сцены ====

    async def end(self):
        await self.__bot__.delete_message(
            self.user_id, self.message_id
        )
        scene_manager.remove_scene(self.user_id)