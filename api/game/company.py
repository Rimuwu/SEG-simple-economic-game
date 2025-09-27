import asyncio
from global_modules.models.cells import Cells
from modules.generate import generate_number
from modules.websocket_manager import websocket_manager
from global_modules.db.baseclass import BaseClass
from modules.json_database import just_db
from game.session import session_manager
from global_modules.load_config import ALL_CONFIGS, Resources, Improvements, Settings, Capital, Reputation
from global_modules.bank import calc_credit, get_credit_conditions, check_max_credit_steps

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

    def create(self, name: str, session_id: str):
        self.name = name
        self.id = just_db.max_id_in_table(
            self.__tablename__) + 1

        with_this_name = just_db.find_one(
            self.__tablename__, name=name)
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

        self.save_to_base()
        self.reupdate()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-create_company",
            "data": {
                'session_id': self.session_id,
                'company': self.__dict__
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

        return [user for user in just_db.find(
            "users", to_class=User, company_id=self.id)]

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

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-company_deleted",
            "data": {
                "company_id": self.id
            }
        }))
        return True

    def get_max_warehouse_size(self):
        # TODO: учитывать улучшения склада
        return 100

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

    def get_resources(self):
        return {res_id: RESOURCES.get_resource(res_id) for res_id in self.warehouses.keys()}

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
        if self.reputation < amount:
            raise ValueError("Not enough reputation to remove.")

        old_reputation = self.reputation
        self.reputation -= amount
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

    def take_credit(self, c_sum: int, steps: int):
        """ 
            Сумма кредита у нас между минимумом и максимумом
            Количество шагов у нас 
        """
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

    def credit_paid_step(self):
        """ Вызывается при каждом шаге игры для компании.
            Начисляет плату по кредитам, если они есть.
        """

        for index, credit in enumerate(self.credits):

            if credit["steps_now"] <= credit["steps_total"]:
                credit["need_pay"] += credit["total_to_pay"] - credit['paid'] // (credit["steps_total"] - credit["steps_now"])

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

        pass

    def apply_credit_penalty(self):
        """ Применяет наказание за неуплату кредитов
        """

        pass

    def to_prison(self):
        """ Сажает компанию в тюрьму за неуплату кредитов
        """

        # Сажается на Х ходов и после шедулером выкидывается с пустой компанией

        pass

    def business_type(self):
        """ Тип бизнеса в соответсвии с доходов за прошлый ход (малый, большой)
        """

        pass

    def taxate(self):
        """ Начисляет налоги в зависимости от типа бизнеса. Вызывается каждый ход.
        """

        pass

    def pay_taxes(self, amount: int):
        """ Платит указанную сумму по налогам.
        """

        pass

    def take_deposit(self, d_sum: int):
        """ 
            Сумма депозита у нас между минимумом и максимумом
        """

        pass

    def withdraw_deposit(self, deposit_index: int):
        """ Забирает депозит с индексом deposit_index.
        """

        pass


    def get_factories(self):
    
        pass

    def complect_factory(self, factory_id: str, resource: str):
    
        pass

    def auto_manufacturing(self, factory_id: str):
        """ Запускает автоматическое производство на фабрике с указанным ID.
        """

        pass

    def sell_on_market(self, 
                       resource: str, amount: int, price_per_unit: int | str,
                       type: str  # "sell" | "exchange"
                       ):
        """ Выставляет товар на биржу от компании. (Продажа)
        """

        pass

    def buy_from_market(self, 
                         order_id: int, amount: int
                         ):
        """ Покупает товар с биржи от компании.
        """

        pass

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