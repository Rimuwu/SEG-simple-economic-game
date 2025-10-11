
import asyncio
from typing import Optional
from global_modules.db.baseclass import BaseClass
from global_modules.models.resources import Production, Resource
from modules.json_database import just_db
from global_modules.load_config import ALL_CONFIGS, Resources, Improvements, Settings, Capital, Reputation
from modules.function_way import *
from modules.websocket_manager import websocket_manager

RESOURCES: Resources = ALL_CONFIGS["resources"]
IMPROVEMENTS: Improvements = ALL_CONFIGS['improvements']
REPUTATION: Reputation = ALL_CONFIGS['reputation']

class Contract(BaseClass):
    """ Контракт между компаниями
        
        X товара типа Z за Y монет каждый ход
        
        Жизненный цикл контракта:
        1. Создание (create) - контракт создается без оплаты с accepted=False
        2. Принятие (accept_contract) с полной оплатой или отклонение (decline_contract)
        3. Выполнение (execute_turn) каждый ход - только если принят
        4. При неудаче поставки - если за ход не выполнены этап поставки, отмена с возвратом части денег и штрафом репутации
        5. При успешном завершении - удаление и повышение репутации
        6. Непринятые контракты удаляются в конце хода

    """

    __tablename__ = "contracts"
    __unique_id__ = "id"
    __db_object__ = just_db

    def __init__(self, id: int = 0):
        self.id: int = id

        self.supplier_company_id: int = 0  # Компания-поставщик
        self.customer_company_id: int = 0  # Компания-заказчик
        self.session_id: str = ""  # Сессия, в которой создан контракт

        # Что поставляется
        self.resource: str = ""  # Тип ресурса
        self.amount_per_turn: int = 0  # Количество за ход

        # Условия оплаты (только монеты)
        self.payment_amount: int = 0  # Сумма денег

        # Параметры контракта
        self.duration_turns: int = 0  # Длительность в ходах
        self.created_at_step: int = 0  # Ход создания
        self.accepted: bool = False  # Принял ли поставщик контракт
        self.delivered_this_turn: bool = False  # Отправлен ли продукт в текущем ходу
        
        self.successful_deliveries: int = 0  # Количество успешных поставок

    def create(self, supplier_company_id: int, customer_company_id: int, session_id: str,
               resource: str, amount_per_turn: int, duration_turns: int, payment_amount: int):
        """ Создание нового контракта

        Args:
            supplier_company_id: ID компании-поставщика
            customer_company_id: ID компании-заказчика  
            session_id: ID сессии
            resource: Тип ресурса для поставки
            amount_per_turn: Количество за ход
            duration_turns: Длительность в ходах
            payment_amount: Сумма денег за контракт
        """
        from game.company import Company
        from game.session import session_manager
        
        # Валидация
        if amount_per_turn <= 0 or duration_turns <= 0:
            raise ValueError("Количество и длительность должны быть положительными")

        if payment_amount <= 0:
            raise ValueError("Сумма оплаты должна быть положительной")

        if RESOURCES.get_resource(resource) is None:
            raise ValueError(f"Ресурс {resource} не существует")
        
        if supplier_company_id == customer_company_id:
            raise ValueError("Компания не может заключить контракт с самой собой")
        
        supplier = Company(_id=supplier_company_id).reupdate()
        customer = Company(_id=customer_company_id).reupdate()
        
        if not supplier or not customer:
            raise ValueError("Одна из компаний не найдена")
        
        session = session_manager.get_session(session_id)
        if not session:
            raise ValueError("Сессия не найдена")
        
        # Создаём контракт (без предоплаты)
        self.id = just_db.max_id_in_table(self.__tablename__) + 1
        self.supplier_company_id = supplier_company_id
        self.customer_company_id = customer_company_id
        self.session_id = session_id

        self.resource = resource
        self.amount_per_turn = amount_per_turn
        self.payment_amount = payment_amount

        self.duration_turns = duration_turns
        self.created_at_step = session.step
    
        self.accepted = False  # По умолчанию контракт не принят
        self.delivered_this_turn = False  # Продукт не отправлен в текущем ходу

        self.save_to_base()
        self.reupdate()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-contract_created",
            "data": {
                "session_id": self.session_id,
                "contract": self.to_dict()
            }
        }))

        return self

    def execute_turn(self):
        """ Выполнение поставки за текущий ход """
        from game.company import Company
        from game.session import session_manager
        
        session = session_manager.get_session(self.session_id)
        if not session:
            raise ValueError("Сессия не найдена")

        # Проверяем, принят ли контракт
        if not self.accepted:
            raise ValueError("Контракт не принят")

        # Проверяем, не был ли уже отправлен в этом ходе
        if self.delivered_this_turn:
            raise ValueError("Продукт уже отправлен в этом ходе")
        
        supplier = Company(_id=self.supplier_company_id
                           ).reupdate()
        customer = Company(_id=self.customer_company_id
                           ).reupdate()

        if not supplier or not customer:
            # Отменяем контракт с возвратом
            self.delete()
            return False

        # Проверяем наличие ресурса у поставщика
        supplier_resource_amount = supplier.warehouses.get(
            self.resource, 0
            )

        if supplier_resource_amount < self.amount_per_turn:
            # Сразу отменяем контракт с возвратом части денег и штрафом репутации
            raise ValueError("У поставщика недостаточно ресурса для выполнения контракта")

        # Выполняем поставку (игнорируем ограничения склада заказчика)
        try:
            try:
                supplier.remove_resource(self.resource, self.amount_per_turn)
            except ValueError:
                raise ValueError("Ошибка при списании ресурса у поставщика")

            # Пытаемся добавить ресурс заказчику, сколько поместится
            try:
                customer.add_resource(self.resource, self.amount_per_turn)
            except ValueError:
                # Если места нет, добавляем сколько можем
                free_space = customer.get_warehouse_free_size()
                if free_space > 0:
                    customer.add_resource(self.resource, 
                        min(free_space, self.amount_per_turn)
                                          )

            self.successful_deliveries += 1
            self.delivered_this_turn = True

            # Если это была последняя поставка
            if self.duration_turns == self.successful_deliveries:
                # Добавляем репутацию за успешное выполнение
                supplier.add_reputation(
                    REPUTATION.contract.completed
                )

                self.delete()
                return True

            self.save_to_base()
            self.reupdate()

            asyncio.create_task(websocket_manager.broadcast({
                "type": "api-contract_executed",
                "data": {
                    "session_id": self.session_id,
                    "contract_id": self.id,
                    "success": True,
                    "step": session.step
                }
            }))
            
            return True

        except ValueError:
            # При ошибке отменяем контракт
            raise ValueError("Ошибка при выполнении контракта")

    def accept_contract(self):
        """ Принятие контракта поставщиком """
        if self.accepted:
            raise ValueError("Контракт уже принят")
        
        if self.successful_deliveries > 0:
            raise ValueError("Контракт уже начал выполняться")
        
        # Проверяем и снимаем полную оплату с заказчика
        from game.company import Company
        
        supplier = Company(_id=self.supplier_company_id
                           ).reupdate()
        customer = Company(_id=self.customer_company_id
                           ).reupdate()
        
        if not supplier or not customer:
            raise ValueError("Одна из компаний не найдена")

        if customer.balance < self.payment_amount:
            raise ValueError("У заказчика недостаточно средств для оплаты контракта")
        
        try:
            customer.remove_balance(self.payment_amount)
            supplier.add_balance(self.payment_amount)
        except ValueError as e:
            raise ValueError(f"Ошибка оплаты: {e}")

        self.accepted = True
        self.save_to_base()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-contract_accepted",
            "data": {
                "session_id": self.session_id,
                "contract_id": self.id
            }
        }))
        
        return self

    def decline_contract(self):
        """ Отклонение контракта поставщиком """
        if self.accepted:
            raise ValueError("Нельзя отклонить уже принятый контракт")
        
        if self.successful_deliveries > 0:
            raise ValueError("Контракт уже начал выполняться")
        
        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-contract_declined",
            "data": {
                "session_id": self.session_id,
                "contract_id": self.id
            }
        }))
        
        self.delete()
        return self

    def cancel_with_refund(self):
        """ Отмена контракта с возвратом части денег и штрафом репутации """
        from game.company import Company
        
        supplier = Company(_id=self.supplier_company_id).reupdate()
        customer = Company(_id=self.customer_company_id).reupdate()

        not_executed = self.duration_turns - self.successful_deliveries

        if supplier and customer:
            # Возвращаем деньги за оставшиеся поставки
            if not_executed <= 0:
                refund_amount = 0
            else:
                refund_amount = self.payment_amount // not_executed

            try:
                if supplier.balance >= refund_amount:
                    supplier.remove_balance(refund_amount)
                    customer.add_balance(refund_amount)
                # Штраф репутации за невыполнение
                supplier.remove_reputation(
                    REPUTATION.contract.failed
                )
            except ValueError:
                # Если не удалось вернуть деньги - больший штраф
                supplier.remove_reputation(
                    REPUTATION.contract.failed * 2
                    )

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-contract_cancelled",
            "data": {
                "session_id": self.session_id,
                "contract_id": self.id,
                "reason": "Поставщик не смог выполнить поставку"
            }
        }))

        self.delete()
        return self

    def on_new_game_step(self):
        """ Проверка контракта при новом ходе

            Сбрасывает статус доставки
            Удаляет непринятые контракты в конце хода
        """
        from game.session import session_manager

        # Если контракт не принят в конце хода - удаляем
        if not self.accepted:
            asyncio.create_task(websocket_manager.broadcast({
                "type": "api-contract_expired",
                "data": {
                    "session_id": self.session_id,
                    "contract_id": self.id,
                    "reason": "Контракт не был принят до конца хода"
                }
            }))
            
            self.delete()
            return True  # Контракт удален

        else:
            if not self.delivered_this_turn:
                # Отменяем контракт с возвратом части денег и штрафом репутации
                self.cancel_with_refund()
                return True

            self.delivered_this_turn = False
            self.save_to_base()
            return True

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "supplier_company_id": self.supplier_company_id,
            "customer_company_id": self.customer_company_id,
            "session_id": self.session_id,
            "resource": self.resource,
            "amount_per_turn": self.amount_per_turn,
            "payment_amount": self.payment_amount,
            "duration_turns": self.duration_turns,
            "created_at_step": self.created_at_step,
            "accepted": self.accepted,
            "delivered_this_turn": self.delivered_this_turn
        }

    def delete(self):
        just_db.delete(self.__tablename__, id=self.id)
        del self