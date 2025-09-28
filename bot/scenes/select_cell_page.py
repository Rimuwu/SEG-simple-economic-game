from oms import Page
from aiogram.types import Message, CallbackQuery
from modules.utils import update_page, cell_into_xy, xy_into_cell
from modules.ws_client import get_sessions_free_cells, set_company_position
from oms.utils import callback_generator


class SelectCell(Page):
    
    __page_name__ = 'select-cell-page'
    
    # Устанавливаем 7 кнопок в ряду
    row_width = 7
   
    async def buttons_worker(self):
        buttons = []
        
        # Получаем данные сессии
        scene_data = self.scene.get_data('scene')
        session_id = scene_data.get('session')
        
        if not session_id:
            return buttons
            
        # Получаем свободные ячейки
        free_cells = await get_sessions_free_cells(session_id=session_id)
        print(f"Свободные ячейки: {free_cells}")
        
        # Преобразуем в удобный формат для проверки
        free_cells_set = set()
        if free_cells:
            for cell in free_cells:
                x, y = cell.get('x'), cell.get('y')
                if x is not None and y is not None:
                    cell_name = xy_into_cell(x, y)
                    free_cells_set.add(cell_name)
        
        # Создаем кнопки 7x7
        for i in range(7):
            for j in range(7):
                cell_name = xy_into_cell(i, j)
                
                # Проверяем, свободна ли ячейка
                if cell_name in free_cells_set:
                    # Свободная ячейка - зеленая
                    button_text = f"🟢 {cell_name}"
                    callback_data = callback_generator(
                        self.scene.__scene_name__, 
                        'select_cell', 
                        cell_name
                    )
                else:
                    # Занятая ячейка - красная
                    button_text = f"🔴 {cell_name}"
                    callback_data = callback_generator(
                        self.scene.__scene_name__, 
                        'occupied_cell', 
                        cell_name
                    )
                
                buttons.append({
                    'text': button_text,
                    'callback_data': callback_data
                })
        
        return buttons
    
    @Page.on_callback('select_cell')
    async def on_select_cell(self, callback: CallbackQuery, args: list):
        """Обработка выбора свободной ячейки"""
        if len(args) < 4:  # scene:select_cell:scene_name:cell_name
            await callback.answer("❌ Ошибка в данных ячейки")
            return
            
        cell_name = args[3]  # Название ячейки (например, A1)
        
        try:
            # Получаем данные сцены
            scene_data = self.scene.get_data('scene')
            session_id = scene_data.get('session')
            company_id = scene_data.get('company_id')
            
            if not session_id or not company_id:
                await callback.answer("❌ Ошибка: нет данных о сессии или компании")
                return

            # Преобразуем название ячейки в координаты
            try:
                x, y = cell_into_xy(cell_name)
            except (ValueError, IndexError):
                await callback.answer("❌ Неверный формат ячейки")
                return

            # Отправляем запрос на установку позиции компании
            response = await set_company_position(company_id, x, y)
            
            if response and response.get('error'):
                await callback.answer(f"❌ Ошибка: {response.get('error')}")
                return

            # Успешно установили позицию
            await callback.answer(f"✅ Компания размещена на ячейке {cell_name}!")
            
            # Переходим на главную страницу игры
            await self.scene.update_page('main-page')

        except Exception as e:
            await callback.answer(f"❌ Произошла ошибка: {str(e)}")
    
    @Page.on_callback('occupied_cell')
    async def on_occupied_cell(self, callback: CallbackQuery, args: list):
        """Обработка нажатия на занятую ячейку"""
        if len(args) >= 4:
            cell_name = args[3]
            await callback.answer(f"❌ Ячейка {cell_name} уже занята")
        else:
            await callback.answer("❌ Эта ячейка занята")
    
