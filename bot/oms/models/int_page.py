from .page import Page

class IntTypeScene(Page):

    __page_name__: str = ''
    __max_int__: int = 4096
    __min_int__: int = 1
    __scene_key__: str = 'int-type'
    __next_page__: str = ''


    __json_args__ = [
        'max_int', 'min_int', 'scene_key',
        'next_page'
    ]

    def __after_init__(self):
        self.max_int = self.__max_int__
        self.min_int = self.__min_int__
        self.scene_key = self.__scene_key__
        self.next_page = self.__next_page__

    @Page.on_text('int')
    async def handle_int(self, message, value: int):
        self.clear_content()

        if value < self.min_int:
            self.content += f"\n\nЧисло слишком маленькое. Минимальное число: {self.min_int}"
            await self.scene.update_message()
            return

        if value > self.max_int:
            self.content += f"\n\nЧисло слишком большое. Максимальная число: {self.max_int}"
            await self.scene.update_message()
            return

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
            self.clear_content()
            await self.scene.update_message()