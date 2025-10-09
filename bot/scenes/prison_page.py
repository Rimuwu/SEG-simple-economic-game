from oms import Page
from aiogram.types import CallbackQuery
from modules.ws_client import get_company
from oms.utils import callback_generator
from global_modules.logs import Logger

bot_logger = Logger.get_logger("bot")


class PrisonPage(Page):
    __page_name__ = "prison-page"
    
    async def content_worker(self):
        """Показать информацию о заключении компании"""
        scene_data = self.scene.get_data('scene')
        company_id = scene_data.get('company_id')
        
        if not company_id:
            return "❌ Ошибка: компания не найдена"
        
        try:
            # Получаем данные компании
            company_data = await get_company(id=company_id)
            bot_logger.info(f"get_company response for prison: {company_data}")
            
            if isinstance(company_data, str):
                return f"❌ Ошибка при получении данных: {company_data}"
            
            
            # Получаем информацию о задолженности
            balance = company_data.get('balance', 0)
            company_name = company_data.get('name', 'Компания')
            
            # Формируем текст
            content = "🔒 **ТЮРЬМА**\n\n"
            content += f"Компания: *{company_name}*\n\n"
            
            content += "❌ Ваша компания находится в тюрьме!\n\n"
            
            # Информация о задолженности
            content += f"💰 Текущий баланс: {balance:,} 💰\n\n".replace(",", " ")
            
            # Информация о сроке заключения
            # В конфигурации настроек обычно есть параметр prison_duration
            # Предположим, что это 3 хода (можно будет уточнить из settings)
            from global_modules.load_config import ALL_CONFIGS
            settings = ALL_CONFIGS.get('settings')
            
            # Примерный срок - 3 хода (если не указано иначе в настройках)
            prison_duration = 3
            if settings:
                # Пытаемся получить длительность тюрьмы из настроек
                prison_duration = getattr(settings, 'prison_duration', 3)
            
            content += f"⛓ **Срок заключения:** {prison_duration} ход(ов)\n\n"
            
            content += "📋 **Последствия заключения:**\n"
            content += "• Компания не может производить ресурсы\n"
            content += "• Заводы простаивают\n"
            content += "• Невозможно совершать сделки\n"
            content += "• Налоги продолжают начисляться\n\n"
            
            content += "💡 **Как избежать тюрьмы в будущем:**\n"
            content += "• Вовремя оплачивайте налоги\n"
            content += "• Следите за балансом компании\n"
            content += "• Планируйте расходы заранее\n\n"
            
            content += f"⏳ Освобождение через: *{prison_duration}* ход(ов)"
            
            return content
            
        except Exception as e:
            bot_logger.error(f"Ошибка при получении информации о тюрьме: {e}")
            return f"❌ Ошибка при загрузке данных: {str(e)}"
    
    async def buttons_worker(self):
        """Кнопки на странице тюрьмы"""
        buttons = [
            {
                'text': '📊 Обновить информацию',
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'refresh'
                )
            },
            {
                'text': '↪️ Вернуться в меню',
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'back'
                )
            }
        ]
        
        self.row_width = 1
        return buttons
    
    @Page.on_callback('refresh')
    async def refresh_info(self, callback: CallbackQuery, args: list):
        """Обновить информацию на странице"""
        await self.scene.update_message()
        await callback.answer("🔄 Информация обновлена")
    
    @Page.on_callback('back')
    async def back_to_menu(self, callback: CallbackQuery, args: list):
        """Возврат в главное меню"""
        await self.scene.update_page('main-page')
        await callback.answer()
