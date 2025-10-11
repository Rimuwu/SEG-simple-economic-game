import asyncio
from typing import Optional
from game.stages import leave_from_prison
from global_modules.models.cells import CellType, Cells
from modules.generate import generate_number
from modules.websocket_manager import websocket_manager
from global_modules.db.baseclass import BaseClass
from modules.json_database import just_db
from game.session import session_manager
from global_modules.load_config import ALL_CONFIGS, Resources, Improvements, Settings, Capital, Reputation
from global_modules.bank import calc_credit, get_credit_conditions, check_max_credit_steps, calc_deposit, get_deposit_conditions, check_max_deposit_steps
from game.factory import Factory

RESOURCES: Resources = ALL_CONFIGS["resources"]
CELLS: Cells = ALL_CONFIGS['cells']
IMPROVEMENTS: Improvements = ALL_CONFIGS['improvements']
SETTINGS: Settings = ALL_CONFIGS['settings']
CAPITAL: Capital = ALL_CONFIGS['capital']
REPUTATION: Reputation = ALL_CONFIGS['reputation']

class Company(BaseClass):

    __tablename__ = "companies"
    __unique_id__ = "id"
    __db_object__ = just_db

    def __init__(self, _id: int = 0):
        self.id: int = _id
        self.name: str = ""

        self.reputation: int = 0
        self.balance: int = 0
        self.economic_power: int = 0

        self.in_prison: bool = False
        self.prison_end_step: Optional[int] = None

        self.credits: list = []
        self.deposits: list = []

        self.improvements: dict = {}
        self.warehouses: dict = {}

        self.session_id: str = ""
        self.cell_position: str = "" # 3.1

        self.tax_debt: int = 0  # Задолженность по налогам
        self.overdue_steps: int = 0  # Количество просроченных ходов

        self.secret_code: int = 0 # Для вступления другими игроками

        self.last_turn_income: int = 0  # Доход за прошлый ход
        self.this_turn_income: int = 0  # Доход за текущий ход

        self.business_type: str = "small"  # Тип бизнеса: "small" или "big"
        self.owner: int = 0

    def set_owner(self, user_id: int):
        if self.owner != 0:
            raise ValueError("Владелец уже установлен.")
        if user_id in [user.id for user in self.users] is False:
            raise ValueError("Пользователь не является членом компании.")

        self.owner = user_id
        self.save_to_base()

    def create(self, name: str, session_id: str):
        self.name = name
        self.id = just_db.max_id_in_table(
            self.__tablename__) + 1

        with_this_name = just_db.find_one(
            self.__tablename__, name=name, session_id=session_id)
        if with_this_name:
            raise ValueError(f"Компания с именем '{name}' уже существует.")

        session = session_manager.get_session(session_id)
        if not session or not session.can_add_company():
            raise ValueError("Недействительная или неактивная сессия для добавления компании.")
        self.session_id = session_id

        self.name = name

        # Генерируем уникальный секретный код
        not_in_use = True
        while not_in_use:
            self.secret_code = generate_number(6)
            if not just_db.find_one("companies",
                                    secret_code=self.secret_code):
                not_in_use = False

        self.improvements = SETTINGS.start_improvements_level.__dict__

        self.balance = CAPITAL.start
        self.reputation = REPUTATION.start

        self.save_to_base()
        self.reupdate()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-create_company",
            "data": {
                'session_id': self.session_id,
                'company': self.to_dict()
            }
        }))
        return self

    def can_user_enter(self):
        session = session_manager.get_session(self.session_id)
        if not session or session.stage != "FreeUserConnect":
            return False

        if len(self.users) >= SETTINGS.max_players_in_company:
            return False
        return True

    @property
    def users(self) -> list['User']:
        from game.user import User

        users = just_db.find(
            User.__tablename__, to_class=User, 
            company_id=self.id
        )
        return users

    def set_position(self, x: int, y: int):
        if isinstance(x, int) is False or isinstance(y, int) is False:
            raise ValueError("Координаты должны быть целыми числами.")

        session = session_manager.get_session(self.session_id)
        if not session or not session.can_select_cell(x, y):
            return False

        old_position = self.cell_position
        self.cell_position = f"{x}.{y}"
        self.save_to_base()
        self.reupdate()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-company_set_position",
            "data": {
                "company_id": self.id,
                "old_position": old_position,
                "new_position": self.cell_position
            }
        }))

        col = self.get_improvements()['factory']['tasksPerTurn']
        col_complect = col // 3
        cell_type: str = self.get_cell_type() # type: ignore

        for _ in range(col):
            res = None

            if col_complect > 0:
                res = SETTINGS.start_complectation.get(cell_type, None)

            Factory().create(self.id, res)
            col_complect -= 1

        return True

    def get_position(self):
        if not self.cell_position:
            return None
        try:
            x, y = map(int, self.cell_position.split('.'))
            return (x, y)
        except Exception:
            return None

    def delete(self):
        just_db.delete(self.__tablename__, **{self.__unique_id__: self.id})

        for user in self.users: user.leave_from_company()
        for factory in self.get_factories(): factory.delete()
        for exchange in self.exchages: exchange.delete()
        for contract in self.get_contracts(): contract.delete()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-company_deleted",
            "data": {
                "company_id": self.id
            }
        }))
        return True

    def get_max_warehouse_size(self) -> int:
        imps = self.get_improvements()
        if 'warehouse' not in imps:
            return 0

        base_size = imps['warehouse']['capacity']
        return base_size

    def get_warehouse_free_size(self) -> int:
        return self.get_max_warehouse_size() - self.get_resources_amount()

    def add_resource(self, resource: str, amount: int, 
                     ignore_space: bool = False):
        if RESOURCES.get_resource(resource) is None:
            raise ValueError(f"Ресурс '{resource}' не существует.")
        if amount <= 0:
            raise ValueError("Количество должно быть положительным целым числом.")
        if self.get_resources_amount() + amount > self.get_max_warehouse_size() and not ignore_space:
            raise ValueError("Недостаточно места на складе.")

        if resource in self.warehouses:
            self.warehouses[resource] += amount
        else:
            self.warehouses[resource] = amount

        self.save_to_base()
        self.reupdate()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-company_resource_added",
            "data": {
                "company_id": self.id,
                "resource": resource,
                "amount": amount
            }
        }))
        return True

    def remove_resource(self, resource: str, amount: int):
        if RESOURCES.get_resource(resource) is None:
            raise ValueError(f"Ресурс '{resource}' не существует.")
        if amount <= 0:
            raise ValueError("Количество должно быть положительным целым числом.")
        if resource not in self.warehouses or self.warehouses[resource] < amount:
            raise ValueError(f"Недостаточно ресурса '{resource}' для удаления.")

        self.warehouses[resource] -= amount
        if self.warehouses[resource] == 0:
            del self.warehouses[resource]

        self.save_to_base()
        self.reupdate()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-company_resource_removed",
            "data": {
                "company_id": self.id,
                "resource": resource,
                "amount": amount
            }
        }))
        return True

    def get_resources_amount(self):
        count = 0
        for amount in self.warehouses.values(): 
            count += amount
        return count

    def set_economic_power(self, count: int, item: str, e_type: str):
        mod = 1

        if e_type == "production":
            mod = 1
        elif e_type == "exchange":
            mod = 2
        elif e_type == "city_sell":
            mod = 3
        elif e_type == "contract":
            mod = 2

        resource = RESOURCES.get_resource(item)  # type: ignore
        if not resource:
            dif = 0
        else:
            dif = resource.basePrice

        self.economic_power += int(count * dif * mod)
        self.save_to_base()

    def get_my_cell_info(self):
        cell_type_key = self.get_cell_type()
        if not cell_type_key: return None

        result = CELLS.types.get(cell_type_key)
        return result

    def get_cell_type(self):
        position = self.get_position()
        if not position:
            return None
        x, y = position
        session = session_manager.get_session(self.session_id)
        if not session:
            return None
        index = x * session.map_size["cols"] + y

        if index < 0 or index >= len(session.cells):
            return None
        return session.cells[index]

    def get_improvements(self):
        """ Возвращает данные улучшений для компании
        """
        cell_type = self.get_cell_type()
        if cell_type is None: return {}

        data = {}

        for iml_key in self.improvements.keys():
            data[iml_key] = IMPROVEMENTS.get_improvement(
                cell_type, iml_key, str(self.improvements[iml_key])
            ).__dict__

        return data

    def add_balance(self, amount: int, income_percent: float = 1.0):
        if not isinstance(income_percent, float):
            raise ValueError("Процент дохода должен быть числом с плавающей точкой.")
        if income_percent < 0:
            raise ValueError("Процент дохода должен быть неотрицательным.")
        if not isinstance(amount, int):
            raise ValueError("Сумма должна быть целым числом.")
        if amount <= 0:
            raise ValueError("Сумма должна быть положительным целым числом.")

        old_balance = self.balance
        self.balance += amount
        self.this_turn_income += int(amount * income_percent)

        self.save_to_base()
        self.reupdate()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-company_balance_changed",
            "data": {
                "company_id": self.id,
                "old_balance": old_balance,
                "new_balance": self.balance
            }
        }))
        return True

    def remove_balance(self, amount: int):
        if not isinstance(amount, int):
            raise ValueError("Сумма должна быть целым числом.")
        if amount <= 0:
            raise ValueError("Сумма должна быть положительным целым числом.")
        if self.balance < amount:
            raise ValueError("Недостаточно средств для списания.")

        old_balance = self.balance
        self.balance -= amount
        self.save_to_base()
        self.reupdate()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-company_balance_changed",
            "data": {
                "company_id": self.id,
                "old_balance": old_balance,
                "new_balance": self.balance
            }
        }))
        return True

    def improve(self, improvement_type: str):
        """ Улучшает указанное улучшение на 1 уровень, если это возможно.
        """

        self.in_prison_check()

        # my_improvements = self.get_improvements()
        imp_lvl_now = self.improvements.get(
            improvement_type, None)
        cell_type = self.get_cell_type()

        if cell_type is None:
            raise ValueError("Невозможно определить тип клетки для улучшений.")

        if imp_lvl_now is None:
            raise ValueError(f"Тип улучшения '{improvement_type}' не найден.")

        imp_next_lvl = IMPROVEMENTS.get_improvement(
                cell_type, improvement_type, 
                str(imp_lvl_now + 1)
            )

        if imp_next_lvl is None:
            raise ValueError(f"Нет следующего уровня для улучшения '{improvement_type}'.")

        cost = imp_next_lvl.cost
        self.remove_balance(cost)

        self.improvements[improvement_type] = imp_lvl_now + 1
        self.save_to_base()
        self.reupdate()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-company_improvement_upgraded",
            "data": {
                "company_id": self.id,
                "improvement_type": improvement_type,
                "new_level": self.improvements[improvement_type]
            }
        }))
        return True

    def add_reputation(self, amount: int):
        if not isinstance(amount, int):
            raise ValueError("Сумма должна быть целым числом.")
        if amount <= 0:
            raise ValueError("Сумма должна быть положительным целым числом.")

        old_reputation = self.reputation
        self.reputation += amount
        self.save_to_base()
        self.reupdate()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-company_reputation_changed",
            "data": {
                "company_id": self.id,
                "old_reputation": old_reputation,
                "new_reputation": self.reputation
            }
        }))
        return True

    def remove_reputation(self, amount: int):
        if not isinstance(amount, int):
            raise ValueError("Сумма должна быть целым числом.")
        if amount <= 0:
            raise ValueError("Сумма должна быть положительным целым числом.")

        old_reputation = self.reputation
        self.reputation = max(0, self.reputation - amount)
        
        if self.reputation != old_reputation:
            self.save_to_base()
            self.reupdate()

            asyncio.create_task(websocket_manager.broadcast({
                "type": "api-company_reputation_changed",
                "data": {
                    "company_id": self.id,
                    "old_reputation": old_reputation,
                    "new_reputation": self.reputation
                }
            }))

            if self.reputation <= 0: self.to_prison()
            return True
        return False

    def take_credit(self, c_sum: int, steps: int):
        """ 
            Сумма кредита у нас между минимумом и максимумом
            Количество шагов у нас 
        """
        self.in_prison_check()

        if not isinstance(c_sum, int) or not isinstance(steps, int):
            raise ValueError("Сумма и шаги должны быть целыми числами.")
        if c_sum <= 0 or steps <= 0:
            raise ValueError("Сумма и шаги должны быть положительными целыми числами.")

        credit_condition = get_credit_conditions(self.reputation)
        if not credit_condition.possible:
            raise ValueError("Кредит невозможен с текущей репутацией.")

        total, pay_per_turn, extra = calc_credit(
            c_sum, credit_condition.without_interest, credit_condition.percent, steps
            )

        session = session_manager.get_session(self.session_id)
        if not session:
            raise ValueError("Сессия не найдена.")

        if not check_max_credit_steps(steps, 
                                      session.step, 
                                      session.max_steps):
            raise ValueError("Срок кредита превышает максимальное количество шагов игры.")

        if len(self.credits) >= SETTINGS.max_credits_per_company:
            raise ValueError("Достигнуто максимальное количество активных кредитов для этой компании.")

        if c_sum > CAPITAL.bank.credit.max:
            raise ValueError(f"Сумма кредита превышает максимальный лимит {CAPITAL.bank.credit.max}.")

        elif c_sum < CAPITAL.bank.credit.min:
            raise ValueError(f"Сумма кредита ниже минимального лимита {CAPITAL.bank.credit.min}.")

        credit_data = {
            "total_to_pay": total,
            "need_pay": 0,
            "paid": 0,

            "steps_total": steps,
            "steps_now": 0
        }
        self.credits.append(credit_data)

        self.save_to_base()
        self.add_balance(c_sum, 0.0) # деньги без процентов в доход

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-company_credit_taken",
            "data": {
                "company_id": self.id,
                "amount": c_sum,
                "steps": steps
            }
        }))
        return credit_data

    def credit_paid_step(self):
        """ Вызывается при каждом шаге игры для компании.
            Начисляет плату по кредитам, если они есть.
        """

        for index, credit in enumerate(self.credits):

            if credit["steps_now"] < credit["steps_total"]:
                steps_left = max(1, credit["steps_total"] - credit["steps_now"])
                credit["need_pay"] += (credit["total_to_pay"] - credit['need_pay'] - credit ['paid']) // steps_left
                credit["steps_now"] += 1

            elif credit["steps_now"] == credit["steps_total"]:
                # Последний день - начисляем всю оставшуюся сумму
                credit["need_pay"] += credit["total_to_pay"] - credit['paid']
                credit["steps_now"] += 1

            elif credit["steps_now"] > credit["steps_total"]:
                # Просрочка - не увеличиваем steps_now больше, но снижаем репутацию
                self.remove_reputation(REPUTATION.credit.lost)

            if credit["steps_now"] - credit["steps_total"] > REPUTATION.credit.max_overdue:
                self.remove_reputation(self.reputation)
                self.remove_credit(index)
                self.to_prison()

        self.save_to_base()
        self.reupdate()

    def remove_credit(self, credit_index: int):
        """ Удаляет кредит с индексом credit_index.
        """

        if credit_index < 0 or credit_index >= len(self.credits):
            raise ValueError("Недействительный индекс кредита.")

        del self.credits[credit_index]
        self.save_to_base()
        self.reupdate()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-company_credit_removed",
            "data": {
                "company_id": self.id,
                "credit_index": credit_index
            }
        }))
        return True

    def pay_credit(self, credit_index: int, amount: int):
        """ Платит указанную сумму по кредиту с индексом credit_index.
        """

        self.in_prison_check()

        if not isinstance(credit_index, int) or not isinstance(amount, int):
            raise ValueError("Индекс кредита и сумма должны быть целыми числами.")
        if credit_index < 0 or credit_index >= len(self.credits):
            raise ValueError("Недействительный индекс кредита.")
        if amount <= 0:
            raise ValueError("Сумма должна быть положительным целым числом.")
        if self.balance < amount:
            raise ValueError("Недостаточно средств для оплаты кредита.")

        credit = self.credits[credit_index]

        if amount < credit["need_pay"]:
            raise ValueError("Сумма платежа должна быть не менее требуемой для этого хода.")

        # Досрочное закрытие кредита - можно заплатить больше чем need_pay
        remaining_debt = credit["total_to_pay"] - credit["paid"]
        if amount > remaining_debt:
            amount = remaining_debt

        # Снимаем деньги с баланса
        self.remove_balance(amount)

        # Обновляем информацию по кредиту
        credit["paid"] += amount
        credit["need_pay"] = max(0, credit["need_pay"] - amount)

        # Если кредит полностью выплачен, удаляем его
        if credit["paid"] >= credit["total_to_pay"]:
            self.remove_credit(credit_index)
            self.add_reputation(REPUTATION.credit.gained)
        else:
            self.credits[credit_index] = credit
            self.save_to_base()
            self.reupdate()

        remaining = credit["total_to_pay"] - credit["paid"] if credit["paid"] < credit["total_to_pay"] else 0

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-company_credit_paid",
            "data": {
                "company_id": self.id,
                "credit_index": credit_index,
                "amount": amount,
                "remaining": remaining
            }
        }))
        return True

    def to_prison(self):
        """ Сажает компанию в тюрьму за неуплату кредитов
        """

        # Сажается на Х ходов и после шедулером выкидывается с пустой компанией

        session = session_manager.get_session(self.session_id)
        if not session:
            raise ValueError("Сессия не найдена.")

        end_step = session.step + REPUTATION.prison.stages

        self.in_prison = True
        self.prison_end_step = end_step
        self.save_to_base()
        self.reupdate()

        session.create_step_schedule(
            end_step,
            leave_from_prison,
            session_id=self.session_id,
            company_id=self.id
        )

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-company_to_prison",
            "data": {
                "company_id": self.id,
                "end_step": end_step
            }
        }))

    def leave_prison(self):
        """ Выход из тюрьмы по времени
        """

        if not self.in_prison:
            raise ValueError("Компания не находится в тюрьме.")

        self.in_prison = False
        self.prison_end_step = None
        self.save_to_base()
        self.reupdate()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-company_left_prison",
            "data": {
                "company_id": self.id
            }
        }))
        return True

    def in_prison_check(self):
        """ Находится ли компания в тюрьме (Вызов ошибки для удобства)
        """
        if self.in_prison:
            raise ValueError("Компания уже находится в тюрьме.")

        return self.in_prison

    def business_tax(self):
        """ Определяет налоговую ставку в зависимости от типа бизнеса.
        """
        
        session = session_manager.get_session(self.session_id)
        if not session:
            raise ValueError("Сессия не найдена.")

        big_mod = session.get_event_effects().get(
            'tax_rate_large', CAPITAL.bank.tax.big_on
        )

        small_mod = session.get_event_effects().get(
            'tax_rate_small', CAPITAL.bank.tax.small_business
        )

        if self.business_type == "big":
            return big_mod
        return small_mod

    def taxate(self):
        """ Начисляет налоги в зависимости от типа бизнеса. Вызывается каждый ход.
        """

        if self.tax_debt > 0:
            self.overdue_steps += 1
            self.remove_reputation(REPUTATION.tax.late)

        if self.overdue_steps > REPUTATION.tax.not_paid_stages:
            self.overdue_steps = 0
            self.tax_debt = 0

            self.remove_reputation(self.reputation)
            self.to_prison()
            return

        percent = self.business_tax()
        tax_amount = int(self.last_turn_income * percent)

        self.tax_debt += tax_amount
        self.save_to_base()
        self.reupdate()


    def pay_taxes(self, amount: int):
        """ Платит указанную сумму по налогам.
        """

        self.in_prison_check()

        if not isinstance(amount, int):
            raise ValueError("Сумма должна быть целым числом.")
        if amount <= 0:
            raise ValueError("Сумма должна быть положительным целым числом.")
        if self.tax_debt <= 0:
            raise ValueError("Нет налогового долга для оплаты.")
        if self.balance < amount:
            raise ValueError("Недостаточно средств для оплаты налогов.")

        if amount > self.tax_debt: amount = self.tax_debt

        # Снимаем деньги с баланса
        self.remove_balance(amount)

        # Обновляем информацию по налогам
        self.tax_debt -= amount
        if self.tax_debt <= 0:
            self.tax_debt = 0
            self.overdue_steps = 0
            self.add_reputation(REPUTATION.tax.paid)

        self.save_to_base()
        self.reupdate()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-company_tax_paid",
            "data": {
                "company_id": self.id,
                "amount": amount,
                "remaining": self.tax_debt
            }
        }))
        return True

    def take_deposit(self, d_sum: int, steps: int):
        """ 
            Создаёт вклад на указанную сумму и срок
            d_sum - сумма вклада
            steps - срок вклада в ходах
        """
        self.in_prison_check()

        if not isinstance(d_sum, int) or not isinstance(steps, int):
            raise ValueError("Сумма и шаги должны быть целыми числами.")
        if d_sum <= 0 or steps <= 0:
            raise ValueError("Сумма и шаги должны быть положительными целыми числами.")

        deposit_condition = get_deposit_conditions(self.reputation)
        if not deposit_condition.possible:
            raise ValueError("Депозит невозможен с текущей репутацией.")

        income_per_turn, total_income = calc_deposit(
            d_sum, deposit_condition.percent, steps
        )

        session = session_manager.get_session(self.session_id)
        if not session:
            raise ValueError("Сессия не найдена.")

        if not check_max_deposit_steps(steps, 
                                       session.step, 
                                       session.max_steps):
            raise ValueError("Срок депозита превышает максимальное количество шагов игры.")

        if d_sum > CAPITAL.bank.contribution.max:
            raise ValueError(f"Сумма депозита превышает максимальный лимит {CAPITAL.bank.contribution.max}.")

        elif d_sum < CAPITAL.bank.contribution.min:
            raise ValueError(f"Сумма депозита ниже минимального лимита {CAPITAL.bank.contribution.min}.")

        if self.balance < d_sum:
            raise ValueError("Недостаточно средств для создания депозита.")

        deposit_data = {
            "initial_sum": d_sum,
            "current_balance": d_sum,  # Баланс вклада (сумма + накопленные проценты)
            "income_per_turn": income_per_turn,
            "total_earned": 0,  # Сколько уже заработано процентов
            
            "steps_total": steps,
            "steps_now": 0,
            
            "can_withdraw_from": session.step + 3  # Можно забрать через 3 хода
        }
        
        # Снимаем деньги с баланса компании
        self.remove_balance(d_sum)
        
        self.deposits.append(deposit_data)
        self.save_to_base()
        self.reupdate()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-company_deposit_taken",
            "data": {
                "company_id": self.id,
                "amount": d_sum,
                "steps": steps
            }
        }))
        return deposit_data

    def deposit_income_step(self):
        """ Вызывается при каждом шаге игры для компании.
            Начисляет доход по вкладам на баланс вклада (не на счёт компании).
            Автоматически снимает депозиты по окончании срока.
        """

        for index, deposit in enumerate(self.deposits):
            if deposit["steps_now"] < deposit["steps_total"]:
                # Начисляем проценты на баланс вклада
                deposit["current_balance"] += deposit["income_per_turn"]
                deposit["total_earned"] += deposit["income_per_turn"]

            deposit["steps_now"] += 1

            # Если срок депозита истек, то снимаем
            if deposit["steps_now"] >= deposit["steps_total"]:

                if self.in_prison is False:
                    self.withdraw_deposit(index)

        self.save_to_base()
        self.reupdate()

    def withdraw_deposit(self, deposit_index: int):
        """ Забирает депозит с индексом deposit_index.
            Возвращает всю сумму (начальная + проценты) на счёт компании.
        """
        self.in_prison_check()

        if not isinstance(deposit_index, int):
            raise ValueError("Индекс депозита должен быть целым числом.")
        if deposit_index < 0 or deposit_index >= len(self.deposits):
            raise ValueError("Недействительный индекс депозита.")

        deposit = self.deposits[deposit_index]
        
        session = session_manager.get_session(self.session_id)
        if not session:
            raise ValueError("Сессия не найдена.")
        
        # Проверяем, можно ли забрать деньги (прошло минимум 3 хода)
        if session.step < deposit["can_withdraw_from"]:
            raise ValueError(f"Нельзя забрать депозит пока. Доступно с шага {deposit['can_withdraw_from']}.")

        # Возвращаем весь баланс вклада на счёт компании
        amount_to_return = deposit["current_balance"]
        self.add_balance(amount_to_return, 0.0)  # Деньги без учёта в доходе

        # Удаляем вклад
        del self.deposits[deposit_index]
        self.save_to_base()
        self.reupdate()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-company_deposit_withdrawn",
            "data": {
                "company_id": self.id,
                "deposit_index": deposit_index,
                "amount": amount_to_return
            }
        }))
        return True


    def raw_in_step(self):
        """ Вызывается при каждом шаге игры для компании.
            Определеяет сколько сырья выдать компании в ход.
        """

        imps = self.get_improvements()
        if 'station' not in imps:
            return 0

        perturn = imps['station']['productsPerTurn']
        return perturn


    def get_factories(self) -> list['Factory']:
        """ Возвращает список фабрик компании.
        """
        return [factory for factory in just_db.find(
            "factories", to_class=Factory, company_id=self.id)] # type: ignore

    def complect_factory(self, factory_id: int, resource: str):
        """ Укомплектовать фабрику с указанным ID ресурсом.
            Запускает этап комплектации.
        """

        factory = Factory(factory_id).reupdate()
        if not factory:
            raise ValueError("Фабрика не найдена.")
        if factory.company_id != self.id:
            raise ValueError("Фабрика не принадлежит этой компании.")

        factory.pere_complete(resource)

    def complete_free_factories(self, 
                        find_resource: Optional[str],
                        new_resource: str,
                        count: int,
                        produce_status: bool = False
                        ):
        """ Переукомплектовать фабрики с типом ресурса (без него) на новый ресурс.
            Запускает этап комплектации.
        """

        free_factories: list[Factory] = []
        for f in self.get_factories():
            if f.complectation == find_resource and f.produce == produce_status:
                free_factories.append(f)

        print(f'find_resource: {find_resource}, new_resource: {new_resource}, count: {count}, produce_status: {produce_status}')
        print(f"Found {len(free_factories)} free factories for re-complectation.")

        limit = 0
        for factory in free_factories:
            if limit >= count: break

            limit += 1
            factory.pere_complete(new_resource)

    def auto_manufacturing(self, factory_id: int, status: bool):
        """ Включает или выключает авто производство на фабрике с указанным ID.
        """

        factory = Factory(factory_id).reupdate()
        if not factory:
            raise ValueError("Фабрика не найдена.")
        if factory.company_id != self.id:
            raise ValueError("Фабрика не принадлежит этой компании.")

        factory.set_auto(status)

    def factory_set_produce(self, factory_id: int, produce: bool):
        """ Включает или выключает производство на фабрике с указанным ID.
        """

        factory = Factory(factory_id).reupdate()
        if not factory:
            raise ValueError("Фабрика не найдена.")
        if factory.company_id != self.id:
            raise ValueError("Фабрика не принадлежит этой компании.")

        factory.set_produce(produce)

    def get_contracts(self) -> list['Contract']:
        """ Получает все контракты компании """
        from game.contract import Contract

        contracts: list[Contract] = just_db.find(
            Contract.__tablename__, to_class=Contract,
            supplier_company_id=self.id
        ) # type: ignore

        contracts += just_db.find(
            Contract.__tablename__, to_class=Contract,
            customer_company_id=self.id
        ) # type: ignore

        return contracts

    def get_max_contracts(self) -> int:
        """ Получает максимальное количество активных контрактов """
        contracts_level = self.get_improvements().get('contracts', 1)
        contracts_config = IMPROVEMENTS.contracts.levels.get(str(contracts_level))
        
        if not contracts_config or contracts_config.max is None:
            return 5  # По умолчанию 5 контрактов (уровень 1)
        
        return contracts_config.max

    def can_create_contract(self) -> bool:
        """ Проверяет, может ли компания создать новый контракт """

        return len(self.get_contracts()) < self.get_max_contracts()

    def on_new_game_stage(self, step: int):
        """ Вызывается при переходе на новый игровой этап.
            Обновляет доходы, списывает налоги и т.д.
        """
        from game.contract import Contract

        self.last_turn_income = self.this_turn_income
        self.this_turn_income = 0

        session = session_manager.get_session(self.session_id)
        if not session:
            raise ValueError("Сессия не найдена.")

        if step != 1:
            if self.last_turn_income >= CAPITAL.bank.tax.big_on:
                self.business_type = "big"
                self.save_to_base()
                self.reupdate()

        self.deposit_income_step()  # Начисляем проценты по вкладам
        self.credit_paid_step()
        self.taxate()

        cell_info = self.get_my_cell_info()
        if cell_info:
            resource_id = cell_info.resource_id

            mod = session.get_event_effects().get(
                'resource_extraction_speed', 1.0
            )

            cell_type = self.get_cell_type()
            if session.get_event().get('cell_type') == cell_type:
                mod *= session.get_event().get('income_multiplier', 1.0)

            raw_col = int(self.raw_in_step() * mod)

            if resource_id and raw_col > 0:
                try:
                    self.add_resource(resource_id, raw_col)
                except Exception as e: 
                    max_col = self.get_warehouse_free_size()
                    if max_col > 0:
                        self.add_resource(resource_id, max_col)

        factories = self.get_factories()
        for factory in factories:
            factory.on_new_game_stage()

        contracts = self.get_contracts()
        for contract in contracts:
            contract: Contract
            contract.on_new_game_step()

    @property
    def exchages(self) -> list['Exchange']:
        from game.exchange import Exchange

        exchanges = just_db.find(
            Exchange.__tablename__, to_class=Exchange,
            company_id = self.id,
            session_id=self.session_id
        )

        return exchanges

    def to_dict(self):
        """Возвращает полный статус компании со всеми данными"""
        return {
            # Основная информация
            "id": self.id,
            "name": self.name,
            "owner": self.owner,
            "session_id": self.session_id,
            "secret_code": self.secret_code,
            
            # Финансовые данные
            "balance": self.balance,
            "last_turn_income": self.last_turn_income,
            "this_turn_income": self.this_turn_income,
            "business_type": self.business_type,
            "economic_power": self.economic_power,
            
            # Репутация и статус
            "reputation": self.reputation,
            "in_prison": self.in_prison,
            "prison_end_step": self.prison_end_step,
            
            # Позиция и местоположение
            "cell_position": self.cell_position,
            "position_coords": self.get_position(),
            "cell_type": self.get_cell_type(),
            "cell_info": self.get_my_cell_info().__dict__ if self.get_my_cell_info() else None,
            
            # Налоги
            "tax_debt": self.tax_debt,
            "overdue_steps": self.overdue_steps,
            "tax_rate": self.business_tax(),
            
            # Кредиты и депозиты
            "credits": self.credits,
            "deposits": self.deposits,
            
            # Улучшения и ресурсы
            "improvements": self.improvements,
            "improvements_data": self.get_improvements(),
            "warehouses": self.warehouses,
            "warehouse_capacity": self.get_max_warehouse_size(),
            "warehouse_free_size": self.get_warehouse_free_size(),
            "resources_amount": self.get_resources_amount(),
            "raw_per_turn": self.raw_in_step(),
            
            # Пользователи и фабрики
            "users": [user.to_dict() for user in self.users],
            "factories": [factory.to_dict() for factory in self.get_factories()],
            "factories_count": len(self.get_factories()),
            
            # Дополнительные возможности
            "can_user_enter": self.can_user_enter(),

            "exchages": self.exchages
        }