from oms import Page
from aiogram.types import CallbackQuery
from oms.utils import callback_generator
from global_modules.logs import Logger
from modules.ws_client import company_complete_free_factories, get_factories, factory_set_auto
from modules.resources import RESOURCES

bot_logger = Logger.get_logger("bot")


class FactoryRekitProduce(Page):
    __page_name__ = "factory-rekit-produce"
    
    async def content_worker(self):
        """Показать выбор типа производства"""
        scene_data = self.scene.get_data('scene')
        
        group_type = scene_data.get('rekit_group')
        count = scene_data.get('rekit_count')
        resource = scene_data.get('rekit_resource')
        
        if not all([group_type, count, resource]):
            return "❌ Ошибка: недостаточно данных для перекомплектации"
        
        # Формируем текст
        resource_info = RESOURCES.get(resource, {"name": resource, "emoji": "📦"})
        
        content = "🔄 **Перекомплектация заводов**\n\n"
        content += f"Ресурс: {resource_info['emoji']} {resource_info['name']}\n"
        content += f"Количество: {count}\n\n"
        content += "Выберите режим производства:\n\n"
        content += "🔄 **Автоматическое** - завод будет производить ресурс каждый ход автоматически\n\n"
        content += "🎯 **Разовое** - завод будет ждать команды на производство"
        
        return content
    
    async def buttons_worker(self):
        """Кнопки выбора режима производства"""
        buttons = [
            {
                'text': '🔄 Автоматическое',
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'produce_auto'
                )
            },
            {
                'text': '🎯 Разовое',
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'produce_manual'
                )
            },
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
    
    @Page.on_callback('produce_auto')
    async def set_auto_produce(self, callback: CallbackQuery, args: list):
        """Установить автоматическое производство"""
        await self._complete_recomplectation(callback, produce_status=True)
    
    @Page.on_callback('produce_manual')
    async def set_manual_produce(self, callback: CallbackQuery, args: list):
        """Установить разовое производство"""
        await self._complete_recomplectation(callback, produce_status=False)
    
    async def _complete_recomplectation(self, callback: CallbackQuery, produce_status: bool):
        """Выполнить перекомплектацию с указанным режимом производства"""
        scene_data = self.scene.get_data('scene')
        
        group_type = scene_data.get('rekit_group')
        count = int(scene_data.get('rekit_count'))
        resource = scene_data.get('rekit_resource')
        company_id = scene_data.get('company_id')
        
        if not company_id:
            await callback.answer("❌ Ошибка: ID компании не найден", show_alert=True)
            return
        
        # Определяем find_resource
        find_resource = None if group_type == 'idle' else group_type
        
        bot_logger.info(f"Recomplecting factories: company_id={company_id}, find={find_resource}, new={resource}, count={count}, is_auto={produce_status}")
        
        # Вызываем API для перекомплектации (ВСЕГДА с produce_status=False для поиска свободных заводов)
        result = await company_complete_free_factories(
            company_id=company_id,
            new_resource=resource,
            count=count,
            find_resource=find_resource,
            produce_status=False  # Ищем свободные заводы (produce=False)
        )
        
        bot_logger.info(f"API response: {result}")
        
        # Проверяем результат
        if isinstance(result, dict) and result.get('success'):
            # Теперь устанавливаем is_auto на перекомплектованные заводы
            if produce_status:  # Если выбрано автоматическое производство
                factories_response = await get_factories(company_id=company_id)
                if factories_response and isinstance(factories_response, dict) and "factories" in factories_response:
                    factories = factories_response["factories"]
                    # Находим заводы с нужной комплектацией и устанавливаем is_auto
                    for factory in factories:
                        if factory.get('complectation') == resource and not factory.get('is_auto'):
                            await factory_set_auto(factory['id'], True)
                            bot_logger.info(f"Set auto=True for factory {factory['id']}")
            
            resource_info = RESOURCES.get(resource, {"name": resource, "emoji": "📦"})
            mode_text = "🔄 Автоматическое" if produce_status else "🎯 Разовое"
            
            # Очищаем временные данные
            scene_data.pop('rekit_group', None)
            scene_data.pop('rekit_count', None)
            scene_data.pop('rekit_resource', None)
            await self.scene.set_data('scene', scene_data)
            
            # Обновляем сообщение вместо отправки нового
            await callback.message.edit_text(
                f"✅ Перекомплектовано {count} заводов на {resource_info['emoji']} {resource_info['name']}!\n"
                f"Режим производства: {mode_text}"
            )
            
            # Возвращаемся в меню заводов
            await self.scene.update_page('factory-menu')
        else:
            error_msg = result.get('error', 'Неизвестная ошибка') if isinstance(result, dict) else 'Ошибка API'
            await callback.answer(f"❌ Ошибка: {error_msg}", show_alert=True)
        
        await callback.answer()
    
    @Page.on_callback('back')
    async def back_to_resource(self, callback: CallbackQuery, args: list):
        """Возврат к выбору ресурса"""
        await self.scene.update_page('factory-rekit-resource')
        await callback.answer()
