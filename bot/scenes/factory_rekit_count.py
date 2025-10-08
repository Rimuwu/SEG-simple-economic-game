from oms import Page
from aiogram.types import Message, CallbackQuery
from oms.utils import callback_generator
from global_modules.logs import Logger

bot_logger = Logger.get_logger("bot")


class FactoryRekitCount(Page):
    __page_name__ = "factory-rekit-count"
    
    # Маппинг ресурсов
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
        """Показать запрос количества заводов"""
        scene_data = self.scene.get_data('scene')
        group_type = scene_data.get('rekit_group')
        
        if not group_type:
            return "❌ Ошибка: группа заводов не выбрана"
        
        # Формируем текст в зависимости от выбранной группы
        if group_type == 'idle':
            group_name = "⚪️ Простаивающие заводы"
        else:
            resource_info = self.RESOURCES.get(group_type, {"name": group_type, "emoji": "📦"})
            group_name = f"{resource_info['emoji']} {resource_info['name']}"
        
        content = "🔄 **Перекомплектация заводов**\n\n"
        content += f"Группа: {group_name}\n\n"
        content += "Введите количество заводов для перекомплектации:"
        
        return content
    
    async def buttons_worker(self):
        """Кнопки с быстрым выбором количества"""
        buttons = [
            {
                'text': '↪️ Назад',
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'back'
                )
            }
        ]
        
        self.row_width = 1
        return buttons
    
    @Page.on_text('int')
    async def handle_text_input(self, message: Message, value: int):
        """Обработка текстового ввода количества"""
        if value <= 0:
            await message.answer("❌ Количество должно быть больше 0")
            return
        
        # Сохраняем количество
        scene_data = self.scene.get_data('scene')
        scene_data['rekit_count'] = str(value)
        await self.scene.set_data('scene', scene_data)
        
        # Переходим на страницу выбора ресурса
        await self.scene.update_page('factory-rekit-resource')
    
    @Page.on_callback('back')
    async def back_to_groups(self, callback: CallbackQuery, args: list):
        """Возврат к выбору группы"""
        await self.scene.update_page('factory-rekit-groups')
        await callback.answer()
