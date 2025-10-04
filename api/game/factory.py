
import asyncio
from typing import Optional
from global_modules.models.cells import Cells
from global_modules.db.baseclass import BaseClass
from global_modules.models.resources import Production, Resource
from modules.json_database import just_db
from global_modules.load_config import ALL_CONFIGS, Resources, Improvements, Settings, Capital, Reputation
from modules.function_way import *
from modules.websocket_manager import websocket_manager

RESOURCES: Resources = ALL_CONFIGS["resources"]
CELLS: Cells = ALL_CONFIGS['cells']
IMPROVEMENTS: Improvements = ALL_CONFIGS['improvements']
SETTINGS: Settings = ALL_CONFIGS['settings']
CAPITAL: Capital = ALL_CONFIGS['capital']
REPUTATION: Reputation = ALL_CONFIGS['reputation']

class Factory(BaseClass):

    __tablename__ = "factories"
    __unique_id__ = "id"
    __db_object__ = just_db

    def __init__(self, id: int = 0):
        self.id: int = id
        self.company_id: int = 0

        self.complectation: Optional[str] = None  # Какая комплектация производится
        self.progress: list[int] = [0, 0]  # [текущий прогресс, прогресс для завершения]

        self.produce: bool = False  # Должна ли фабрика производить продукцию
        self.is_auto: bool = False  # Автоматическое производство

        self.complectation_stages = 0  # Сколько ходов осталось до завершения комплектации

        self.produced: int = 0  # Сколько всего произведено продукции

    def create(self, company_id: int, 
               complectation: Optional[str] = None):
        """ Создание новой фабрики
        """
        if complectation not in RESOURCES.resources and complectation is not None:
            raise ValueError("Invalid complectation type.")

        self.company_id = company_id
        self.complectation = complectation
        self.id = self.__db_object__.max_id_in_table(self.__tablename__) + 1

        if complectation is not None:
            production: Production = RESOURCES.get_resource(complectation).production # type: ignore

            turns = production.turns if production else 0
            self.progress = [0, turns]

        self.save_to_base()
        self.reupdate()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-factory-create",
            "data": {
                "factory": self.status(),
                "company_id": self.company_id
            }
        }))

        return self

    @property
    def is_working(self) -> bool:
        """ Проверка, работает ли фабрика
        """

        if self.complectation_stages > 0: # Если идёт перекомплектация
            return False

        if self.complectation is None: # Если не выбрана комплектация
            return False

        if not self.produce and not self.is_auto: # Если не производит и не авто
            return False

        if not self.check_materials(): # Если нет материалов
            return False

        return True

    def pere_complete(self, new_complectation: str):
        """ Перекомплектация фабрики
        """
        if new_complectation not in RESOURCES.resources:
            raise ValueError("Invalid complectation type.")

        # Проверяем, что ресурс не является сырьем
        new_resource = RESOURCES.get_resource(new_complectation)
        if new_resource.raw:
            raise ValueError("Cannot produce raw resources.")

        # Получаем уровни старой и новой комплектации
        old_level = 0
        if self.complectation is not None:
            old_level = RESOURCES.get_resource(self.complectation).lvl # type: ignore

        new_level = new_resource.lvl # type: ignore

        # Рассчитываем время перекомплектации
        if new_level > old_level:
            self.complectation_stages = new_level - old_level
        else:
            self.complectation_stages = new_level

        self.complectation = new_complectation
        production: Production = new_resource.production # type: ignore
        self.progress = [0, production.turns]

        self.save_to_base()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-factory-start-complectation",
            "data": {
            'factory_id': self.id,
            'company_id': self.company_id
            }
        }))
        return True

    def on_new_game_stage(self):
        from game.company import Company

        company = Company(self.company_id).reupdate()

        # Этап комплектации
        if self.complectation_stages > 0:
            self.complectation_stages -= 1
            self.save_to_base()

            if self.complectation_stages == 0:
                asyncio.create_task(websocket_manager.broadcast({
                    "type": "api-factory-end-complectation",
                    "data": {
                        'factory_id': self.id,
                        'company_id': self.company_id
                    }
                }))

        # Этап производства
        elif self.is_working:
            resource = RESOURCES.get_resource(self.complectation) # type: ignore
            self.progress[0] += 1

            # Снимаем материалы со склада компании при первом ходе производства
            if self.progress[0] == 1:
                materials = resource.production.materials # type: ignore

                for mat, qty in materials.items():
                    company.remove_resource(mat, qty)

            # Если производство завершено - добавляем ресурсы на склад компании
            if self.progress[0] >= self.progress[1]:
                output = resource.production.output # type: ignore

                # Добавляем продукцию на склад компании
                if self.complectation:
                    company.add_resource(
                        self.complectation, output)
                    self.produced += output

                self.progress[0] = 0

                # Если авто, то проверяем материалы и продолжаем производство, если есть материалы
                if self.is_auto and self.check_materials():
                    self.produce = True
                else:
                    self.produce = False

                asyncio.create_task(websocket_manager.broadcast({
                    "type": "api-factory-end-production",
                    "data": {
                        'factory_id': self.id,
                        'company_id': self.company_id
                    }
                }))
            
            self.save_to_base()

    def set_produce(self, produce: bool):
        """ Установка статуса производства фабрики
        """
        if self.progress[0] == 0:
            self.produce = produce
            self.save_to_base()
        else:
            raise ValueError("Can't change produce status during production.")

    def set_auto(self, is_auto: bool):
        """ Установка статуса автоматического производства фабрики
        """
        self.is_auto = is_auto
        self.save_to_base()

    def check_materials(self):
        """ Проверка наличия материалов для производства
        """
        from game.company import Company

        if self.complectation is None:
            raise ValueError("Complectation not set.")

        resource: Resource = RESOURCES.get_resource(self.complectation) # type: ignore
        if not resource.production: return False

        materials = resource.production.materials # type: ignore

        company = Company(self.company_id).reupdate()
        all_good = True
        for mat, qty in materials.items():
            if company.warehouses.get(mat, 0) < qty:
                all_good = False
                break

        return all_good

    def to_dict(self) -> dict:
        """ Получение статуса фабрики
        """
        return {
            "id": self.id,
            "company_id": self.company_id,
            "complectation": self.complectation,
            "progress": self.progress,
            "produce": self.produce,
            "is_auto": self.is_auto,
            "complectation_stages": self.complectation_stages,
            "is_working": self.is_working,
            "check_materials": self.check_materials() if self.complectation else False
        }

    def delete(self):
        """ Удаление фабрики
        """
        company_id = self.company_id
        factory_id = self.id

        self.__db_object__.delete(self.__tablename__, 
                                  **{self.__unique_id__: self.id})

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-factory-delete",
            "data": {
                "factory_id": factory_id,
                "company_id": company_id
            }
        }))

        return True