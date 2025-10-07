from oms import Page
from aiogram.types import Message, CallbackQuery
from modules.ws_client import company_complete_free_factories
from oms.utils import callback_generator


class FactoryRekitResource(Page):
    __page_name__ = "factory-rekit-resource-page"
    
    # Список доступных ресурсов для производства с короткими ID
    AVAILABLE_RESOURCES = {
        "oil": "Нефть",
        "metal": "Металл", 
        "wood": "Дерево",
        "cotton": "Хлопок",
        "oil_p": "Нефтепродукты",
        "nails": "Гвозди",
        "planks": "Доски",
        "fabric": "Ткань",
        "med_eq": "Медицинское оборудование",
        "machine": "Станок",
        "furniture": "Мебель",
        "tent": "Палатка",
        "barrel": "Бочка",
        "tarp": "Брезент",
        "insulation": "Изоляционный материал",
        "sail": "Парус",
        "generator": "Генератор",
        "armor": "Бронежилет",
        "fridge": "Холодильник",
        "yacht": "Парусная яхта"
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
        
        # Группируем ресурсы по уровням
        basic_resources = [("oil", "Нефть"), ("metal", "Металл"), ("wood", "Дерево"), ("cotton", "Хлопок")]
        level1_resources = [("oil_p", "Нефтепродукты"), ("nails", "Гвозди"), ("planks", "Доски"), ("fabric", "Ткань")]
        level2_resources = [("med_eq", "Медоборудование"), ("machine", "Станок"), ("furniture", "Мебель"), ("tent", "Палатка")]
        level3_resources = [("barrel", "Бочка"), ("tarp", "Брезент"), ("insulation", "Изоляция"), ("sail", "Парус")]
        level4_resources = [("generator", "Генератор"), ("armor", "Бронежилет"), ("fridge", "Холодильник"), ("yacht", "Яхта")]
        
        # Базовые ресурсы
        for res_id, res_name in basic_resources:
            buttons.append({
                'text': f"⚪️ {res_name}",
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'sel_res',
                    res_id
                )
            })
        
        # Уровень 1
        for res_id, res_name in level1_resources:
            buttons.append({
                'text': f"🟢 {res_name}",
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'sel_res',
                    res_id
                )
            })
        
        # Уровень 2
        for res_id, res_name in level2_resources:
            buttons.append({
                'text': f"🟡 {res_name}",
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'sel_res',
                    res_id
                )
            })
        
        # Уровень 3
        for res_id, res_name in level3_resources:
            buttons.append({
                'text': f"🟠 {res_name}",
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'sel_res',
                    res_id
                )
            })
        
        # Уровень 4
        for res_id, res_name in level4_resources:
            buttons.append({
                'text': f"🔴 {res_name}",
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
        
        # Получаем полное название ресурса
        new_resource = self.AVAILABLE_RESOURCES.get(resource_id, resource_id)
        
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
                produce_status=True  # Включаем производство после перекомплектации
            )
            
            if response and response.get('result'):
                await callback.answer(
                    f"✅ Перекомплектовано {rekit_count} заводов на {new_resource}",
                    show_alert=True
                )
                # Возвращаемся в меню заводов
                await self.scene.update_page('factory-menu')
            else:
                error_msg = response.get('error', 'Неизвестная ошибка') if response else 'Нет ответа от сервера'
                await callback.answer(f"❌ Ошибка: {error_msg}", show_alert=True)
        except Exception as e:
            await callback.answer(f"❌ Ошибка при перекомплектации: {str(e)}", show_alert=True)
    
    @Page.on_callback('back')
    async def back_to_count(self, callback: CallbackQuery, args: list):
        """Вернуться к вводу количества"""
        await self.scene.update_page('factory-rekit-count-page')
        await callback.answer()
