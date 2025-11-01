from game.session import SessionObject
from global_modules.db.baseclass import BaseClass
from modules.db import just_db

class Statistic(BaseClass, SessionObject):

    __tablename__ = "statistics"
    __unique_id__ = "id"
    __db_object__ = just_db

    def __init__(self, id: int = 0):
        self.id: int = id

        self.session_id: str = ""
        self.company_id: int = 0
        self.stage: int = 0
        
        self.balance: int = 0 # Баланс компании
        self.reputation: int = 0 # Репутация компании
        self.economic_power: int = 0 # Экономическая мощь компании
        self.tax_debt: int = 0 # Налоговый долг компании
        self.credits: int = 0 # Количество кредитов компании
        self.deposits: int = 0 # Количество депозитов компании
        self.in_prison: bool = False # Находится ли компания в тюрьме
        self.business_type: str = "" # Тип бизнеса компании

        self.factories: int = 0 # Количество фабрик компании
        self.exchanges: int = 0 # Количество бирж компании
        self.contracnts: int = 0 # Количество контрактов компании
        self.warehouse: int = 0 # Размер склада компании

        self.product_count: int = 0 # Объем производства продуктов компанией
        self.sell_to_city: int = 0 # Объем продаж в город компанией

    async def create(self, 
                     company_id: int, 
                     session_id: str,
                     stage: int,
                     data: dict = {}
                     ):

        self.company_id = company_id
        self.session_id = session_id
        self.stage = stage

        find_res: dict = await just_db.find_one(self.__tablename__,
                                  company_id=company_id,
                                  session_id=session_id,
                                  stage=stage
                                  ) # type: ignore

        if find_res is not None:
            return self.load_from_base(find_res)

        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

        await just_db.insert(self.__tablename__, self.to_dict())
        return self

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "company_id": self.company_id,
            "stage": self.stage,
            "balance": self.balance,
            "reputation": self.reputation,
            "economic_power": self.economic_power,
            "tax_debt": self.tax_debt,
            "credits": self.credits,
            "deposits": self.deposits,
            "in_prison": self.in_prison,
            "business_type": self.business_type,
            "factories": self.factories,
            "exchanges": self.exchanges,
            "contracnts": self.contracnts,
            "warehouse": self.warehouse
        }

    async def delete(self):
        await just_db.delete(self.__tablename__, id=self.id, session_id=self.session_id)
        return True

    @classmethod
    async def get_all_by_company(cls, session_id: str, company_id: int) -> list['Statistic']:
        rows: list[dict] = await just_db.find(cls.__tablename__, 
                                  session_id=session_id, company_id=company_id) # type: ignore
        statistics = []

        for row in rows:
            stat = cls()
            stat = stat.load_from_base(row)
            statistics.append(stat)

        return statistics

    @classmethod
    async def update_me(cls,
                        company_id: int,
                        session_id: str,
                        stage: int,
                        **kwargs
                        ):

        stat: Statistic = await just_db.find_one(cls.__tablename__,
                                     company_id=company_id,
                                     session_id=session_id,
                                     stage=stage,
                                     to_class=Statistic
                                     ) # type: ignore

        for key, value in kwargs.items():

            if not hasattr(stat, key):
                setattr(stat, key, value)
            else:
                if isinstance(stat.__dict__[key], dict) and isinstance(value, dict):
                    stat.__dict__[key].update(value)

                elif isinstance(stat.__dict__[key], list) and isinstance(value, list):
                    stat.__dict__[key].extend(value)

                elif isinstance(stat.__dict__[key], (int, float)) and isinstance(value, (int, float)):
                    stat.__dict__[key] += value

                else:
                    if hasattr(stat, key):
                        stat.__dict__[key] = value

        await stat.save_to_base()
        return stat