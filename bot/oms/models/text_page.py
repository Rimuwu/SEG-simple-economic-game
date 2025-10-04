from .page import Page

class TextTypeScene(Page):

    __page_name__: str = ''
    __max_length__: int = 4096  # Максимальная длина текста по умолчанию
    __min_length__: int = 1     # Минимальная длина текста по умолчанию
    __scene_key__: str = 'text-type'  # Ключ сцены для сохранения данных
    __next_page__: str = ''  # Следующая страница после ввода текста


    __json_args__ = [
        'max_length', 'min_length', 'scene_key',
        'next_page'
    ] # Аргументы которые можно переопределить из json конфига

    def __after_init__(self):
        self.max_length = self.__max_length__
        self.min_length = self.__min_length__
        self.scene_key = self.__scene_key__
        self.next_page = self.__next_page__

    @Page.on_text('str')
    async def handle_text(self, message, value: str):
        text = value.strip()
        self.clear_content()

        if len(text) < self.min_length:
            self.content += f"\n\nТекст слишком короткий. Минимальная длина: {self.min_length} символов."
            await self.scene.update_message()
            return

        if len(text) > self.max_length:
            self.content += f"\n\nТекст слишком длинный. Максимальная длина: {self.max_length} символов."
            await self.scene.update_message()
            return

        # Сохраняем текст в сцену
        self.scene.update_key(
            'scene',
            self.scene_key, 
            text
        )

        # Сохраняем текст в страницу
        self.scene.update_key(
            self.__page_name__,
            self.scene_key, 
            text
        )

        # Переходим к следующей странице
        if self.next_page:
            await self.scene.update_page(
                self.next_page)
        else:
            self.clear_content()
            await self.scene.update_message()