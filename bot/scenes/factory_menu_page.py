from oms import Page
from aiogram.types import Message, CallbackQuery
from modules.ws_client import get_factories, get_company_status
from oms.utils import callback_generator


class FactoryMenu(Page):
    __page_name__ = "factory-menu"
    
    async def content_worker(self):
        scene_data = self.scene.get_data('scene')
        company_id = scene_data.get('company_id')
        
        if not company_id:
            return "❌ Ошибка: компания не найдена"
        
        # Получаем список фабрик компании
        factories_response = await get_factories(company_id=company_id)
        
        if not factories_response or "factories" not in factories_response:
            return "❌ Не удалось загрузить список заводов"
        
        factories = factories_response["factories"]
        
        if not factories:
            return "🏭 **Управление заводами**\n\nУ вас пока нет заводов.\nПриобретите их в разделе улучшений."
        
        # Группируем заводы по статусу и ресурсу
        auto_factories = {}  # {resource: count}
        manual_factories = {}  # {resource: count}
        idle_factories = 0
        
        for factory in factories:
            complectation = factory.get('complectation')
            is_auto = factory.get('is_auto', False)
            is_producing = factory.get('is_produce', False)
            
            if not complectation or complectation == 'None':
                idle_factories += 1
            elif is_producing and is_auto:
                auto_factories[complectation] = auto_factories.get(complectation, 0) + 1
            elif is_producing and not is_auto:
                manual_factories[complectation] = manual_factories.get(complectation, 0) + 1
            else:
                idle_factories += 1
        
        # Формируем текст
        content = f"🏭 **Управление заводами**\n\n"
        content += f"📊 **Всего заводов:** {len(factories)}\n\n"
        
        if auto_factories:
            content += "🔄 **Автоматическое производство:**\n"
            for resource, count in auto_factories.items():
                content += f"  • {resource}: {count} шт.\n"
            content += "\n"
        
        if manual_factories:
            content += "⏸️ **Разовое производство:**\n"
            for resource, count in manual_factories.items():
                content += f"  • {resource}: {count} шт.\n"
            content += "\n"
        
        if idle_factories > 0:
            content += f"⚪️ **Простаивает:** {idle_factories} шт.\n\n"
        
        content += "Выберите действие:"
        
        return content
    
    async def buttons_worker(self):
        buttons = [
            {
                'text': '🔄 Перекомплектовать',
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'rekit_menu'
                )
            },
            {
                'text': '🛒 Купить заводы',
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'buy_factories'
                )
            }
        ]
        
        self.row_width = 1
        return buttons
    
    @Page.on_callback('rekit_menu')
    async def show_rekit_menu(self, callback: CallbackQuery, args: list):
        """Показать меню перекомплектации с группами заводов"""
        await self.scene.update_page('factory-rekit-groups-page')
        await callback.answer()
    
    @Page.on_callback('buy_factories')
    async def show_buy_menu(self, callback: CallbackQuery, args: list):
        """Показать меню покупки заводов"""
        await callback.answer("🚧 Функция в разработке", show_alert=True)



