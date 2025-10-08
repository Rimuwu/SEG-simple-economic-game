from oms import Page
from aiogram.types import Message, CallbackQuery
from modules.ws_client import company_complete_free_factories
from oms.utils import callback_generator
from global_modules.logs import Logger

bot_logger = Logger.get_logger("bot")


class FactoryRekitResource(Page):
    __page_name__ = "factory-rekit-resource"
    
        # Маппинг ресурсов с английского на русский с эмодзи
    RESOURCES = {
        "oil_products": {"name": "Нефтепродукты", "emoji": "⛽"},
        "nails": {"name": "Гвозди", "emoji": "🔩"},
        "boards": {"name": "Доски", "emoji": "🪵"},
        "fabric": {"name": "Ткань", "emoji": "🧵"},
        "medical_equipment": {"name": "Медицинское оборудование", "emoji": "💉"},
        "machine": {"name": "Станок", "emoji": "⚙️"},
        "furniture": {"name": "Мебель", "emoji": "🪑"},
        "tent": {"name": "Палатка", "emoji": "⛺"},
        "barrel": {"name": "Бочка", "emoji": "🛢️"},
        "tarpaulin": {"name": "Брезент", "emoji": "🎪"},
        "insulation_material": {"name": "Изоляционный материал", "emoji": "🧱"},
        "sail": {"name": "Парус", "emoji": "⛵"},
        "generator": {"name": "Генератор", "emoji": "⚡"},
        "body_armor": {"name": "Бронежилет", "emoji": "🦺"},
        "refrigerator": {"name": "Холодильник", "emoji": "🧊"},
        "yacht": {"name": "Парусная яхта", "emoji": "🛥️"}
    }
    
    async def content_worker(self):
        """Показать список ресурсов для перекомплектации"""
        scene_data = self.scene.get_data('scene')
        group_type = scene_data.get('rekit_group')
        count_str = scene_data.get('rekit_count')
        
        if not group_type or not count_str:
            return "❌ Ошибка: данные о перекомплектации не найдены"
        
        # Формируем текст
        if group_type == 'idle':
            group_name = "⚪️ Простаивающие заводы"
        else:
            resource_info = self.RESOURCES.get(group_type, {"name": group_type, "emoji": "📦"})
            group_name = f"{resource_info['emoji']} {resource_info['name']}"
        
        count_display = "все" if count_str == "all" else count_str
        
        content = "🔄 **Перекомплектация заводов**\n\n"
        content += f"Группа: {group_name}\n"
        content += f"Количество: **{count_display}**\n\n"
        content += "Выберите ресурс для перекомплектации:"
        
        return content
    
    async def buttons_worker(self):
        """Кнопки с доступными ресурсами"""
        buttons = []
        
        # Добавляем кнопки для всех доступных ресурсов
        for resource_key, resource_info in self.RESOURCES.items():
            buttons.append({
                'text': f'{resource_info["emoji"]} {resource_info["name"]}',
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'rekit',
                    resource_key
                )
            })
        
        # Кнопка назад
        buttons.append({
            'text': '↪️ Назад',
            'callback_data': callback_generator(
                self.scene.__scene_name__,
                'back'
            )
        })
        
        self.row_width = 2
        return buttons
    
    @Page.on_callback('rekit')
    async def do_rekit(self, callback: CallbackQuery, args: list):
        """Выполнить перекомплектацию"""
        if len(args) < 2:
            await callback.answer("❌ Ошибка: ресурс не указан", show_alert=True)
            return
        
        new_resource = args[1]
        
        # Получаем данные из scene
        scene_data = self.scene.get_data('scene')
        company_id = scene_data.get('company_id')
        group_type = scene_data.get('rekit_group')
        count_str = scene_data.get('rekit_count')
        
        if not company_id or not group_type or not count_str:
            await callback.answer("❌ Ошибка: недостаточно данных", show_alert=True)
            return
        
        # Определяем find_resource (откуда берём заводы)
        find_resource = None if group_type == 'idle' else group_type
        
        # Определяем количество
        count = None if count_str == 'all' else int(count_str)
        
        bot_logger.info(f"Перекомплектация: company_id={company_id}, find_resource={find_resource}, new_resource={new_resource}, count={count}")
        
        try:
            # Вызываем API
            response = await company_complete_free_factories(
                company_id=company_id,
                find_resource=find_resource,
                new_resource=new_resource,
                count=count,
                produce_status=False  # Разовое производство
            )
            
            bot_logger.info(f"API response: {response}")
            
            # Проверяем ответ
            if response and isinstance(response, dict) and "error" in response:
                await callback.answer(f"❌ {response['error']}", show_alert=True)
            else:
                # Успех - показываем сообщение
                resource_info = self.RESOURCES.get(new_resource, {"name": new_resource, "emoji": "📦"})
                count_display = "все" if count_str == "all" else count_str
                
                await callback.answer(
                    f"✅ Перекомплектовано {count_display} заводов на {resource_info['emoji']} {resource_info['name']}!",
                    show_alert=True
                )
                
                # Очищаем временные данные
                scene_data.pop('rekit_group', None)
                scene_data.pop('rekit_count', None)
                await self.scene.set_data('scene', scene_data)
                
                # Возвращаемся в меню заводов
                await self.scene.update_page('factory-menu')
                
        except Exception as e:
            bot_logger.error(f"Ошибка при перекомплектации: {e}")
            await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)
    
    @Page.on_callback('back')
    async def back_to_count(self, callback: CallbackQuery, args: list):
        """Возврат к вводу количества"""
        await self.scene.update_page('factory-rekit-count')
        await callback.answer()
