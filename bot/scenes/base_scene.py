"""
Базовый класс Scene с поддержкой админ-панели
Все сцены должны наследоваться от AdminScene вместо Scene
"""
import os
from oms import Scene
from oms.utils import callback_generator


# Получаем список ID администраторов из .env
ADMIN_IDS = [admin_id.strip() for admin_id in os.getenv("ADMIN_IDS", "").strip().split(",") if admin_id.strip()]


class AdminScene(Scene):
    """
    Расширенный класс Scene с автоматической поддержкой админ-панели
    
    Автоматически добавляет кнопку перехода в админ-панель для всех администраторов
    на всех страницах всех сцен.
    """
    
    async def preparate_message_data(self, only_buttons: bool = False):
        """
        Переопределенный метод preparate_message_data
        Добавляет кнопку админ-панели для администраторов
        """
        # Вызываем родительский метод для получения базовых данных
        page = self.current_page
        await page.data_preparate()

        if not only_buttons:
            text: str = await page.content_worker()
        else: 
            text = page.__page__.content

        buttons: list[dict] = await page.buttons_worker()

        # Добавляем кнопки перехода между страницами
        if page.enable_topages:
            to_pages: dict[str, str] = page.to_pages

            for i, (page_name, title) in enumerate(to_pages.items()):
                buttons.append({
                    'text': title,
                    'callback_data': callback_generator(
                        self.__scene_name__, 
                        'to_page', page_name
                    ),
                    'next_line': len(buttons) > 0 and i == 0
                })

        # ===== ДОБАВЛЕНИЕ КНОПКИ АДМИН-ПАНЕЛИ =====
        # Проверяем, является ли пользователь администратором
        user_id_str = str(self.user_id)
        is_admin = user_id_str in ADMIN_IDS
        
        # Проверяем, не находимся ли мы уже на странице админ-панели
        is_admin_page = page.__page_name__ == "admin-panel-page"
        
        if is_admin and not is_admin_page:
            # Сохраняем текущую страницу для возврата
            scene_data = self.get_data('scene')
            if not scene_data:
                scene_data = {}
            scene_data['previous_page'] = self.page
            await self.set_data('scene', scene_data)
            
            # Добавляем кнопку админ-панели
            buttons.append({
                'text': '🔧 Админ-панель',
                'callback_data': callback_generator(
                    self.__scene_name__, 
                    'to_page', 
                    'admin-panel-page'
                ),
                'next_line': True  # Кнопка будет на новой строке
            })
        
        # Импортируем list_to_inline из utils
        from oms.utils import list_to_inline
        inl_markup = list_to_inline(buttons, page.row_width)
        
        return text, inl_markup
