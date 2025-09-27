from typing import TYPE_CHECKING, Optional
from datetime import datetime, timedelta
import re

from .json_scene import ScenePage, SceneModel
from aiogram.types import Message, CallbackQuery

if TYPE_CHECKING:
    from .scene import Scene

class Page:

    __page_name__: str = ''

    def __init__(self, 
                 scene: SceneModel, 
                 this_scene: 'Scene',
                 page_name: str = ''):
        if page_name and not self.__page_name__: 
            self.__page_name__ = page_name

        self.__scene__: SceneModel = scene
        self.__page__: ScenePage = scene.pages.get(
            self.__page_name__) # type: ignore

        self.__callback_handlers__ = {}
        self.__text_handlers__ = {}

        # Собираем обработчики из методов класса
        for attr_name in dir(self.__class__):
            if not attr_name.startswith('_'):  # Пропускаем приватные методы
                attr = getattr(self.__class__, attr_name)
                if callable(attr):
                    # Проверяем текстовые обработчики
                    if hasattr(attr, '_text_handler_info'):
                        for handler_info in attr._text_handler_info:
                            data_type = handler_info['data_type']
                            separator = handler_info['separator']

                            if data_type in self.__text_handlers__:
                                raise ValueError(f"Обработчик для типа {data_type} уже зарегистрирован.")

                            # Получаем bound method для экземпляра
                            bound_method = getattr(self, attr_name)
                            self.__text_handlers__[data_type] = {
                                'handler': bound_method,
                                'separator': separator
                            }

                    # Проверяем callback обработчики
                    if hasattr(attr, '_callback_handler_info'):
                        for handler_info in attr._callback_handler_info:
                            callback_type = handler_info['callback_type']

                            if callback_type in self.__callback_handlers__:
                                raise ValueError(f"Обработчик для {callback_type} уже зарегистрирован.")

                            # Получаем bound method для экземпляра
                            bound_method = getattr(self, attr_name)
                            self.__callback_handlers__[callback_type] = bound_method

        if not self.__page__:
            raise ValueError(f"Страница {self.__page_name__} не найдена в сцене {scene.name} -> {list(scene.pages.keys())}")

        self.title: str = self.__page__.title
        self.content: str = self.__page__.content
        self.to_pages: dict = self.__page__.to_pages

        self.scene: Scene = this_scene

    def __call__(self, *args, **kwargs):
        return self

    def get_data(self, key: Optional[str] = None):
        """ Получение данных страницы (всех или по ключу)
        """
        if key:
            return self.scene.get_key(self.__page_name__, key)
        return self.scene.get_data(self.__page_name__)

    def set_data(self, data: dict) -> bool:
        """ Установка данных (с польной перезаписью) страницы
        """
        return self.scene.set_data(self.__page_name__, data)

    def update_data(self, key: str, value) -> bool:
        """ Обновление данных страницы по ключу
        """
        return self.scene.update_key(self.__page_name__, key, value)



    @staticmethod
    def on_text(data_type: str, separator: str = ','):
        """ Декоратор для регистрации обработчиков текстовых сообщений
            Поддерживаемые типы: 'int', 'str', 'time', 'list'

            Пример использования:

            @Page.on_text('int')
            async def handle_int(self, message: Message, value: int):
                print(f"Получено число: {value}")

            @Page.on_text('time')
            async def handle_time(self, message: Message, value: datetime):
                print(f"Получено время: {value}")

            @Page.on_text('list', separator=';')
            async def handle_list(self, message: Message, value: list):
                print(f"Получен список: {value}")

            @Page.on_text('all')
            async def handle_all_text(self, message: Message):
                print(f"Получен любой текст: {message.text}")
        """
        def decorator(func):
            # Сохраняем информацию о декораторе в атрибуте функции
            if not hasattr(func, '_text_handler_info'):
                func._text_handler_info = []
            
            func._text_handler_info.append({
                'data_type': data_type,
                'separator': separator
            })
            return func
        return decorator

    def _parse_time(self, text: str) -> Optional[datetime]:
        """ Парсинг времени из строки """
        now = datetime.now()

        # Паттерн для времени с датой: 16:30 21.10.2025
        pattern_with_date = r'(\d{1,2}):(\d{2})\s+(\d{1,2})\.(\d{1,2})\.(\d{4})'
        match_date = re.match(pattern_with_date, text.strip())

        if match_date:
            hour, minute, day, month, year = map(int, match_date.groups())
            try:
                return datetime(year, month, day, hour, minute)
            except ValueError:
                return None

        # Паттерн для времени без даты: 16:30
        pattern_time_only = r'(\d{1,2}):(\d{2})'
        match_time = re.match(pattern_time_only, text.strip())

        if match_time:
            hour, minute = map(int, match_time.groups())
            try:
                target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

                # Если время уже прошло сегодня, устанавливаем на завтра
                if target_time <= now:
                    target_time += timedelta(days=1)

                return target_time
            except ValueError:
                return None

        return None

    def _parse_text(self, text: str, data_type: str, separator: str = ','):
        """ Парсинг текста в соответствующий тип данных """
        text = text.strip()

        if data_type == 'int':
            try:
                return int(text)
            except ValueError:
                return None

        elif data_type == 'str':
            return text

        elif data_type == 'time':
            return self._parse_time(text)

        elif data_type == 'list':
            parsed_list = [item.strip() for item in text.split(separator) if item.strip()]
            # Если в списке только 1 элемент, считаем это не списком, а текстом
            if len(parsed_list) <= 1:
                return None
            return parsed_list

        return None

    async def text_handler(self, message: Message) -> None:
        """ Обработка текстовых сообщений с автоматическим определением типа """
        text = message.text or ""
        handled = False

        # Определяем порядок приоритета типов (от наиболее к наименее специфичным)
        type_priority = ['time', 'int', 'list', 'str']
        
        # Проверяем каждый тип в порядке приоритета
        for data_type in type_priority:
            if data_type not in self.__text_handlers__:
                continue
                
            handler_info = self.__text_handlers__[data_type]
            handler = handler_info['handler']
            separator = handler_info['separator']

            parsed_value = self._parse_text(text, data_type, separator)

            if parsed_value is not None:
                await handler(message=message, value=parsed_value)
                handled = True
                break

        # Если есть обработчик для 'all', вызываем его всегда
        if 'all' in self.__text_handlers__:
            handler = self.__text_handlers__['all']['handler']
            await handler(message=message)

        # Если текст не был обработан, можно добавить обработку по умолчанию
        if not handled and 'all' not in self.__text_handlers__:
            pass  # Здесь можно добавить обработку по умолчанию



    @staticmethod
    def on_callback(callback_type: str):
        """ Декоратор для регистрации обработчиков нажатий кнопок
            Пример использования:

            @Page.on_callback('my_callback')
            async def my_callback_handler(self, 
                callback: CallbackQuery, args: list):
                print(args) # ['additional', 'args']

            Пример создания кнопки для такого обработчика:
            {
                'text': 'Нажми меня',
                'callback_data': callback_generator(
                    self.scene.__scene_name__, 
                    'my_callback', 
                    'additional', 'args'
                )
            }

            Нельзя ставить 2 обработчика на один callback_type!
        """
        def decorator(func):
            # Сохраняем информацию о декораторе в атрибуте функции
            if not hasattr(func, '_callback_handler_info'):
                func._callback_handler_info = []

            func._callback_handler_info.append({
                'callback_type': callback_type
            })
            return func
        return decorator

    async def callback_handler(self, 
                    callback: CallbackQuery, args: list) -> None:
        """ Обработка и получение нажатий
        """
        if args and args[0] in self.__callback_handlers__:
            callback_type = args[0]
            handler = self.__callback_handlers__[callback_type]
            await handler(callback=callback, args=args)

        if 'all' in self.__callback_handlers__:
            handler = self.__callback_handlers__['all']
            await handler(callback=callback, args=args)



    def clear_content(self):
        """ Очистка контента до значения из конфига
        """
        self.content = self.__page__.content



    # МОЖНО И НУЖНО МЕНЯТЬ !

    async def content_worker(self) -> str:
        return self.content

    async def buttons_worker(self) -> list[dict]:
        return []