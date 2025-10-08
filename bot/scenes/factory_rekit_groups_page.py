from oms import Page
from aiogram.types import Message, CallbackQuery
from modules.ws_client import get_factories
from oms.utils import callback_generator


class FactoryRekitGroups(Page):
    __page_name__ = "factory-rekit-groups-page"
    
    async def content_worker(self):
        """Показать группы заводов по статусу"""
        scene_data = self.scene.get_data('scene')
        company_id = scene_data.get('company_id')
        
        if not company_id:
            return "❌ Ошибка: компания не найдена"
        
        # Получаем список фабрик компании
        factories_response = await get_factories(company_id=company_id)
        
        if not factories_response or "factories" not in factories_response:
            return "❌ Не удалось загрузить список заводов"
        
        factories = factories_response["factories"]
        
        # Группируем заводы
        groups = {}  # {f"{resource}_{is_auto}_{is_producing}": [factory_ids]}
        
        for factory in factories:
            factory_id = factory.get('id')
            complectation = factory.get('complectation', 'None')
            is_auto = factory.get('is_auto', False)
            is_producing = factory.get('is_produce', False)
            
            # Определяем статус и создаем строковый ключ
            if not complectation or complectation == 'None':
                resource = 'Простой'
                status_key = f"{resource}_{False}_{False}"
            elif is_producing and is_auto:
                status_key = f"{complectation}_{True}_{True}"
            elif is_producing and not is_auto:
                status_key = f"{complectation}_{False}_{True}"
            else:
                status_key = f"{complectation}_{False}_{False}"
            
            if status_key not in groups:
                groups[status_key] = []
            groups[status_key].append(factory_id)
        
        # Сохраняем группы в данные страницы
        await self.update_data('factory_groups', groups)
        
        content = "🔄 **Перекомплектация заводов**\n\n"
        content += "Выберите группу заводов для перекомплектации:\n\n"
        
        for status_key, factory_ids in groups.items():
            # Парсим ключ обратно
            parts = status_key.split('_')
            if len(parts) == 3:
                resource = parts[0]
                is_auto = parts[1] == 'True'
                is_producing = parts[2] == 'True'
                
                count = len(factory_ids)
                if resource == 'Простой':
                    content += f"⚪️ **Простаивает:** {count} шт.\n"
                elif is_auto:
                    content += f"🔄 **{resource} (авто):** {count} шт.\n"
                elif is_producing:
                    content += f"⏸️ **{resource} (разово):** {count} шт.\n"
                else:
                    content += f"⏹️ **{resource} (остановлен):** {count} шт.\n"
        
        return content
    
    async def buttons_worker(self):
        """Кнопки групп заводов"""
        page_data = self.get_data()
        factory_groups = page_data.get('factory_groups', {})
        
        buttons = []
        
        for status_key, factory_ids in factory_groups.items():
            # Парсим ключ
            parts = status_key.split('_')
            if len(parts) == 3:
                resource = parts[0]
                is_auto = parts[1] == 'True'
                is_producing = parts[2] == 'True'
                
                count = len(factory_ids)
                
                # Определяем эмодзи и текст
                if resource == 'Простой':
                    emoji = "⚪️"
                    text = f"{emoji} Простаивает ({count})"
                elif is_auto:
                    emoji = "🔄"
                    text = f"{emoji} {resource} авто ({count})"
                elif is_producing:
                    emoji = "⏸️"
                    text = f"{emoji} {resource} разово ({count})"
                else:
                    emoji = "⏹️"
                    text = f"{emoji} {resource} остановлен ({count})"
                
                buttons.append({
                    'text': text,
                    'callback_data': callback_generator(
                        self.scene.__scene_name__,
                        'select_group',
                        status_key
                    )
                })
        
        buttons.append({
            'text': '↪️ Назад',
            'callback_data': callback_generator(
                self.scene.__scene_name__,
                'back_to_factory'
            )
        })
        
        self.row_width = 1
        return buttons
    
    @Page.on_callback('select_group')
    async def select_group(self, callback: CallbackQuery, args: list):
        """Выбор группы для перекомплектации"""
        if len(args) < 2:
            await callback.answer("❌ Ошибка: группа не указана", show_alert=True)
            return
        
        group_key = args[1]
        
        # Сохраняем выбранную группу
        await self.update_data('selected_group', group_key)
        
        # Переходим к вводу количества
        await self.scene.update_page('factory-rekit-count-page')
        await callback.answer()
    
    @Page.on_callback('back_to_factory')
    async def back_to_factory(self, callback: CallbackQuery, args: list):
        """Вернуться к меню заводов"""
        await self.scene.update_page('factory-menu')
        await callback.answer()
