from oms import Page
from aiogram.types import Message, CallbackQuery
from modules.ws_client import company_complete_free_factories
from oms.utils import callback_generator


class FactoryRekitResource(Page):
    __page_name__ = "factory-rekit-resource-page"
    
    # Маппинг ресурсов с эмодзи (только производные, без сырья)
    AVAILABLE_RESOURCES = {
        # Уровень 1
        "oil_p": {"name": "Нефтепродукты", "emoji": "⛽"},
        "nails": {"name": "Гвозди", "emoji": "🔩"},
        "planks": {"name": "Доски", "emoji": "🪵"},
        "fabric": {"name": "Ткань", "emoji": "🧵"},
        # Уровень 2
        "med_eq": {"name": "Медоборудование", "emoji": "💉"},
        "machine": {"name": "Станок", "emoji": "⚙️"},
        "furniture": {"name": "Мебель", "emoji": "🪑"},
        "tent": {"name": "Палатка", "emoji": "⛺"},
        # Уровень 3
        "barrel": {"name": "Бочка", "emoji": "🛢️"},
        "tarp": {"name": "Брезент", "emoji": "🎪"},
        "insulation": {"name": "Изоляция", "emoji": "🧱"},
        "sail": {"name": "Парус", "emoji": "⛵"},
        # Уровень 4
        "generator": {"name": "Генератор", "emoji": "⚡"},
        "armor": {"name": "Бронежилет", "emoji": "🦺"},
        "fridge": {"name": "Холодильник", "emoji": "🧊"},
        "yacht": {"name": "Яхта", "emoji": "🛥️"}
    }
    
    async def content_worker(self):
        """Выбор ресурса для перекомплектации"""
        count_data = self.scene.get_data('factory-rekit-count-page')
        rekit_count = count_data.get('rekit_count', 0)
        
        content = f"🎯 **Выбор ресурса**\n\n"
        content += f"Количество заводов: **{rekit_count}** шт.\n\n"
        content += "Выберите ресурс, на который хотите перекомплектовать заводы:"
        
        return content
    
    async def buttons_worker(self):
        """Кнопки с ресурсами"""
        buttons = []
        
        # Группируем ресурсы по уровням (убрали базовые ресурсы)
        level1_resources = ["oil_p", "nails", "planks", "fabric"]
        level2_resources = ["med_eq", "machine", "furniture", "tent"]
        level3_resources = ["barrel", "tarp", "insulation", "sail"]
        level4_resources = ["generator", "armor", "fridge", "yacht"]
        
        # Уровень 1
        for res_id in level1_resources:
            res_data = self.AVAILABLE_RESOURCES[res_id]
            buttons.append({
                'text': f"{res_data['emoji']} {res_data['name']}",
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'sel_res',
                    res_id
                )
            })
        
        # Уровень 2
        for res_id in level2_resources:
            res_data = self.AVAILABLE_RESOURCES[res_id]
            buttons.append({
                'text': f"{res_data['emoji']} {res_data['name']}",
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'sel_res',
                    res_id
                )
            })
        
        # Уровень 3
        for res_id in level3_resources:
            res_data = self.AVAILABLE_RESOURCES[res_id]
            buttons.append({
                'text': f"{res_data['emoji']} {res_data['name']}",
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'sel_res',
                    res_id
                )
            })
        
        # Уровень 4
        for res_id in level4_resources:
            res_data = self.AVAILABLE_RESOURCES[res_id]
            buttons.append({
                'text': f"{res_data['emoji']} {res_data['name']}",
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'sel_res',
                    res_id
                )
            })
        
        buttons.append({
            'text': '↪️ Назад',
            'callback_data': callback_generator(
                self.scene.__scene_name__,
                'back'
            )
        })
        
        self.row_width = 2
        return buttons
    
    @Page.on_callback('sel_res')
    async def select_resource(self, callback: CallbackQuery, args: list):
        """Выполнение перекомплектации"""
        if len(args) < 2:
            await callback.answer("❌ Ошибка: ресурс не указан", show_alert=True)
            return
        
        resource_id = args[1]
        
        # Получаем данные о ресурсе
        resource_data = self.AVAILABLE_RESOURCES.get(resource_id)
        if not resource_data:
            await callback.answer("❌ Неизвестный ресурс", show_alert=True)
            return
        
        new_resource = resource_data['name']
        
        # Получаем данные
        scene_data = self.scene.get_data('scene')
        company_id = scene_data.get('company_id')
        
        count_data = self.scene.get_data('factory-rekit-count-page')
        rekit_count = count_data.get('rekit_count', 0)
        factory_ids = count_data.get('factory_ids', [])
        selected_group = count_data.get('selected_group', '')
        
        # Парсим старый ресурс из группы
        parts = selected_group.split('_')
        if len(parts) == 3:
            old_resource = parts[0] if parts[0] != 'Простой' else None
        else:
            old_resource = None
        
        # Выполняем перекомплектацию через API
        try:
            response = await company_complete_free_factories(
                company_id=company_id,
                find_resource=old_resource,
                new_resource=new_resource,
                count=rekit_count,
                produce_status=True
            )
            
            # Проверяем ответ: может быть None, dict с result, или dict с error
            if response is None:
                # API не вернул ответ, но запрос мог пройти
                await callback.answer(
                    f"⚠️ Запрос отправлен: {rekit_count} заводов → {new_resource}",
                    show_alert=True
                )
                await self.scene.update_page('factory-menu')
            elif isinstance(response, dict):
                if response.get('result') == True or response.get('success') == True:
                    await callback.answer(
                        f"✅ Перекомплектовано {rekit_count} заводов на {new_resource}",
                        show_alert=True
                    )
                    await self.scene.update_page('factory-menu')
                elif 'error' in response:
                    await callback.answer(f"❌ {response['error']}", show_alert=True)
                else:
                    # Непонятный ответ, но считаем успехом
                    await callback.answer(
                        f"✅ Запрос выполнен: {rekit_count} заводов → {new_resource}",
                        show_alert=True
                    )
                    await self.scene.update_page('factory-menu')
            else:
                # Странный формат ответа
                await callback.answer(
                    f"⚠️ Запрос отправлен: {rekit_count} заводов → {new_resource}",
                    show_alert=True
                )
                await self.scene.update_page('factory-menu')
                
        except Exception as e:
            await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)
    
    @Page.on_callback('back')
    async def back_to_count(self, callback: CallbackQuery, args: list):
        """Вернуться к вводу количества"""
        await self.scene.update_page('factory-rekit-count-page')
        await callback.answer()
