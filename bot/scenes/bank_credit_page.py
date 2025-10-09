from oms import Page
from aiogram.types import CallbackQuery, Message
from modules.ws_client import get_company, company_take_credit, company_pay_credit
from oms.utils import callback_generator
from global_modules.bank import get_credit_conditions, calc_credit
from pprint import pprint

class BankCreditPage(Page):
    
    __page_name__ = "bank-credit-page"
    
    async def content_worker(self):
        scene_data = self.scene.get_data('scene')
        company_id = scene_data.get('company_id')
        
        if not company_id:
            return "❌ Ошибка: компания не найдена"
        
        # Получаем данные компании
        company_data = await get_company(id=company_id)
        
        if isinstance(company_data, str):
            return f"❌ Ошибка при получении данных: {company_data}"
        
        reputation = company_data.get('reputation', 0)
        credits = company_data.get('credits', [])
        
        # Получаем состояние страницы
        credit_state = scene_data.get('credit_state', 'main')
        
        # Основной экран
        if credit_state == 'main':
            return await self._main_screen(credits, reputation)
        
        # Экран ввода срока кредита
        elif credit_state == 'input_period':
            return await self._input_period_screen(company_data)
        
        # Экран ввода суммы кредита
        elif credit_state == 'input_amount':
            return await self._input_amount_screen(scene_data)
        
        # Экран подтверждения кредита
        elif credit_state == 'confirm':
            return await self._confirm_screen(scene_data, reputation)
        
        return "❌ Неизвестное состояние"
    
    async def _main_screen(self, credits, reputation):
        """Основной экран с информацией о кредитах"""
        text = "💳 *Кредиты*\n\n"
        
        # Получаем условия кредитования
        try:
            conditions = get_credit_conditions(reputation)
            
            # Информация об условиях
            percent = conditions.percent * 100
            without_interest = conditions.without_interest
            
            text += f"*Ваши условия:*\n"
            text += f"Процентная ставка: {percent}%\n"
            text += f"Льготный период: {without_interest} ход(ов)\n"
            text += f"Репутация: {reputation} ⭐\n\n"
        except ValueError:
            text += "❌ *Кредиты недоступны*\n"
            text += f"Минимальная репутация для кредита: 11\n"
            text += f"Ваша репутация: {reputation} ⭐\n\n"
        
        # Активные кредиты
        if credits and len(credits) > 0:
            text += "*Активные кредиты:*\n\n"
            for i, credit in enumerate(credits, 1):
                total = credit.get("total_to_pay", 0)
                paid = credit.get("paid", 0)
                need_pay = credit.get("need_pay", 0)
                steps_total = credit.get("steps_total", 0)
                steps_now = credit.get("steps_now", 0)
                
                remaining = total - paid
                steps_left = steps_total - steps_now
                
                text += f"*Кредит #{i}*\n"
                text += f"Осталось выплатить: {remaining:,} 💰 (из {total:,})\n".replace(",", " ")
                text += f"Следующий платеж: {need_pay:,} 💰\n".replace(",", " ")
                text += f"Ходов до закрытия: {steps_left}/{steps_total}\n"
                
                if need_pay > 0:
                    text += "⚠️ *Требуется оплата!*\n"
                
                text += "\n"
        else:
            text += "_У вас нет активных кредитов_\n"
        
        return text
    
    async def _input_period_screen(self, company_data):
        """Экран ввода срока кредита"""
        # Получаем текущий ход и максимум
        current_step = company_data.get('step', 0)
        max_step = company_data.get('max_step', 15)
        max_period = max_step - current_step
        
        text = f"""⏱ *Взятие кредита*

*Шаг 1: Введите срок кредита*

На какое количество ходов хотите взять кредит?
Минимум: 1 ход
Максимум: {max_period} ход(ов)
(Текущий ход: {current_step}, до конца игры: {max_period})"""
        
        return text
    
    async def _input_amount_screen(self, scene_data):
        """Экран ввода суммы кредита"""
        credit_period = scene_data.get('credit_period', 0)
        
        text = f"""💰 *Взятие кредита*

✅ Срок: {credit_period} ход(ов)

*Шаг 2: Введите сумму кредита*

Какую сумму хотите взять в кредит?
Минимум: 1 000 💰"""
        
        return text
    
    async def _confirm_screen(self, scene_data, reputation):
        """Экран подтверждения взятия кредита"""
        credit_period = scene_data.get('credit_period', 0)
        credit_amount = scene_data.get('credit_amount', 0)
        
        # Получаем условия кредитования
        conditions = get_credit_conditions(reputation)
        
        # Расчитываем параметры кредита
        total, pay_per_turn, extra = calc_credit(
            S=credit_amount,
            free=conditions.without_interest,
            r_percent=conditions.percent,
            T=credit_period
        )
        
        percent = conditions.percent * 100
        
        text = f"""💳 *Подтверждение кредита*

*Параметры кредита:*
Сумма: {credit_amount:,} 💰
Срок: {credit_period} ход(ов)

*Условия:*
Процентная ставка: {percent}%
Льготный период: {conditions.without_interest} ход(ов)
Ходов с процентами: {extra}

*К оплате:*
Всего к возврату: {total:,} 💰
Платеж за ход: {pay_per_turn:,} 💰

Подтвердите взятие кредита:""".replace(",", " ")
        
        return text
    
    async def buttons_worker(self):
        """Генерация кнопок"""
        scene_data = self.scene.get_data('scene')
        company_id = scene_data.get('company_id')
        credit_state = scene_data.get('credit_state', 'main')
        
        buttons = []
        
        # Кнопки для основного экрана
        if credit_state == 'main':
            # Получаем данные компании
            company_data = await get_company(id=company_id)
            
            if isinstance(company_data, dict):
                reputation = company_data.get('reputation', 0)
                credits = company_data.get('credits', [])
                
                # Проверяем возможность взять кредит
                try:
                    get_credit_conditions(reputation)
                    buttons.append({
                        'text': '💰 Взять кредит',
                        'callback_data': callback_generator(
                            self.scene.__scene_name__,
                            'take_credit'
                        )
                    })
                except ValueError:
                    pass
                
                # Кнопки для оплаты кредитов
                if credits and len(credits) > 0:
                    for i, credit in enumerate(credits):
                        need_pay = credit.get("need_pay", 0)
                        if need_pay > 0:
                            buttons.append({
                                'text': f'💸 Оплатить кредит #{i+1} ({need_pay:,} 💰)'.replace(",", " "),
                                'callback_data': callback_generator(
                                    self.scene.__scene_name__,
                                    'pay_credit',
                                    str(i)
                                )
                            })
        
        # Кнопки для экранов ввода - добавляем кнопку отмены
        elif credit_state in ['input_period', 'input_amount']:
            buttons = [
                {
                    'text': '❌ Отменить',
                    'callback_data': callback_generator(
                        self.scene.__scene_name__,
                        'cancel_credit'
                    )
                }
            ]
        
        # Кнопки для экрана подтверждения
        elif credit_state == 'confirm':
            buttons = [
                {
                    'text': '✅ Да, взять кредит',
                    'callback_data': callback_generator(
                        self.scene.__scene_name__,
                        'confirm_credit'
                    )
                },
                {
                    'text': '❌ Нет, отменить',
                    'callback_data': callback_generator(
                        self.scene.__scene_name__,
                        'cancel_credit'
                    )
                }
            ]
        
        self.row_width = 1
        return buttons
    
    @Page.on_callback('take_credit')
    async def take_credit_handler(self, callback: CallbackQuery, args: list):
        """Начало процесса взятия кредита - запрос срока"""
        # Устанавливаем состояние ожидания ввода срока
        scene_data = self.scene.get_data('scene')
        scene_data['credit_state'] = 'input_period'
        self.scene.set_data('scene', scene_data)
        
        # Обновляем сообщение для показа инструкции
        await self.scene.update_message()
        await callback.answer("💬 Введите срок кредита в сообщении")
    
    @Page.on_callback('pay_credit')
    async def pay_credit_handler(self, callback: CallbackQuery, args: list):
        """Оплата кредита"""
        # Проверяем структуру args - если первый элемент 'pay_credit', берем второй
        if args and args[0] == 'pay_credit':
            if len(args) < 2:
                await callback.answer("❌ Ошибка: не указан индекс кредита", show_alert=True)
                return
            credit_index = int(args[1])
        elif args and len(args) > 0:
            credit_index = int(args[0])
        else:
            await callback.answer("❌ Ошибка: не указан индекс кредита", show_alert=True)
            return
        
        scene_data = self.scene.get_data('scene')
        company_id = scene_data.get('company_id')
        
        if not company_id:
            await callback.answer("❌ Ошибка: компания не найдена", show_alert=True)
            return
        
        # Получаем данные компании
        company_data = await get_company(id=company_id)
        if isinstance(company_data, str):
            await callback.answer(f"❌ Ошибка: {company_data}", show_alert=True)
            return
        
        credits = company_data.get('credits', [])
        balance = company_data.get('balance', 0)
        
        if credit_index < 0 or credit_index >= len(credits):
            await callback.answer("❌ Ошибка: кредит не найден", show_alert=True)
            return
        
        credit = credits[credit_index]
        need_pay = credit.get("need_pay", 0)
        
        if need_pay <= 0:
            await callback.answer("✅ По этому кредиту нет задолженности", show_alert=True)
            return
        
        if balance < need_pay:
            await callback.answer(
                f"❌ Недостаточно средств!\nНеобходимо: {need_pay:,} 💰\nДоступно: {balance:,} 💰".replace(",", " "),
                show_alert=True
            )
            return
        
        # Оплачиваем кредит
        result = await company_pay_credit(
            company_id=str(company_id),
            credit_index=credit_index,
            amount=need_pay
        )
        
        if isinstance(result, str):
            await callback.answer(f"❌ Ошибка: {result}", show_alert=True)
        else:
            await callback.answer(f"✅ Платеж выполнен: {need_pay:,} 💰".replace(",", " "), show_alert=True)
            # Сбрасываем состояние и обновляем страницу
            scene_data = self.scene.get_data('scene')
            scene_data['credit_state'] = 'main'
            self.scene.set_data('scene', scene_data)
            await self.scene.update_message()
    
    @Page.on_callback('confirm_credit')
    async def confirm_credit_handler(self, callback: CallbackQuery, args: list):
        """Подтверждение взятия кредита"""
        scene_data = self.scene.get_data('scene')
        company_id = scene_data.get('company_id')
        credit_amount = scene_data.get('credit_amount', 0)
        credit_period = scene_data.get('credit_period', 0)
        
        if not company_id:
            await callback.answer("❌ Ошибка: компания не найдена", show_alert=True)
            return
        
        # Берем кредит
        result = await company_take_credit(
            company_id=str(company_id),
            amount=credit_amount,
            period=credit_period
        )
        print("=========================================================")
        pprint(result)
        print("=========================================================")
        if isinstance(result, str):
            await callback.answer(f"❌ Ошибка: {result}", show_alert=True)
        else:
            await callback.answer(
                f"✅ Кредит оформлен!\n"
                f"Сумма: {credit_amount:,} 💰\n"
                f"Срок: {credit_period} ход(ов)".replace(",", " "),
                show_alert=True
            )
            # Сбрасываем состояние и возвращаемся к основному экрану
            scene_data['credit_state'] = 'main'
            scene_data['credit_amount'] = 0
            scene_data['credit_period'] = 0
            self.scene.set_data('scene', scene_data)
            await self.scene.update_message()
    
    @Page.on_callback('cancel_credit')
    async def cancel_credit_handler(self, callback: CallbackQuery, args: list):
        """Отмена взятия кредита"""
        scene_data = self.scene.get_data('scene')
        scene_data['credit_state'] = 'main'
        scene_data['credit_amount'] = 0
        scene_data['credit_period'] = 0
        self.scene.set_data('scene', scene_data)
        
        await callback.answer("❌ Взятие кредита отменено")
        await self.scene.update_message()
    
    @Page.on_text('int')
    async def handle_input(self, message: Message, value: int):
        """Обработка ввода чисел (срок или сумма)"""
        scene_data = self.scene.get_data('scene')
        credit_state = scene_data.get('credit_state', 'main')
        company_id = scene_data.get('company_id')
        
        # Ввод срока кредита
        if credit_state == 'input_period':
            if value < 1:
                await message.answer("❌ Срок должен быть не менее 1 хода")
                return
            
            # Получаем данные компании для проверки максимального срока
            company_data = await get_company(id=company_id)
            if isinstance(company_data, str):
                await message.answer(f"❌ Ошибка: {company_data}")
                return
            
            current_step = company_data.get('step', 0)
            max_step = company_data.get('max_step', 15)
            max_period = max_step - current_step
            
            if value > max_period:
                await message.answer(
                    f"❌ Срок не может превышать {max_period} ход(ов)!\n"
                    f"(Текущий ход: {current_step}, до конца игры: {max_period})"
                )
                return
            
            # Сохраняем срок и переходим к вводу суммы
            scene_data['credit_period'] = value
            scene_data['credit_state'] = 'input_amount'
            self.scene.set_data('scene', scene_data)
            
            # Обновляем сообщение для показа следующего шага
            await self.scene.update_message()
        
        # Ввод суммы кредита
        elif credit_state == 'input_amount':
            if value < 1000:
                await message.answer("❌ Минимальная сумма кредита: 1 000 💰")
                return
            
            # Сохраняем сумму и переходим к подтверждению
            scene_data['credit_amount'] = value
            scene_data['credit_state'] = 'confirm'
            self.scene.set_data('scene', scene_data)
            
            # Обновляем сообщение для показа экрана подтверждения
            await self.scene.update_message()
