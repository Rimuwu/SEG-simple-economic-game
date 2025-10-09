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
from global_modules.bank import calc_credit, get_credit_conditions, check_max_credit_steps
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

        self.in_prison: bool = False

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
            raise ValueError("Owner is already set.")
        if user_id in [user.id for user in self.users] is False:
            raise ValueError("User is not a member of the company.")

        self.owner = user_id
        self.save_to_base()

    def create(self, name: str, session_id: str):
        self.name = name
        self.id = just_db.max_id_in_table(
            self.__tablename__) + 1

        with_this_name = just_db.find_one(
            self.__tablename__, name=name, session_id=session_id)
        if with_this_name:
            raise ValueError(f"Company with name '{name}' already exists.")

        session = session_manager.get_session(session_id)
        if not session or not session.can_add_company():
            raise ValueError("Invalid or inactive session for adding a company.")
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
            raise ValueError("Coordinates must be integers.")

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

    def add_resource(self, resource: str, amount: int):
        if RESOURCES.get_resource(resource) is None:
            raise ValueError(f"Resource '{resource}' does not exist.")
        if amount <= 0:
            raise ValueError("Amount must be a positive integer.")
        if self.get_resources_amount() + amount > self.get_max_warehouse_size():
            raise ValueError("Not enough space in the warehouse.")

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
            raise ValueError(f"Resource '{resource}' does not exist.")
        if amount <= 0:
            raise ValueError("Amount must be a positive integer.")
        if resource not in self.warehouses or self.warehouses[resource] < amount:
            raise ValueError(f"Not enough of resource '{resource}' to remove.")

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

    def add_balance(self, amount: int):
        if not isinstance(amount, int):
            raise ValueError("Amount must be an integer.")
        if amount <= 0:
            raise ValueError("Amount must be a positive integer.")

        old_balance = self.balance
        self.balance += amount
        self.this_turn_income += amount

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
            raise ValueError("Amount must be an integer.")
        if amount <= 0:
            raise ValueError("Amount must be a positive integer.")
        if self.balance < amount:
            raise ValueError("Not enough balance to remove.")

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
            raise ValueError("Cannot determine cell type for improvements.")

        if imp_lvl_now is None:
            raise ValueError(f"Improvement type '{improvement_type}' not found.")

        imp_next_lvl = IMPROVEMENTS.get_improvement(
                cell_type, improvement_type, 
                str(imp_lvl_now + 1)
            )

        if imp_next_lvl is None:
            raise ValueError(f"No next level for improvement '{improvement_type}'.")

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
            raise ValueError("Amount must be an integer.")
        if amount <= 0:
            raise ValueError("Amount must be a positive integer.")

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
            raise ValueError("Amount must be an integer.")
        if amount <= 0:
            raise ValueError("Amount must be a positive integer.")

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
            raise ValueError("Sum and steps must be integers.")
        if c_sum <= 0 or steps <= 0:
            raise ValueError("Sum and steps must be positive integers.")

        credit_condition = get_credit_conditions(self.reputation)
        if not credit_condition.possible:
            raise ValueError("Credit is not possible with the current reputation.")

        total, pay_per_turn, extra = calc_credit(
            c_sum, credit_condition.without_interest, credit_condition.percent, steps
            )

        session = session_manager.get_session(self.session_id)
        if not session:
            raise ValueError("Session not found.")

        if not check_max_credit_steps(steps, 
                                      session.step, 
                                      session.max_steps):
            raise ValueError("Credit duration exceeds the maximum game steps.")

        if len(self.credits) >= SETTINGS.max_credits_per_company:
            raise ValueError("Maximum number of active credits reached for this company.")

        self.credits.append(
            {
                "total_to_pay": total,
                "need_pay": 0,
                "paid": 0,

                "steps_total": steps,
                "steps_now": 0
            }
        )
        
        self.save_to_base()
        self.add_balance(c_sum)
        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-company_credit_taken",
            "data": {
                "company_id": self.id,
                "amount": c_sum,
                "steps": steps
            }
        }))

    def credit_paid_step(self):
        """ Вызывается при каждом шаге игры для компании.
            Начисляет плату по кредитам, если они есть.
        """

        for index, credit in enumerate(self.credits):

            if credit["steps_now"] <= credit["steps_total"]:
                credit["need_pay"] += (credit["total_to_pay"] - credit['need_pay'] - credit ['paid']) // (credit["steps_total"] - credit["steps_now"])

            elif credit["steps_now"] > credit["steps_total"]:
                credit["need_pay"] += credit["total_to_pay"] - credit['paid']
                self.remove_reputation(REPUTATION.credit.lost)

            if credit["steps_now"] - credit["steps_total"] > REPUTATION.credit.max_overdue:
                self.remove_reputation(self.reputation)
                self.remove_credit(index)
                self.to_prison()

            credit["steps_now"] += 1

        self.save_to_base()
        self.reupdate()

    def remove_credit(self, credit_index: int):
        """ Удаляет кредит с индексом credit_index.
        """

        if credit_index < 0 or credit_index >= len(self.credits):
            raise ValueError("Invalid credit index.")

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
            raise ValueError("Credit index and amount must be integers.")
        if credit_index < 0 or credit_index >= len(self.credits):
            raise ValueError("Invalid credit index.")
        if amount <= 0:
            raise ValueError("Amount must be a positive integer.")
        if self.balance < amount:
            raise ValueError("Not enough balance to pay credit.")

        credit = self.credits[credit_index]

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
            raise ValueError("Session not found.")

        self.in_prison = True
        self.save_to_base()
        self.reupdate()

        session.create_step_schedule(
            session.step + REPUTATION.prison.stages,
            leave_from_prison,
            session_id=self.session_id,
            company_id=self.id
        )

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-company_to_prison",
            "data": {
                "company_id": self.id
            }
        }))

    def leave_prison(self):
        """ Выход из тюрьмы по времени
        """

        if not self.in_prison:
            raise ValueError("Company is not in prison.")

        self.in_prison = False
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
            raise ValueError("Company is already in prison.")

        return self.in_prison

    def business_tax(self):
        """ Определяет налоговую ставку в зависимости от типа бизнеса.
        """

        if self.business_type == "big":
            return CAPITAL.bank.tax.big_on
        return CAPITAL.bank.tax.small_business

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
            raise ValueError("Amount must be an integer.")
        if amount <= 0:
            raise ValueError("Amount must be a positive integer.")
        if self.tax_debt <= 0:
            raise ValueError("No tax debt to pay.")
        if self.balance < amount:
            raise ValueError("Not enough balance to pay taxes.")

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

    def take_deposit(self, d_sum: int):
        """ 
            Сумма депозита у нас между минимумом и максимумом
        """

        pass

    def withdraw_deposit(self, deposit_index: int):
        """ Забирает депозит с индексом deposit_index.
        """

        pass


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
            raise ValueError("Factory not found.")
        if factory.company_id != self.id:
            raise ValueError("Factory does not belong to this company.")

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
            raise ValueError("Factory not found.")
        if factory.company_id != self.id:
            raise ValueError("Factory does not belong to this company.")

        factory.set_auto(status)

    def factory_set_produce(self, factory_id: int, produce: bool):
        """ Включает или выключает производство на фабрике с указанным ID.
        """

        factory = Factory(factory_id).reupdate()
        if not factory:
            raise ValueError("Factory not found.")
        if factory.company_id != self.id:
            raise ValueError("Factory does not belong to this company.")

        factory.set_produce(produce)

    def create_contract(self, 
                        company_id: int | None, 
                        resource: str, amount: int, price_per_unit: int | str,
                        type: str,  # "sell" | "exchange" 
                        steps: int
                        ):
        """ Создает контракт с другой компанией.
        """

        pass

    def take_contract(self, contract_id: int):
        """ Принимает контракт от другой компании.
        """

        pass

    def cancel_contract(self, contract_id: int):
        """ Отменяет контракт. (Предложенный)
        """

        pass

    def sell_resource_to_city(self, resource: str, 
                              amount: int, city_id: int):
        """ Продает ресурс городу.
        """

        pass

    def get_logistics_resources(self):
        """ Возвращает список логистических транспортных средств компании.
        """

        pass


    def on_new_game_stage(self, step: int):
        """ Вызывается при переходе на новый игровой этап.
            Обновляет доходы, списывает налоги и т.д.
        """

        self.last_turn_income = self.this_turn_income
        self.this_turn_income = 0

        if step != 1:
            if self.last_turn_income >= CAPITAL.bank.tax.big_on:
                self.business_type = "big"
                self.save_to_base()
                self.reupdate()

        self.credit_paid_step()
        self.taxate()

        cell_info = self.get_my_cell_info()
        if cell_info:
            resource_id = cell_info.resource_id 
            raw_col = self.raw_in_step()

            if resource_id and raw_col > 0:
                try:
                    self.add_resource(resource_id, raw_col)
                except Exception as e: 
                    print(f'stage add comp res. of {self.id} error: {e}')

        factories = self.get_factories()
        for factory in factories:
            factory.on_new_game_stage()

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
            
            # Репутация и статус
            "reputation": self.reputation,
            "in_prison": self.in_prison,
            
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