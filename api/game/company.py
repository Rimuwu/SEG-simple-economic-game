import asyncio
from modules.generate import generate_number
from modules.websocket_manager import websocket_manager
from global_modules.db.baseclass import BaseClass
from modules.json_database import just_db
from game.session import session_manager
from global_modules.load_config import ALL_CONFIGS, Resources

resources: Resources = ALL_CONFIGS["resources"]

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
        if resources.get_resource(resource) is None:
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
        if resources.get_resource(resource) is None:
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
        return {res_id: resources.get_resource(res_id) for res_id in self.warehouses.keys()}

    def get_resources_amount(self):
        count = 0
        for amount in self.warehouses.values(): 
            count += amount
        return count