
import asyncio
from typing import Optional, Literal
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

class Exchange(BaseClass):
    """ Логика
        - Выставляем предложение
        - Другая компания отправляет запрос на покупку (деньги списываются сразу)
        - Компания принимает / отклоняет сделку
        - - Если принимает, то в течение хода надо отправить товар
        - - Если не отправляет, то репутация падает, сделка закрывается, деньги возвращаются
        - - Если отклоняет, то деньги возвращаются покупателю

        Максимальное время жизни запроса - 3 хода. Если за это время заказ не принят, деньги возвращаются покупателю и снимается запрос.

        Типы сделок:
        - За монеты (Х товара типа Z на Y монет)
        - Бартер (Х товара типа Z на Y продукта J)
    """

    __tablename__ = "exchange"
    __unique_id__ = "id"
    __db_object__ = just_db

    def __init__(self, id: int = 0):
        self.id: int = id
        self.seller_company_id: int = 0  # ID компании-продавца
        self.buyer_company_id: Optional[int] = None  # ID компании-покупателя (None если еще не принята)
        
        # Тип сделки: "money" (за монеты) или "barter" (бартер)
        self.deal_type: Literal["money", "barter"] = "money"
        
        # Что продается
        self.offer_resource_type: str = ""  # Тип ресурса
        self.offer_resource_amount: int = 0  # Количество ресурса
        
        # Что требуется взамен
        self.price_money: int = 0  # Цена в монетах (для типа "money")
        self.price_resource_type: str = ""  # Тип ресурса для бартера (для типа "barter")
        self.price_resource_amount: int = 0  # Количество ресурса для бартера (для типа "barter")
        
        # Статус сделки: "active" (выставлена), "pending" (ожидает отправки товара), 
        # "completed" (выполнена), "rejected" (отклонена), "failed" (не выполнена в срок)
        self.status: Literal["active", "pending", "completed", "rejected", "failed"] = "active"
        
        # Список запросов на покупку от других компаний
        # Структура: [{"company_id": int, "created_turn": int}, ...]
        self.purchase_requests: list[dict] = []
        
        # Для отслеживания выполнения сделки
        self.delivery_deadline_turn: Optional[int] = None  # До какого хода нужно отправить товар
        self.goods_sent: bool = False  # Отправлен ли товар
        
        # Ход создания предложения
        self.created_turn: int = 0

    def create(self, seller_company_id: int, offer_resource_type: str, 
               offer_resource_amount: int, deal_type: Literal["money", "barter"],
               price_money: int = 0, price_resource_type: str = "", 
               price_resource_amount: int = 0, current_turn: int = 0):
        """ Создание новой сделки
        
        Args:
            seller_company_id: ID компании-продавца
            offer_resource_type: Тип предлагаемого ресурса
            offer_resource_amount: Количество предлагаемого ресурса
            deal_type: Тип сделки ("money" или "barter")
            price_money: Цена в монетах (для типа "money")
            price_resource_type: Тип требуемого ресурса (для типа "barter")
            price_resource_amount: Количество требуемого ресурса (для типа "barter")
            current_turn: Текущий ход игры
        """
        # Валидация входных данных
        if offer_resource_type not in RESOURCES.resources:
            raise ValueError(f"Invalid resource type: {offer_resource_type}")
        
        if offer_resource_amount <= 0:
            raise ValueError("Resource amount must be positive")
        
        if deal_type not in ["money", "barter"]:
            raise ValueError("Deal type must be 'money' or 'barter'")
        
        if deal_type == "money" and price_money <= 0:
            raise ValueError("Price must be positive for money deals")
        
        if deal_type == "barter":
            if price_resource_type not in RESOURCES.resources:
                raise ValueError(f"Invalid price resource type: {price_resource_type}")
            if price_resource_amount <= 0:
                raise ValueError("Price resource amount must be positive")
        
        # Создаем сделку (без проверки наличия товара и без резервирования)
        self.id = self.__db_object__.max_id_in_table(self.__tablename__) + 1
        self.seller_company_id = seller_company_id
        self.offer_resource_type = offer_resource_type
        self.offer_resource_amount = offer_resource_amount
        self.deal_type = deal_type
        self.price_money = price_money
        self.price_resource_type = price_resource_type
        self.price_resource_amount = price_resource_amount
        self.status = "active"
        self.created_turn = current_turn

        self.save_to_base()
        self.reupdate()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-exchange-create",
            "data": {
                "exchange": self.to_dict()
            }
        }))

        return self

    def add_purchase_request(self, buyer_company_id: int, current_turn: int):
        """ Добавление запроса на покупку от компании
        
        Args:
            buyer_company_id: ID компании-покупателя
            current_turn: Текущий ход игры
        """
        if self.status != "active":
            raise ValueError("Exchange is not active")
        
        if buyer_company_id == self.seller_company_id:
            raise ValueError("Seller cannot buy from themselves")
        
        # Проверяем, что запрос еще не был отправлен
        for request in self.purchase_requests:
            if request["company_id"] == buyer_company_id:
                raise ValueError("Purchase request already exists")
        
        # Проверяем, что у покупателя достаточно средств/ресурсов
        from game.company import Company
        buyer = Company(buyer_company_id)
        buyer.reupdate()
        
        if self.deal_type == "money":
            if buyer.balance < self.price_money:
                raise ValueError("Buyer doesn't have enough money")
            # Резервируем деньги покупателя
            buyer.balance -= self.price_money
        else:  # barter
            if buyer.warehouses.get(self.price_resource_type, 0) < self.price_resource_amount:
                raise ValueError("Buyer doesn't have enough resources")
            # Резервируем ресурсы покупателя
            buyer.warehouses[self.price_resource_type] = buyer.warehouses.get(self.price_resource_type, 0) - self.price_resource_amount
        
        buyer.save_to_base()
        
        self.purchase_requests.append({
            "company_id": buyer_company_id,
            "created_turn": current_turn
        })
        
        self.save_to_base()
        self.reupdate()
        
        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-exchange-purchase-request",
            "data": {
                "exchange_id": self.id,
                "buyer_company_id": buyer_company_id
            }
        }))

    def accept_deal(self, buyer_company_id: int, current_turn: int):
        """ Принятие сделки продавцом
        
        Args:
            buyer_company_id: ID компании-покупателя
            current_turn: Текущий ход игры
        """
        if self.status != "active":
            raise ValueError("Exchange is not active")
        
        # Проверяем, что есть запрос от этого покупателя
        request_found = False
        for request in self.purchase_requests:
            if request["company_id"] == buyer_company_id:
                request_found = True
                break
        
        if not request_found:
            raise ValueError("No purchase request from this buyer")
        
        # Отклоняем все остальные запросы и возвращаем средства
        for request in self.purchase_requests:
            if request["company_id"] != buyer_company_id:
                self._refund_buyer(request["company_id"])
        
        # Устанавливаем покупателя и меняем статус
        self.buyer_company_id = buyer_company_id
        self.status = "pending"
        self.delivery_deadline_turn = current_turn + 1  # Нужно отправить в течение следующего хода
        
        self.save_to_base()
        self.reupdate()
        
        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-exchange-accepted",
            "data": {
                "exchange_id": self.id,
                "buyer_company_id": buyer_company_id
            }
        }))

    def reject_deal(self, buyer_company_id: int):
        """ Отклонение сделки продавцом
        
        Args:
            buyer_company_id: ID компании-покупателя, чей запрос отклоняется
        """
        if self.status != "active":
            raise ValueError("Exchange is not active")
        
        # Проверяем, что есть запрос от этого покупателя
        request_found = False
        request_to_remove = None
        for request in self.purchase_requests:
            if request["company_id"] == buyer_company_id:
                request_found = True
                request_to_remove = request
                break
        
        if not request_found:
            raise ValueError("No purchase request from this buyer")
        
        # Возвращаем средства покупателю
        self._refund_buyer(buyer_company_id)
        
        # Удаляем запрос из списка
        if request_to_remove is not None:
            self.purchase_requests.remove(request_to_remove)
        
        self.save_to_base()
        self.reupdate()
        
        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-exchange-rejected",
            "data": {
                "exchange_id": self.id,
                "buyer_company_id": buyer_company_id
            }
        }))

    def cancel_deal(self):
        """ Отмена сделки продавцом (до принятия какого-либо запроса)
        """
        if self.status != "active":
            raise ValueError("Can only cancel active exchanges")
        
        # Возвращаем средства всем покупателям, отправившим запросы
        for request in self.purchase_requests:
            self._refund_buyer(request["company_id"])
        
        self.status = "rejected"
        self.save_to_base()
        self.reupdate()
        
        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-exchange-cancelled",
            "data": {
                "exchange_id": self.id
            }
        }))

    def send_goods(self):
        """ Отправка товара покупателю
        """
        if self.status != "pending":
            raise ValueError("Exchange is not in pending state")
        
        from game.company import Company
        seller = Company(self.seller_company_id)
        seller.reupdate()
        
        # Проверяем наличие товара у продавца
        if seller.warehouses.get(self.offer_resource_type, 0) < self.offer_resource_amount:
            raise ValueError("Seller doesn't have enough resources")
        
        # Помечаем товар как отправленный
        self.goods_sent = True
        
        # Сразу завершаем сделку
        self._complete_deal()

    def _refund_buyer(self, buyer_company_id: int):
        """ Возврат средств покупателю
        
        Args:
            buyer_company_id: ID компании-покупателя
        """
        from game.company import Company
        buyer = Company(buyer_company_id)
        buyer.reupdate()
        
        if self.deal_type == "money":
            buyer.balance += self.price_money
        else:  # barter
            buyer.warehouses[self.price_resource_type] = buyer.warehouses.get(self.price_resource_type, 0) + self.price_resource_amount
        
        buyer.save_to_base()

    def _complete_deal(self):
        """ Завершение сделки (перевод средств и ресурсов)
        """
        from game.company import Company
        
        seller = Company(self.seller_company_id)
        seller.reupdate()
        
        if self.buyer_company_id is None:
            raise ValueError("Buyer company ID is not set")
        
        buyer = Company(self.buyer_company_id)
        buyer.reupdate()
        
        # Проверяем наличие товара у продавца (проверка только при отправке)
        if seller.warehouses.get(self.offer_resource_type, 0) < self.offer_resource_amount:
            # Недостаточно товара - сделка провалена
            self._fail_deal()
            return
        
        # Вычитаем товар у продавца
        seller.warehouses[self.offer_resource_type] = seller.warehouses.get(self.offer_resource_type, 0) - self.offer_resource_amount
        
        # Покупатель получает товар
        buyer.warehouses[self.offer_resource_type] = buyer.warehouses.get(self.offer_resource_type, 0) + self.offer_resource_amount
        
        # Продавец получает оплату
        if self.deal_type == "money":
            seller.balance += self.price_money
        else:  # barter
            seller.warehouses[self.price_resource_type] = seller.warehouses.get(self.price_resource_type, 0) + self.price_resource_amount
        
        seller.save_to_base()
        buyer.save_to_base()
        
        self.status = "completed"
        self.goods_sent = True
        
        self.save_to_base()
        self.reupdate()
        
        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-exchange-completed",
            "data": {
                "exchange_id": self.id
            }
        }))

    def _fail_deal(self):
        """ Провал сделки (не отправлен товар в срок)
        """
        from game.company import Company
        
        seller = Company(self.seller_company_id)
        seller.reupdate()
        
        if self.buyer_company_id is None:
            raise ValueError("Buyer company ID is not set")
        
        buyer = Company(self.buyer_company_id)
        buyer.reupdate()
        
        # Возвращаем оплату покупателю
        if self.deal_type == "money":
            buyer.balance += self.price_money
        else:  # barter
            buyer.warehouses[self.price_resource_type] = buyer.warehouses.get(self.price_resource_type, 0) + self.price_resource_amount
        
        # Снижаем репутацию продавца
        reputation_penalty = 10  # Штраф за невыполнение сделки
        seller.reputation -= reputation_penalty
        
        seller.save_to_base()
        buyer.save_to_base()
        
        self.status = "failed"
        
        self.save_to_base()
        self.reupdate()
        
        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-exchange-failed",
            "data": {
                "exchange_id": self.id
            }
        }))

    def to_dict(self) -> dict:
        """ Преобразование объекта в словарь
        """
        return {
            "id": self.id,
            "seller_company_id": self.seller_company_id,
            "buyer_company_id": self.buyer_company_id,
            "deal_type": self.deal_type,
            "offer_resource_type": self.offer_resource_type,
            "offer_resource_amount": self.offer_resource_amount,
            "price_money": self.price_money,
            "price_resource_type": self.price_resource_type,
            "price_resource_amount": self.price_resource_amount,
            "status": self.status,
            "purchase_requests": self.purchase_requests,
            "delivery_deadline_turn": self.delivery_deadline_turn,
            "goods_sent": self.goods_sent,
            "created_turn": self.created_turn
        }

    def delete(self):
        """ Удаление сделки
        """
        # Если сделка активна или в ожидании, нужно вернуть средства
        if self.status == "active":
            for request in self.purchase_requests:
                self._refund_buyer(request["company_id"])
        
        elif self.status == "pending":
            if self.buyer_company_id:
                self._refund_buyer(self.buyer_company_id)
        
        self.__db_object__.delete(self.__tablename__, **{self.__unique_id__: self.id})
        return True
    
    def on_end_game_stage(self, current_turn: int):
        """ Проверка сделки в конце хода
        
        Args:
            current_turn: Текущий ход игры
        """
        if self.status == "active":
            # Проверяем запросы на покупку - удаляем те, что старше 3 ходов
            expired_requests = []
            for request in self.purchase_requests:
                if current_turn - request["created_turn"] >= 3:
                    expired_requests.append(request)
            
            # Возвращаем деньги по истекшим запросам
            for request in expired_requests:
                self._refund_buyer(request["company_id"])
                self.purchase_requests.remove(request)
            
            if expired_requests:
                self.save_to_base()
                self.reupdate()
                
        elif self.status == "pending":
            # Проверяем, истек ли срок доставки
            if self.delivery_deadline_turn and current_turn > self.delivery_deadline_turn:
                if not self.goods_sent:
                    # Сделка провалена
                    self._fail_deal()
                else:
                    # Сделка выполнена (на случай если товар был отправлен, но _complete_deal не был вызван)
                    self._complete_deal()
            elif self.goods_sent:
                # Товар отправлен до истечения срока (на случай если _complete_deal не был вызван)
                self._complete_deal()