"""
WebSocket клиент для взаимодействия с игровым сервером
Адаптирован из bot/modules/ws_client.py для обучения нейросети
"""
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import sys
from pathlib import Path

# Добавляем путь к global_modules (когда запуск из /ai-trainer/)
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

import time
import asyncio
from typing import Optional, Any, Dict, List
from global_modules.api_client import create_client
from global_modules.logs import Logger

UPDATE_PASSWORD = os.getenv("UPDATE_PASSWORD", "supersecret")

# Настройка логирования
ai_logger = Logger.get_logger("ai_trainer")

# Создаем WebSocket клиента
ws_client = create_client(
    client_id=f"ai_trainer_{int(time.time())}", 
    uri=os.getenv("WS_SERVER_URI", "ws://localhost:81/ws/connect"),
    logger=ai_logger
)


class AIGameClient:
    """Клиент для взаимодействия AI с игровым сервером"""
    
    def __init__(self, training_mode: bool = True, skip_timers: bool = True):
        """
        Инициализация клиента
        
        Args:
            training_mode: Если True, используется режим обучения
            skip_timers: Если True, пропускаются таймауты между действиями
        """
        self.training_mode = training_mode
        self.skip_timers = skip_timers
        self.current_company = None
        self.current_session = None
    
    # ==================== УПРАВЛЕНИЕ СЕССИЕЙ ====================
    
    async def create_session(self, session_id: Optional[str] = None) -> Dict:
        """Создание сессии"""
        return await ws_client.send_message(
            "create-session",
            session_id=session_id,
            password=UPDATE_PASSWORD,
            wait_for_response=True
        )
    
    async def get_session(self, session_id: Optional[str] = None, stage: Optional[str] = None) -> Dict:
        """Получение информации о сессии"""
        return await ws_client.send_message(
            "get-session",
            session_id=session_id,
            stage=stage,
            wait_for_response=True
        )
    
    # ==================== УПРАВЛЕНИЕ КОМПАНИЯМИ ====================
    
    async def create_company(self, name: str, 
                             who_create: int = 0,
                             session_id: Optional[str] = None) -> Dict:
        """Создание компании"""
        session = session_id or self.current_session
        return await ws_client.send_message(
            "create-company",
            name=name,
            who_create=who_create,  # 0 для системного создания
            session_id=session,
            password=UPDATE_PASSWORD,
            wait_for_response=True
        )
    
    async def get_company(self, id: Optional[int] = None, name: Optional[str] = None, 
                         session_id: Optional[str] = None) -> Dict:
        """Получение информации о компании"""
        return await ws_client.send_message(
            "get-company",
            id=id,
            name=name,
            session_id=session_id,
            wait_for_response=True
        )
    
    async def set_company_position(self, company_id: int, x: int, y: int) -> Dict:
        """Обновление местоположения компании"""
        return await ws_client.send_message(
            "set-company-position",
            company_id=company_id,
            x=x,
            y=y,
            password=UPDATE_PASSWORD,
            wait_for_response=True
        )
    
    async def get_company_improvement_info(self, company_id: int) -> Dict:
        """Получение информации о улучшениях компании"""
        return await ws_client.send_message(
            "get-company-improvement-info",
            company_id=company_id,
            wait_for_response=True
        )
    
    async def update_company_improve(self, company_id: int, improvement_type: str) -> Dict:
        """Улучшение компании"""
        return await ws_client.send_message(
            "update-company-improve",
            company_id=company_id,
            improvement_type=improvement_type,
            password=UPDATE_PASSWORD,
            wait_for_response=True
        )
    
    async def company_take_credit(self, company_id: int, amount: int, period: int) -> Dict:
        """Получение кредита компанией"""
        return await ws_client.send_message(
            "company-take-credit",
            company_id=company_id,
            amount=amount,
            period=period,
            password=UPDATE_PASSWORD,
            wait_for_response=True
        )
    
    async def company_pay_credit(self, company_id: int, credit_index: int, amount: int) -> Dict:
        """Погашение кредита компанией"""
        return await ws_client.send_message(
            "company-pay-credit",
            company_id=company_id,
            credit_index=credit_index,
            amount=amount,
            password=UPDATE_PASSWORD,
            wait_for_response=True
        )
    
    async def company_pay_taxes(self, company_id: int, amount: int) -> Dict:
        """Погашение налогов компанией"""
        return await ws_client.send_message(
            "company-pay-taxes",
            company_id=company_id,
            amount=amount,
            password=UPDATE_PASSWORD,
            wait_for_response=True
        )
    
    # ==================== РАБОТА С БИРЖЕЙ ====================
    
    async def get_exchanges(self, session_id: Optional[str] = None, company_id: Optional[int] = None,
                           sell_resource: Optional[str] = None, offer_type: Optional[str] = None) -> Dict:
        """Получить список предложений биржи с фильтрацией"""
        return await ws_client.send_message(
            "get-exchanges",
            session_id=session_id,
            company_id=company_id,
            sell_resource=sell_resource,
            offer_type=offer_type,
            wait_for_response=True
        )
    
    async def create_exchange_offer(self, company_id: int, session_id: str, 
                                   sell_resource: str, sell_amount_per_trade: int,
                                   count_offers: int, offer_type: str,
                                   price: Optional[int] = None,
                                   barter_resource: Optional[str] = None,
                                   barter_amount: Optional[int] = None) -> Dict:
        """Создать предложение на бирже"""
        return await ws_client.send_message(
            "create-exchange-offer",
            company_id=company_id,
            session_id=session_id,
            sell_resource=sell_resource,
            sell_amount_per_trade=sell_amount_per_trade,
            count_offers=count_offers,
            offer_type=offer_type,
            price=price,
            barter_resource=barter_resource,
            barter_amount=barter_amount,
            password=UPDATE_PASSWORD,
            wait_for_response=True
        )
    
    async def buy_exchange_offer(self, offer_id: int, buyer_company_id: int, quantity: int) -> Dict:
        """Купить предложение с биржи"""
        return await ws_client.send_message(
            "buy-exchange-offer",
            offer_id=offer_id,
            buyer_company_id=buyer_company_id,
            quantity=quantity,
            password=UPDATE_PASSWORD,
            wait_for_response=True
        )
    
    # ==================== РАБОТА С ГОРОДАМИ ====================
    
    async def get_cities(self, session_id: Optional[str] = None) -> Dict:
        """Получение списка городов"""
        return await ws_client.send_message(
            "get-cities",
            session_id=session_id,
            wait_for_response=True
        )
    
    async def get_city_demands(self, city_id: int) -> Dict:
        """Получение спроса города на товары"""
        return await ws_client.send_message(
            "get-city-demands",
            city_id=city_id,
            wait_for_response=True
        )
    
    async def sell_to_city(self, city_id: int, company_id: int, 
                          resource_id: str, amount: int) -> Dict:
        """Продажа ресурса городу"""
        return await ws_client.send_message(
            "sell-to-city",
            city_id=city_id,
            company_id=company_id,
            resource_id=resource_id,
            amount=amount,
            password=UPDATE_PASSWORD,
            wait_for_response=True
        )
    
    # ==================== РАБОТА С ФАБРИКАМИ ====================
    
    async def get_factories(self, company_id: Optional[int] = None,
                           complectation: Optional[str] = None,
                           produce: Optional[bool] = None,
                           is_auto: Optional[bool] = None) -> Dict:
        """Получение списка фабрик"""
        return await ws_client.send_message(
            "get-factories",
            company_id=company_id,
            complectation=complectation,
            produce=produce,
            is_auto=is_auto,
            wait_for_response=True
        )
    
    async def factory_recomplectation(self, factory_id: int, new_complectation: str) -> Dict:
        """Перекомплектация фабрики"""
        return await ws_client.send_message(
            "factory-recomplectation",
            factory_id=factory_id,
            new_complectation=new_complectation,
            password=UPDATE_PASSWORD,
            wait_for_response=True
        )
    
    async def factory_set_produce(self, factory_id: int, produce: bool) -> Dict:
        """Установка статуса производства фабрики"""
        return await ws_client.send_message(
            "factory-set-produce",
            factory_id=factory_id,
            produce=produce,
            wait_for_response=True
        )
    
    # ==================== УТИЛИТЫ ====================
    
    async def connect(self):
        """Подключение к WebSocket серверу"""
        try:
            await ws_client.connect()
            ai_logger.info("Подключено к игровому серверу")
        except Exception as e:
            ai_logger.error(f"Ошибка при подключении: {e}")
            raise
    
    async def disconnect(self):
        """Отключение от WebSocket сервера"""
        try:
            await ws_client.disconnect()
            ai_logger.info("Отключено от игрового сервера")
        except Exception as e:
            ai_logger.error(f"Ошибка при отключении: {e}")
            raise
