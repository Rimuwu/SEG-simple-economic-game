from typing import TYPE_CHECKING, Optional, Type

from oms_dir.models.scene import ScenePage, SceneModel, SceneLoader
from aiogram.types import Message, CallbackQuery

if TYPE_CHECKING:
    from bot.oms_dir.scene import Scene

class Page:

    __page_name__: str = ''

    def __init__(self, scene: SceneModel, page_name: str = '', this_scene = None):
        if page_name and not self.__page_name__: 
            self.__page_name__ = page_name

        self.__scene__ = scene
        self.__page__: ScenePage = scene.pages.get(
            self.__page_name__) # type: ignore

        if not self.__page__:
            raise ValueError(f"Страница {self.__page_name__} не найдена в сцене {scene.name} -> {list(scene.pages.keys())}")

        self.title = self.__page__.title
        self.content = self.__page__.content
        self.to_pages = self.__page__.to_pages

        self.scene: Optional[Scene] = this_scene

    def __call__(self, *args, **kwargs):
        # self.__init__(*args, **kwargs)
        return self

    def get_pagedata(self):
        return self.scene.get_data(self.__page_name__)

    def update_pagedata(self, data: dict) -> bool:
        return self.scene.set_data(self.__page_name__, data)

    async def content_worker(self) -> str:
        return self.content
        # raise NotImplementedError("Метод content_worker должен быть реализован в подклассе")


    async def buttons_worker(self) -> list[dict]:
        return []
        # raise NotImplementedError("Метод buttons_worker должен быть реализован в подклассе")


    async def text_handler(self, message: Message) -> None:
        """ Обработка и получение сообщения на странице
        """
        pass


    async def callback_handler(self, callback: CallbackQuery, args: list) -> None:
        """ Обработка и получение нажатий
        """
        pass