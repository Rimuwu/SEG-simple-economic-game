from oms import Page
from aiogram.types import CallbackQuery, Message
from modules.ws_client import (
    get_company, get_company_contracts, create_contract, 
    accept_contract, decline_contract, execute_contract
)
from oms.utils import callback_generator
from global_modules.load_config import ALL_CONFIGS
from global_modules.logs import Logger

bot_logger = Logger.get_logger("bot")

class ContractPage(Page):
    
    __page_name__ = "contract-page"
    
    async def content_worker(self):
        """Генерация контента страницы"""
        scene_data = self.scene.get_data('scene')
        company_id = scene_data.get('company_id')
        session_id = scene_data.get('session')
        
        if not company_id:
            return "❌ Ошибка: компания не найдена"
        
        # Получаем данные компании
        company_response = await get_company(id=company_id)
        
        if company_response is None or isinstance(company_response, str):
            return "❌ Ошибка при получении данных компании"
        
        # Получаем состояние страницы
        contract_state = scene_data.get('contract_state', 'main')
        
        # Основной экран со списком контрактов
        if contract_state == 'main':
            return await self._main_screen(company_id)
        
        # Выбор роли при создании контракта
        elif contract_state == 'select_role':
            return await self._select_role_screen()
        
        # Выбор партнёра
        elif contract_state == 'select_partner':
            return await self._select_partner_screen(session_id, company_id)
        
        # Выбор ресурса
        elif contract_state == 'select_resource':
            return await self._select_resource_screen(company_id, scene_data)
        
        # Ввод количества за ход
        elif contract_state == 'input_amount':
            return await self._input_amount_screen(scene_data)
        
        # Ввод длительности
        elif contract_state == 'input_duration':
            return await self._input_duration_screen(scene_data)
        
        # Ввод суммы оплаты
        elif contract_state == 'input_payment':
            return await self._input_payment_screen(scene_data)
        
        # Подтверждение создания
        elif contract_state == 'confirm':
            return await self._confirm_screen(scene_data)
        
        # Просмотр входящих контрактов
        elif contract_state == 'view_incoming':
            return await self._view_incoming_screen(company_id)
        
        # Просмотр отправленных контрактов
        elif contract_state == 'view_outgoing':
            return await self._view_outgoing_screen(company_id)
        
        # Просмотр активных контрактов
        elif contract_state == 'view_active':
            return await self._view_active_screen(company_id)
        
        # Детали контракта
        elif contract_state == 'contract_details':
            return await self._contract_details_screen(scene_data)
        
        return "❌ Неизвестное состояние"
    
    async def _main_screen(self, company_id: int):
        """Главный экран контрактов"""
        scene_data = self.scene.get_data('scene')
        success_message = scene_data.get('success_message', '')
        
        text = "📋 **Контракты**\n\n"
        
        if success_message:
            text += f"✅ {success_message}\n\n"
            await self.scene.update_key('scene', 'success_message', '')
        
        # Получаем все контракты компании
        contracts_response = await get_company_contracts(
            company_id=company_id,
            as_supplier=True,
            as_customer=True
        )
        
        if contracts_response is None:
            text += "⚠️ Ошибка при загрузке контрактов\n\n"
        else:
            contracts = contracts_response if isinstance(contracts_response, list) else []
            
            # Подсчитываем контракты
            incoming_count = len([c for c in contracts if c.get('customer_company_id') == company_id and not c.get('accepted')])
            outgoing_count = len([c for c in contracts if c.get('supplier_company_id') == company_id and not c.get('accepted')])
            active_count = len([c for c in contracts if c.get('accepted')])
            
            text += f"📥 Входящие предложения: {incoming_count}\n"
            text += f"📤 Отправленные предложения: {outgoing_count}\n"
            text += f"✅ Активные контракты: {active_count}\n\n"
        
        text += "Выберите действие:"
        
        return text
    
    async def _select_role_screen(self):
        """Экран выбора роли в контракте"""
        text = "📝 **Создание контракта**\n\n"
        text += "Выберите, кем вы хотите выступить:\n\n"
        text += "**🛒 Я покупаю ресурс** - вы платите деньги и получаете ресурс\n\n"
        text += "**💰 Я продаю ресурс** - вы поставляете ресурс и получаете деньги"
        
        return text
    
    async def _select_partner_screen(self, session_id: str, company_id: int):
        """Экран выбора партнёра"""
        from modules.ws_client import get_companies
        
        scene_data = self.scene.get_data('scene')
        role = scene_data.get('contract_role', '')
        
        # Получаем список всех компаний в сессии
        companies_response = await get_companies(session_id=session_id)
        
        if companies_response is None or not isinstance(companies_response, list):
            return "❌ Ошибка при получении списка компаний"
        
        # Фильтруем свою компанию
        other_companies = [c for c in companies_response if c.get('id') != company_id]
        
        if not other_companies:
            return "❌ Нет доступных компаний для контракта"
        
        role_text = "покупаете у" if role == 'customer' else "продаёте"
        
        text = f"👥 **Выбор партнёра**\n\n"
        text += f"Вы {role_text}:\n\n"
        
        # Сохраняем список компаний для кнопок
        await self.scene.update_key('scene', 'available_companies', other_companies)
        
        return text
    
    async def _select_resource_screen(self, company_id: int, scene_data: dict):
        """Экран выбора ресурса"""
        role = scene_data.get('contract_role', '')
        
        # Получаем список ресурсов из конфига
        resources_config = ALL_CONFIGS.get('resources')
        
        if not resources_config or not hasattr(resources_config, 'resources'):
            return "❌ Ошибка загрузки конфигурации ресурсов"
        
        available_resources = []
        
        if role == 'supplier':
            # Если я поставщик - показываем только ресурсы с моего склада
            company_response = await get_company(id=company_id)
            
            if company_response is None:
                return "❌ Ошибка при получении данных компании"
            
            warehouse = company_response.get('warehouse', {})
            
            # Фильтруем ресурсы, которые есть на складе
            for resource_key, resource_obj in resources_config.resources.items():
                quantity = warehouse.get(resource_key, 0)
                if quantity > 0:
                    available_resources.append({
                        'key': resource_key,
                        'name': resource_obj.label,
                        'emoji': resource_obj.emoji,
                        'quantity': quantity
                    })
            
            if not available_resources:
                return "❌ На вашем складе нет доступных ресурсов для контракта"
        else:
            # Если я покупатель - показываем все ресурсы из конфига
            for resource_key, resource_obj in resources_config.resources.items():
                available_resources.append({
                    'key': resource_key,
                    'name': resource_obj.label,
                    'emoji': resource_obj.emoji,
                    'quantity': None  # Для покупателя количество не важно
                })
        
        role_text = "продаёте" if role == 'supplier' else "покупаете"
        
        text = f"📦 **Выбор ресурса**\n\n"
        text += f"Вы {role_text}. Доступные ресурсы:\n\n"
        
        # Сохраняем список ресурсов для кнопок
        await self.scene.update_key('scene', 'available_resources', available_resources)
        
        return text
    
    async def _input_amount_screen(self, scene_data: dict):
        """Экран ввода количества за ход"""
        resource_key = scene_data.get('contract_resource', '')
        error = scene_data.get('error_message', '')
        
        # Получаем название ресурса
        resources_config = ALL_CONFIGS.get('resources')
        resource_name = resource_key
        
        if resources_config and hasattr(resources_config, 'resources'):
            resource_obj = resources_config.resources.get(resource_key)
            if resource_obj:
                resource_name = resource_obj.label
        
        text = f"📊 **Количество за ход**\n\n"
        text += f"Ресурс: {resource_name}\n\n"
        text += "Введите количество ресурса, которое будет поставляться каждый ход:\n\n"
        text += "Минимум: 1 единица"
        
        if error:
            text += f"\n\n❌ {error}"
        
        return text
    
    async def _input_duration_screen(self, scene_data: dict):
        """Экран ввода длительности контракта"""
        amount = scene_data.get('contract_amount', 0)
        error = scene_data.get('error_message', '')
        
        text = f"⏱ **Длительность контракта**\n\n"
        text += f"Количество за ход: {amount}\n\n"
        text += "Введите длительность контракта в ходах:\n\n"
        text += "Минимум: 1 ход\n"
        text += "Максимум: 10 ходов"
        
        if error:
            text += f"\n\n❌ {error}"
        
        return text
    
    async def _input_payment_screen(self, scene_data: dict):
        """Экран ввода суммы оплаты"""
        amount = scene_data.get('contract_amount', 0)
        duration = scene_data.get('contract_duration', 0)
        resource_key = scene_data.get('contract_resource', '')
        error = scene_data.get('error_message', '')
        
        # Получаем название ресурса
        resources_config = ALL_CONFIGS.get('resources')
        resource_name = resource_key
        
        if resources_config and hasattr(resources_config, 'resources'):
            resource_obj = resources_config.resources.get(resource_key)
            if resource_obj:
                resource_name = resource_obj.label
        
        total_amount = amount * duration
        
        text = f"💰 **Сумма оплаты**\n\n"
        text += f"Ресурс: {resource_name}\n"
        text += f"За ход: {amount} единиц\n"
        text += f"Длительность: {duration} ходов\n"
        text += f"Всего ресурсов: {total_amount}\n\n"
        text += "Введите общую сумму оплаты за весь контракт:\n\n"
        text += "Минимум: 1 💰"
        
        if error:
            text += f"\n\n❌ {error}"
        
        return text
    
    async def _confirm_screen(self, scene_data: dict):
        """Экран подтверждения контракта"""
        role = scene_data.get('contract_role', '')
        partner_name = scene_data.get('contract_partner_name', '')
        resource_key = scene_data.get('contract_resource', '')
        amount = scene_data.get('contract_amount', 0)
        duration = scene_data.get('contract_duration', 0)
        payment = scene_data.get('contract_payment', 0)
        
        # Получаем название ресурса
        resources_config = ALL_CONFIGS.get('resources')
        resource_name = resource_key
        resource_emoji = "📦"
        
        if resources_config and hasattr(resources_config, 'resources'):
            resource_obj = resources_config.resources.get(resource_key)
            if resource_obj:
                resource_name = resource_obj.label
                resource_emoji = resource_obj.emoji
        
        total_amount = amount * duration
        price_per_unit = payment / total_amount if total_amount > 0 else 0
        
        text = f"✅ **Подтверждение контракта**\n\n"
        text += f"**Партнёр:** {partner_name}\n\n"
        
        if role == 'supplier':
            text += f"**Вы:** Поставщик (поставляете ресурс)\n"
            text += f"**Партнёр:** Заказчик (оплачивает)\n\n"
        else:
            text += f"**Вы:** Заказчик (оплачиваете)\n"
            text += f"**Партнёр:** Поставщик (поставляет)\n\n"
        
        text += f"**Условия контракта:**\n"
        text += f"   {resource_emoji} Ресурс: {resource_name}\n"
        text += f"   📦 За ход: {amount} единиц\n"
        text += f"   ⏱ Длительность: {duration} ходов\n"
        text += f"   💰 Общая сумма: {payment} 💰\n"
        text += f"   📊 Всего ресурсов: {total_amount} единиц\n"
        text += f"   💵 Цена за единицу: {price_per_unit:.2f} 💰\n\n"
        
        if role == 'customer':
            text += f"⚠️ **Внимание:** С вашего счёта будет списано {payment} 💰 при принятии контракта партнёром."
        
        return text
    
    async def _view_incoming_screen(self, company_id: int):
        """Экран входящих контрактов"""
        contracts_response = await get_company_contracts(
            company_id=company_id,
            as_customer=True,
            as_supplier=False,
            accepted_only=False
        )
        
        if contracts_response is None:
            return "❌ Ошибка при загрузке контрактов"
        
        contracts = [c for c in contracts_response if not c.get('accepted')]
        
        text = "📥 **Входящие предложения**\n\n"
        text += "_Контракты, где вы - заказчик (получаете ресурс)_\n\n"
        
        if not contracts:
            text += "У вас нет входящих предложений."
        else:
            # Сохраняем контракты для кнопок
            await self.scene.update_key('scene', 'viewed_contracts', contracts)
        
        return text
    
    async def _view_outgoing_screen(self, company_id: int):
        """Экран отправленных контрактов"""
        contracts_response = await get_company_contracts(
            company_id=company_id,
            as_supplier=True,
            as_customer=False,
            accepted_only=False
        )
        
        if contracts_response is None:
            return "❌ Ошибка при загрузке контрактов"
        
        contracts = [c for c in contracts_response if not c.get('accepted')]
        
        text = "📤 **Отправленные предложения**\n\n"
        text += "_Контракты, где вы - поставщик (отдаёте ресурс)_\n\n"
        
        if not contracts:
            text += "У вас нет отправленных предложений."
        else:
            # Сохраняем контракты для кнопок
            await self.scene.update_key('scene', 'viewed_contracts', contracts)
        
        return text
    
    async def _view_active_screen(self, company_id: int):
        """Экран активных контрактов"""
        contracts_response = await get_company_contracts(
            company_id=company_id,
            as_supplier=True,
            as_customer=True,
            accepted_only=True
        )
        
        if contracts_response is None:
            return "❌ Ошибка при загрузке контрактов"
        
        contracts = contracts_response if isinstance(contracts_response, list) else []
        
        text = "✅ **Активные контракты**\n\n"
        
        if not contracts:
            text += "У вас нет активных контрактов."
        else:
            # Разделяем на контракты где мы поставщик и где заказчик
            as_supplier = [c for c in contracts if c.get('supplier_company_id') == company_id]
            as_customer = [c for c in contracts if c.get('customer_company_id') == company_id]
            
            if as_supplier:
                text += "📤 **Вы поставляете:**\n"
                for contract in as_supplier:
                    resource = contract.get('resource', '?')
                    amount = contract.get('amount_per_turn', 0)
                    delivered = contract.get('successful_deliveries', 0)
                    duration = contract.get('duration_turns', 0)
                    text += f"   • {resource}: {amount}/ход ({delivered}/{duration} выполнено)\n"
                text += "\n"
            
            if as_customer:
                text += "📥 **Вы получаете:**\n"
                for contract in as_customer:
                    resource = contract.get('resource', '?')
                    amount = contract.get('amount_per_turn', 0)
                    delivered = contract.get('successful_deliveries', 0)
                    duration = contract.get('duration_turns', 0)
                    text += f"   • {resource}: {amount}/ход ({delivered}/{duration} выполнено)\n"
            
            # Сохраняем контракты для кнопок
            await self.scene.update_key('scene', 'viewed_contracts', contracts)
        
        return text
    
    async def _contract_details_screen(self, scene_data: dict):
        """Экран деталей контракта"""
        contract_id = scene_data.get('viewing_contract_id', 0)
        company_id = scene_data.get('company_id')
        
        from modules.ws_client import get_contract
        contract_response = await get_contract(id=contract_id)
        
        if contract_response is None:
            return "❌ Контракт не найден"
        
        # Определяем роль
        is_supplier = contract_response.get('supplier_company_id') == company_id
        is_customer = contract_response.get('customer_company_id') == company_id
        
        supplier_id = contract_response.get('supplier_company_id')
        customer_id = contract_response.get('customer_company_id')
        
        # Получаем имена компаний
        supplier_response = await get_company(id=supplier_id)
        customer_response = await get_company(id=customer_id)
        
        supplier_name = supplier_response.get('name', 'Неизвестно') if supplier_response else 'Неизвестно'
        customer_name = customer_response.get('name', 'Неизвестно') if customer_response else 'Неизвестно'
        
        resource = contract_response.get('resource', '?')
        amount = contract_response.get('amount_per_turn', 0)
        duration = contract_response.get('duration_turns', 0)
        payment = contract_response.get('payment_amount', 0)
        accepted = contract_response.get('accepted', False)
        delivered = contract_response.get('successful_deliveries', 0)
        delivered_this_turn = contract_response.get('delivered_this_turn', False)
        
        # Получаем название ресурса
        resources_config = ALL_CONFIGS.get('resources')
        resource_name = resource
        resource_emoji = "📦"
        
        if resources_config and hasattr(resources_config, 'resources'):
            resource_obj = resources_config.resources.get(resource)
            if resource_obj:
                resource_name = resource_obj.label
                resource_emoji = resource_obj.emoji
        
        text = f"📋 **Детали контракта #{contract_id}**\n\n"
        text += f"**Поставщик:** {supplier_name}\n"
        text += f"**Заказчик:** {customer_name}\n\n"
        
        if is_supplier:
            text += f"**Ваша роль:** Поставщик\n\n"
        elif is_customer:
            text += f"**Ваша роль:** Заказчик\n\n"
        
        text += f"**Условия:**\n"
        text += f"   {resource_emoji} Ресурс: {resource_name}\n"
        text += f"   📦 За ход: {amount} единиц\n"
        text += f"   ⏱ Длительность: {duration} ходов\n"
        text += f"   💰 Сумма: {payment} 💰\n\n"
        
        if accepted:
            text += f"✅ Статус: Активный\n"
            text += f"📊 Выполнено: {delivered}/{duration} ходов\n"
            
            if is_supplier and not delivered_this_turn:
                text += f"\n⚠️ В этом ходу поставка ещё не отправлена!"
            elif is_supplier and delivered_this_turn:
                text += f"\n✅ Поставка в этом ходу отправлена"
        else:
            text += f"⏳ Статус: Ожидает принятия"
        
        # Сохраняем детали контракта
        await self.scene.update_key('scene', 'current_contract', contract_response)
        
        return text
    
    async def buttons_worker(self):
        """Генерация кнопок"""
        scene_data = self.scene.get_data('scene')
        contract_state = scene_data.get('contract_state', 'main')
        
        buttons = []
        
        # Кнопки главного экрана
        if contract_state == 'main':
            buttons.append({
                'text': '➕ Создать контракт',
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'start_create'
                )
            })
            buttons.append({
                'text': '📥 Входящие',
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'view_incoming'
                ),
                'next_line': True
            })
            buttons.append({
                'text': '📤 Отправленные',
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'view_outgoing'
                )
            })
            buttons.append({
                'text': '✅ Активные',
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'view_active'
                ),
                'next_line': True
            })
        
        # Кнопки выбора роли
        elif contract_state == 'select_role':
            buttons.append({
                'text': '🛒 Я покупаю ресурс',
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'set_role',
                    'customer'
                )
            })
            buttons.append({
                'text': '💰 Я продаю ресурс',
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'set_role',
                    'supplier'
                ),
                'next_line': True
            })
            buttons.append({
                'text': '❌ Отмена',
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'cancel_create'
                ),
                'next_line': True
            })
        
        # Кнопки выбора партнёра
        elif contract_state == 'select_partner':
            companies = scene_data.get('available_companies', [])
            for company in companies:
                buttons.append({
                    'text': f"🏢 {company.get('name', 'Неизвестно')}",
                    'callback_data': callback_generator(
                        self.scene.__scene_name__,
                        'select_partner',
                        str(company.get('id', 0)),
                        company.get('name', 'Неизвестно')
                    ),
                    'next_line': True
                })
            buttons.append({
                'text': '◀️ Назад',
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'back_to_role'
                ),
                'next_line': True
            })
        
        # Кнопки выбора ресурса
        elif contract_state == 'select_resource':
            resources = scene_data.get('available_resources', [])
            for resource in resources:
                # Показываем количество только если оно указано (для supplier)
                quantity = resource.get('quantity')
                if quantity is not None:
                    text = f"{resource.get('emoji', '📦')} {resource.get('name', '?')} ({quantity})"
                else:
                    text = f"{resource.get('emoji', '📦')} {resource.get('name', '?')}"
                
                buttons.append({
                    'text': text,
                    'callback_data': callback_generator(
                        self.scene.__scene_name__,
                        'select_resource',
                        resource.get('key', '')
                    ),
                    'next_line': True
                })
            buttons.append({
                'text': '◀️ Назад',
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'back_to_partner'
                ),
                'next_line': True
            })
        
        # Кнопки ввода количества, длительности, оплаты
        elif contract_state in ['input_amount', 'input_duration', 'input_payment']:
            buttons.append({
                'text': '❌ Отмена',
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'cancel_create'
                )
            })
        
        # Кнопки подтверждения
        elif contract_state == 'confirm':
            buttons.append({
                'text': '✅ Подтвердить',
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'confirm_create'
                )
            })
            buttons.append({
                'text': '❌ Отмена',
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'cancel_create'
                ),
                'next_line': True
            })
        
        # Кнопки просмотра контрактов
        elif contract_state in ['view_incoming', 'view_outgoing', 'view_active']:
            contracts = scene_data.get('viewed_contracts', [])
            
            for contract in contracts:
                contract_id = contract.get('id', 0)
                resource = contract.get('resource', '?')
                amount = contract.get('amount_per_turn', 0)
                
                # Получаем emoji ресурса
                resources_config = ALL_CONFIGS.get('resources')
                resource_emoji = "📦"
                if resources_config and hasattr(resources_config, 'resources'):
                    resource_obj = resources_config.resources.get(resource)
                    if resource_obj:
                        resource_emoji = resource_obj.emoji
                
                buttons.append({
                    'text': f"{resource_emoji} {resource} - {amount}/ход",
                    'callback_data': callback_generator(
                        self.scene.__scene_name__,
                        'view_contract',
                        str(contract_id)
                    ),
                    'next_line': True
                })
            
            buttons.append({
                'text': '◀️ Назад',
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'back_to_main'
                ),
                'next_line': True
            })
        
        # Кнопки деталей контракта
        elif contract_state == 'contract_details':
            contract = scene_data.get('current_contract', {})
            company_id = scene_data.get('company_id')
            contract_id = contract.get('id', 0)
            
            is_supplier = contract.get('supplier_company_id') == company_id
            is_customer = contract.get('customer_company_id') == company_id
            accepted = contract.get('accepted', False)
            delivered_this_turn = contract.get('delivered_this_turn', False)
            
            # Кнопки для входящих (мы заказчики)
            if is_customer and not accepted:
                buttons.append({
                    'text': '✅ Принять',
                    'callback_data': callback_generator(
                        self.scene.__scene_name__,
                        'accept_contract',
                        str(contract_id)
                    )
                })
                buttons.append({
                    'text': '❌ Отклонить',
                    'callback_data': callback_generator(
                        self.scene.__scene_name__,
                        'decline_contract',
                        str(contract_id)
                    ),
                    'next_line': True
                })
            
            # Кнопки для отправленных (мы поставщики)
            elif is_supplier and not accepted:
                buttons.append({
                    'text': '❌ Отменить',
                    'callback_data': callback_generator(
                        self.scene.__scene_name__,
                        'decline_contract',
                        str(contract_id)
                    )
                })
            
            # Кнопки для активных (мы поставщики)
            elif is_supplier and accepted and not delivered_this_turn:
                buttons.append({
                    'text': '📦 Отправить поставку',
                    'callback_data': callback_generator(
                        self.scene.__scene_name__,
                        'execute_contract',
                        str(contract_id)
                    )
                })
            
            buttons.append({
                'text': '◀️ Назад',
                'callback_data': callback_generator(
                    self.scene.__scene_name__,
                    'back_from_details'
                ),
                'next_line': True
            })
        
        return buttons
    
    # Обработчики кнопок
    
    @Page.on_callback('start_create')
    async def start_create_handler(self, callback: CallbackQuery, args: list):
        """Начало создания контракта"""
        await self.scene.update_key('scene', 'contract_state', 'select_role')
        await self.scene.update_message()
    
    @Page.on_callback('set_role')
    async def set_role_handler(self, callback: CallbackQuery, args: list):
        """Выбор роли в контракте"""
        if len(args) < 2:
            return
        
        role = args[1]  # 'customer' or 'supplier'
        await self.scene.update_key('scene', 'contract_role', role)
        await self.scene.update_key('scene', 'contract_state', 'select_partner')
        await self.scene.update_message()
    
    @Page.on_callback('select_partner')
    async def select_partner_handler(self, callback: CallbackQuery, args: list):
        """Выбор партнёра"""
        if len(args) < 3:
            return
        
        partner_id = int(args[1])
        partner_name = args[2]
        
        await self.scene.update_key('scene', 'contract_partner_id', partner_id)
        await self.scene.update_key('scene', 'contract_partner_name', partner_name)
        await self.scene.update_key('scene', 'contract_state', 'select_resource')
        await self.scene.update_message()
    
    @Page.on_callback('select_resource')
    async def select_resource_handler(self, callback: CallbackQuery, args: list):
        """Выбор ресурса"""
        if len(args) < 2:
            return
        
        resource_key = args[1]
        await self.scene.update_key('scene', 'contract_resource', resource_key)
        await self.scene.update_key('scene', 'contract_state', 'input_amount')
        await self.scene.update_key('scene', 'error_message', '')
        await self.scene.update_message()
    
    @Page.on_callback('view_incoming')
    async def view_incoming_handler(self, callback: CallbackQuery, args: list):
        """Просмотр входящих контрактов"""
        await self.scene.update_key('scene', 'contract_state', 'view_incoming')
        await self.scene.update_message()
    
    @Page.on_callback('view_outgoing')
    async def view_outgoing_handler(self, callback: CallbackQuery, args: list):
        """Просмотр отправленных контрактов"""
        await self.scene.update_key('scene', 'contract_state', 'view_outgoing')
        await self.scene.update_message()
    
    @Page.on_callback('view_active')
    async def view_active_handler(self, callback: CallbackQuery, args: list):
        """Просмотр активных контрактов"""
        await self.scene.update_key('scene', 'contract_state', 'view_active')
        await self.scene.update_message()
    
    @Page.on_callback('view_contract')
    async def view_contract_handler(self, callback: CallbackQuery, args: list):
        """Просмотр деталей контракта"""
        if len(args) < 2:
            return
        
        contract_id = int(args[1])
        await self.scene.update_key('scene', 'viewing_contract_id', contract_id)
        await self.scene.update_key('scene', 'previous_state', self.scene.get_key('scene', 'contract_state'))
        await self.scene.update_key('scene', 'contract_state', 'contract_details')
        await self.scene.update_message()
    
    @Page.on_callback('accept_contract')
    async def accept_contract_handler(self, callback: CallbackQuery, args: list):
        """Принятие контракта"""
        if len(args) < 2:
            return
        
        contract_id = int(args[1])
        scene_data = self.scene.get_data('scene')
        user_id = self.scene.user_id
        
        result = await accept_contract(contract_id=contract_id, who_accepter=user_id)
        
        if result is not None and result.get('error'):
            await callback.answer(f"❌ {result.get('error')}", show_alert=True)
        else:
            await self.scene.update_key('scene', 'success_message', 'Контракт принят!')
            await self.scene.update_key('scene', 'contract_state', 'main')
            await self.scene.update_message()
    
    @Page.on_callback('decline_contract')
    async def decline_contract_handler(self, callback: CallbackQuery, args: list):
        """Отклонение контракта"""
        if len(args) < 2:
            return
        
        contract_id = int(args[1])
        user_id = self.scene.user_id
        
        result = await decline_contract(contract_id=contract_id, who_decliner=user_id)
        
        if result is not None and result.get('error'):
            await callback.answer(f"❌ {result.get('error')}", show_alert=True)
        else:
            await self.scene.update_key('scene', 'success_message', 'Контракт отклонён')
            await self.scene.update_key('scene', 'contract_state', 'main')
            await self.scene.update_message()
    
    @Page.on_callback('execute_contract')
    async def execute_contract_handler(self, callback: CallbackQuery, args: list):
        """Выполнение поставки по контракту"""
        if len(args) < 2:
            return
        
        contract_id = int(args[1])
        
        result = await execute_contract(contract_id=contract_id)
        
        if result is not None and result.get('error'):
            await callback.answer(f"❌ {result.get('error')}", show_alert=True)
        else:
            await callback.answer("✅ Поставка отправлена!", show_alert=True)
            # Обновляем экран
            await self.scene.update_key('scene', 'contract_state', 'contract_details')
            await self.scene.update_message()
    
    @Page.on_callback('confirm_create')
    async def confirm_create_handler(self, callback: CallbackQuery, args: list):
        """Подтверждение создания контракта"""
        scene_data = self.scene.get_data('scene')
        company_id = scene_data.get('company_id')
        session_id = scene_data.get('session_id')
        
        role = scene_data.get('contract_role', '')
        partner_id = scene_data.get('contract_partner_id', 0)
        resource = scene_data.get('contract_resource', '')
        amount = scene_data.get('contract_amount', 0)
        duration = scene_data.get('contract_duration', 0)
        payment = scene_data.get('contract_payment', 0)
        
        # Определяем supplier и customer
        if role == 'supplier':
            supplier_id = company_id
            customer_id = partner_id
        else:
            supplier_id = partner_id
            customer_id = company_id
        
        # Создаём контракт
        result = await create_contract(
            supplier_company_id=supplier_id,
            customer_company_id=customer_id,
            session_id=session_id,
            resource=resource,
            amount_per_turn=amount,
            duration_turns=duration,
            payment_amount=payment,
            who_creator=company_id
        )
        
        if result is not None and result.get('error'):
            await callback.answer(f"❌ {result.get('error')}", show_alert=True)
        else:
            await self.scene.update_key('scene', 'success_message', 'Контракт создан!')
            await self.scene.update_key('scene', 'contract_state', 'main')
            # Очищаем временные данные
            for key in ['contract_role', 'contract_partner_id', 'contract_partner_name', 
                       'contract_resource', 'contract_amount', 'contract_duration', 'contract_payment']:
                await self.scene.update_key('scene', key, None)
            await self.scene.update_message()
    
    @Page.on_callback('cancel_create')
    async def cancel_create_handler(self, callback: CallbackQuery, args: list):
        """Отмена создания контракта"""
        await self.scene.update_key('scene', 'contract_state', 'main')
        await self.scene.update_message()
    
    @Page.on_callback('back_to_main')
    async def back_to_main_handler(self, callback: CallbackQuery, args: list):
        """Возврат на главный экран"""
        await self.scene.update_key('scene', 'contract_state', 'main')
        await self.scene.update_message()
    
    @Page.on_callback('back_to_role')
    async def back_to_role_handler(self, callback: CallbackQuery, args: list):
        """Возврат к выбору роли"""
        await self.scene.update_key('scene', 'contract_state', 'select_role')
        await self.scene.update_message()
    
    @Page.on_callback('back_to_partner')
    async def back_to_partner_handler(self, callback: CallbackQuery, args: list):
        """Возврат к выбору партнёра"""
        await self.scene.update_key('scene', 'contract_state', 'select_partner')
        await self.scene.update_message()
    
    @Page.on_callback('back_from_details')
    async def back_from_details_handler(self, callback: CallbackQuery, args: list):
        """Возврат из деталей контракта"""
        previous_state = self.scene.get_key('scene', 'previous_state') or 'main'
        await self.scene.update_key('scene', 'contract_state', previous_state)
        await self.scene.update_message()
    
    # Обработчики текста
    
    @Page.on_text('int')
    async def on_int_input(self, message: Message, value: int):
        """Обработка числового ввода"""
        scene_data = self.scene.get_data('scene')
        contract_state = scene_data.get('contract_state', '')
        
        # Ввод количества
        if contract_state == 'input_amount':
            if value < 1:
                await self.scene.update_key('scene', 'error_message', 'Количество должно быть больше 0')
            else:
                await self.scene.update_key('scene', 'contract_amount', value)
                await self.scene.update_key('scene', 'contract_state', 'input_duration')
                await self.scene.update_key('scene', 'error_message', '')
            await self.scene.update_message()
        
        # Ввод длительности
        elif contract_state == 'input_duration':
            if value < 1:
                await self.scene.update_key('scene', 'error_message', 'Длительность должна быть больше 0')
            elif value > 10:
                await self.scene.update_key('scene', 'error_message', 'Максимальная длительность: 10 ходов')
            else:
                await self.scene.update_key('scene', 'contract_duration', value)
                await self.scene.update_key('scene', 'contract_state', 'input_payment')
                await self.scene.update_key('scene', 'error_message', '')
            await self.scene.update_message()
        
        # Ввод оплаты
        elif contract_state == 'input_payment':
            if value < 1:
                await self.scene.update_key('scene', 'error_message', 'Сумма должна быть больше 0')
            else:
                await self.scene.update_key('scene', 'contract_payment', value)
                await self.scene.update_key('scene', 'contract_state', 'confirm')
                await self.scene.update_key('scene', 'error_message', '')
            await self.scene.update_message()
