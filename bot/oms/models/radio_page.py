from ..utils import callback_generator
from .page import Page

class RadioTypeScene(Page):
    """Страница с выбором из нескольких вариантов (radio).
    """

    __page_name__: str = ''
    __options__: dict = {} # 'key': 'text'
    __select_icon__: str = '✅'
    __scene_key__: str = 'radio-type'
    __default_value__: str = ''
    __next_page__: str = ''


    __json_args__ = [
        'options', 'scene_key', 'default_value',
        'next_page', 'select_icon'
    ]

    def __after_init__(self):
        self.options = self.__options__
        self.select_icon = self.__select_icon__
        self.default_value = self.__default_value__
        self.scene_key = self.__scene_key__
        self.next_page = self.__next_page__

    async def data_preparate(self):
        selected = self.scene.get_key(
            self.__page_name__, self.scene_key)
        if not selected:

            await self.scene.update_key(
                'scene',
                self.scene_key, 
                self.default_value
            )
            await self.scene.update_key(
                self.__page_name__,
                self.scene_key, 
                self.default_value
            )


    async def buttons_worker(self):
        buttons = []
        selected = self.scene.get_key(
            self.__page_name__, self.scene_key)

        for key, text in self.options.items():
            if selected == key:
                text = f"{self.select_icon} {text}"

            buttons.append({
                'text': text,
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'radio', key)
            })

        return buttons

    @Page.on_callback('radio')
    async def handle_int(self, callback, args: list):
        value = args[1]

        # Сохраняем текст в сцену
        await self.scene.update_key(
            'scene',
            self.scene_key, 
            value
        )

        # Сохраняем текст в страницу
        await self.scene.update_key(
            self.__page_name__,
            self.scene_key, 
            value
        )

        # Переходим к следующей странице
        if self.next_page:
            await self.scene.update_page(
                self.next_page)
        else:
            await self.scene.update_message_markup()