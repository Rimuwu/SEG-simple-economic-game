from oms import Page
from aiogram.types import Message, CallbackQuery
from oms.utils import callback_generator


class FactoryRekitCount(Page):
    __page_name__ = "factory-rekit-count-page"
    
    async def content_worker(self):
        """Запрос количества заводов для перекомплектации"""
        # Получаем данные о выбранной группе
        rekit_groups_data = self.scene.get_data('factory-rekit-groups-page')
        selected_group = rekit_groups_data.get('selected_group', '')
        factory_groups = rekit_groups_data.get('factory_groups', {})
        
        # Получаем заводы для выбранной группы
        factory_ids = factory_groups.get(selected_group, [])
        max_count = len(factory_ids)
        
        # Сохраняем данные
        await self.update_data('max_count', max_count)
        await self.update_data('factory_ids', factory_ids)
        await self.update_data('selected_group', selected_group)
        
        # Парсим ключ группы для отображения
        parts = selected_group.split('_')
        if len(parts) == 3:
            resource = parts[0]
            is_auto = parts[1] == 'True'
            is_producing = parts[2] == 'True'
            
            content = f"🔢 **Количество заводов**\n\n"
            
            if resource == 'Простой':
                content += f"Группа: ⚪️ Простаивающие заводы\n"
            elif is_auto:
                content += f"Группа: 🔄 {resource} (автоматически)\n"
            elif is_producing:
                content += f"Группа: ⏸️ {resource} (разово)\n"
            else:
                content += f"Группа: ⏹️ {resource} (остановлен)\n"
            
            content += f"Доступно заводов: **{max_count}** шт.\n\n"
            content += "Введите количество заводов для перекомплектации:"
            
            return content
        
        return "❌ Ошибка: не удалось определить группу"
    
    @Page.on_text('int')
    async def handle_count(self, message: Message, value: int):
        """Обработка введенного количества"""
        page_data = self.get_data()
        max_count = page_data.get('max_count', 0)
        
        if value <= 0:
            await message.answer("❌ Количество должно быть больше 0")
            return
        
        if value > max_count:
            await message.answer(f"❌ Доступно только {max_count} заводов")
            return
        
        # Сохраняем количество
        await self.update_data('rekit_count', value)
        
        # Переходим к выбору ресурса
        await self.scene.update_page('factory-rekit-resource-page')
    
    @Page.on_text('not_handled')
    async def handle_invalid(self, message: Message):
        """Обработка неверного ввода"""
        await message.answer("❌ Пожалуйста, введите число")
