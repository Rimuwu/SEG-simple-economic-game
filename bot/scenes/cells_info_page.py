from oms import Page
from modules.ws_client import get_company
from modules.utils import xy_into_cell
from modules.resources import get_resource_name, get_resource_emoji

class CellsInfo(Page):
    
    __page_name__ = "cells-info-page"
    
    async def content_worker(self):
        scene_data = self.scene.get_data('scene')
        company_id = scene_data.get('company_id')
        
        if not company_id:
            return "❌ Ошибка: компания не найдена"
        
        # Получаем данные компании
        company_data = await get_company(id=company_id)
        
        if isinstance(company_data, str):
            return f"❌ Ошибка при получении данных: {company_data}"
        
        # Получаем информацию о клетке
        cell_type = company_data.get('cell_type', 'unknown')
        cell_info = company_data.get('cell_info', {})
        position_coords = company_data.get('position_coords', [0, 0])
        
        # Получаем название и эмодзи типа клетки
        cell_name = get_resource_name(cell_type)
        cell_emoji = get_resource_emoji(cell_type)
        
        # Преобразуем координаты в буквенный формат
        cell_position = xy_into_cell(position_coords[0], position_coords[1])
        
        # Получаем ресурс клетки (если есть)
        resource_id = cell_info.get('resource_id')
        resource_text = ""
        if resource_id:
            resource_name = get_resource_name(resource_id)
            resource_emoji = get_resource_emoji(resource_id)
            resource_text = f"\n*Ресурс:* {resource_name}"
        
        # Формируем текст
        text = f"""📍 *Информация о клетке*

*Тип клетки:* {cell_name}
*Расположение:* {cell_position}{resource_text}"""
        
        return text
