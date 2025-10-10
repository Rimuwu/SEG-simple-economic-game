from pprint import pprint
from typing import Optional
from ..utils import callback_generator
from .page import Page
from aiogram.types import CallbackQuery

class OptionTypeScene(Page):
    """Страница с выбором нескольких вариантов (checkbox).
    """

    __page_name__: str = ''
    __options__: dict = {} # 'key': 'text'
    __select_icon__: str = '✅'
    __scene_key__: str = 'option-type'
    __default_values__: Optional[list] = None
    __max_select__: int = 0  # 0 - неограниченно
    __max_on_page__: int = 0  # Количество элементов на страницу (0 - все на одной странице)
    __prev_page_icon__: str = '◀️'  # Иконка для кнопки "предыдущая страница"
    __next_page_icon__: str = '▶️'  # Иконка для кнопки "следующая страница"
    __separator__: bool = False

    __json_args__ = [
        'options', 'scene_key', 'default_values',
        'max_on_page', 'prev_page_icon', 'next_page_icon',
        'select_icon', 'max_select', 'separator'
    ]

    def __after_init__(self):
        self.options = self.__options__
        self.select_icon = self.__select_icon__
        self.max_on_page = self.__max_on_page__
        self.default_values = self.__default_values__
        self.scene_key = self.__scene_key__
        self.max_select = self.__max_select__
        self.prev_page_icon = self.__prev_page_icon__
        self.next_page_icon = self.__next_page_icon__
        self.separator = self.__separator__

    async def data_preparate(self):
        selected = self.scene.get_key(
            self.__page_name__, self.scene_key)

        if not selected:
            await self.scene.update_key(
                'scene',
                self.scene_key, 
                self.default_values or []
            )
            await self.scene.update_key(
                self.__page_name__,
                self.scene_key, 
                self.default_values or []
            )

        # Инициализация текущей страницы
        current_page = self.scene.get_key(
            self.__page_name__, 'current_page')

        if current_page is None:
            await self.scene.update_key(
                self.__page_name__,
                'current_page', 
                0
            )


    async def buttons_worker(self):
        buttons = []
        selected = self.scene.get_key(
            self.__page_name__, self.scene_key)

        # Получаем текущую страницу
        current_page = self.scene.get_key(
            self.__page_name__, 'current_page') or 0

        # Если пагинация включена и установлен лимит элементов на странице
        if self.max_on_page > 0:
            # Получаем список всех опций
            options_list = list(self.options.items())
            total_options = len(options_list)
            total_pages = (total_options + self.max_on_page - 1) // self.max_on_page
            
            # Проверяем, что текущая страница в допустимых пределах
            if current_page >= total_pages:
                current_page = total_pages - 1
                await self.scene.update_key(
                    self.__page_name__,
                    'current_page', 
                    current_page
                )
            
            # Вычисляем индексы для текущей страницы
            start_idx = current_page * self.max_on_page
            end_idx = min(start_idx + self.max_on_page, total_options)
            
            # Получаем опции для текущей страницы
            page_options = options_list[start_idx:end_idx]
            
            # Создаем кнопки для опций текущей страницы
            for key, text in page_options:
                if key in selected:
                    text = f"{self.select_icon} {text}"

                buttons.append({
                    'text': text,
                    'callback_data': callback_generator(
                        self.scene.__scene_name__,
                        'option', key)
                })
            
            # Добавляем кнопки навигации, если страниц больше одной
            if total_pages > 1:
                nav_buttons = []

                nav_buttons.append({
                    'text': self.prev_page_icon,
                    'callback_data': callback_generator(
                        self.scene.__scene_name__,
                        'prev_page'),
                    'next_line': True
                })

                nav_buttons.append({
                    'text': self.next_page_icon,
                    'callback_data': callback_generator(
                        self.scene.__scene_name__,
                        'next_page')
                })
                if self.separator:
                    nav_buttons.append({
                        'text': ' ',
                        'callback_data': callback_generator(
                            self.scene.__scene_name__,
                            ' '),
                        'ignore_row': True
                    })

                # Добавляем кнопки навигации отдельной строкой
                if nav_buttons:
                    buttons.extend(nav_buttons)
        else:
            # Без пагинации - показываем все опции
            for key, text in self.options.items():
                if key in selected:
                    text = f"{self.select_icon} {text}"

                buttons.append({
                    'text': text,
                    'callback_data': callback_generator(
                        self.scene.__scene_name__,
                        'option', key)
                })

        return buttons

    @Page.on_callback('option')
    async def handle_int(self, callback: CallbackQuery, 
                         args: list):
        value = args[1]

        scene_data = self.scene.get_key(
            'scene',
            self.scene_key
        ) or []

        if self.max_select > 0 and len(scene_data) >= self.max_select and value not in scene_data:
            # Превышено максимальное количество выборов
            await callback.answer(f"Максимальное количество выборов: {self.max_select}", show_alert=True)
            return

        if value in scene_data:
            scene_data.remove(value)
        else:
            scene_data.append(value)

        # Сохраняем текст в сцену
        await self.scene.update_key(
            'scene',
            self.scene_key, 
            scene_data
        )

        page_data = self.scene.get_key(
            self.__page_name__,
            self.scene_key
        ) or []

        if value in page_data:
            page_data.remove(value)
        else:
            page_data.append(value)

        # Сохраняем текст в сцену
        await self.scene.update_key(
            self.__page_name__,
            self.scene_key, 
            page_data
        )

        await self.scene.update_message_markup()

    @Page.on_callback('prev_page')
    async def handle_prev_page(self, callback: CallbackQuery, args: list):
        """Обработчик кнопки "предыдущая страница"
        """
        current_page = self.scene.get_key(
            self.__page_name__, 'current_page') or 0
        
        if current_page > 0:
            await self.scene.update_key(
                self.__page_name__,
                'current_page', 
                current_page - 1
            )
            await self.scene.update_message_markup()
        else:
            if self.max_on_page > 0:
                total_options = len(self.options)
                total_pages = (total_options + self.max_on_page - 1) // self.max_on_page
                if total_pages > 1:
                    await self.scene.update_key(
                        self.__page_name__,
                        'current_page', 
                        total_pages - 1
                    )
                    await self.scene.update_message_markup()

    @Page.on_callback('next_page')
    async def handle_next_page(self, callback: CallbackQuery, args: list):
        """Обработчик кнопки "следующая страница"
        """
        current_page = self.scene.get_key(
            self.__page_name__, 'current_page') or 0
        
        if self.max_on_page > 0:
            total_options = len(self.options)
            total_pages = (total_options + self.max_on_page - 1) // self.max_on_page
            
            if current_page < total_pages - 1:
                await self.scene.update_key(
                    self.__page_name__,
                    'current_page', 
                    current_page + 1
                )
                await self.scene.update_message_markup()
            else:
                await self.scene.update_key(
                    self.__page_name__,
                    'current_page', 
                    0
                )
                await self.scene.update_message_markup()