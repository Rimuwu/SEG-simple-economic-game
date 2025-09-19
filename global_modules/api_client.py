import asyncio
import websockets
import json
import time
from typing import Callable, Dict, Any, Optional
from os import getenv
import logging


class WebSocketClient:
    """
    Простой WebSocket клиент с поддержкой декораторов для обработки сообщений
    """

    def __init__(self, uri: str, client_id: str, logger = None):
        self.uri = uri
        self.client_id = client_id
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.connected = False
        self.message_handlers: Dict[str, Callable] = {}
        self.logger = logger or logging.getLogger(__name__)

        self._on_connect: Optional[Callable] = None
        self._on_disconnect: Optional[Callable] = None

        # Регистрируем базовые обработчики
        self._register_base_handlers()

    def _register_base_handlers(self):
        """Регистрируем базовые обработчики сообщений"""

        @self.on_message("error")
        async def handle_error(data):
            self.logger.error(f"Ошибка от сервера: {data.get('message', '')}")

    def on_message(self, message_type: str):
        """
        Декоратор для регистрации обработчиков сообщений
        
        Пример использования:
        @client.on_message("broadcast")
        async def handle_broadcast(data):
            print(f"Получено broadcast: {data['content']}")
        """
        def decorator(func: Callable):
            self.message_handlers[message_type] = func
            return func
        return decorator

    def on_event(self, event_type: str):
        """
        Декоратор для регистрации обработчиков событий (подключение, отключение)

        Пример использования:
        @client.on_event("connect")
        async def on_connect():
            print("Подключено к серверу")
        """
        def decorator(func: Callable):
            if event_type == "connect":
                self._on_connect = func
            elif event_type == "disconnect":
                self._on_disconnect = func
            return func
        return decorator

    async def connect(self) -> bool:
        """Подключение к WebSocket серверу"""
        try:
            full_uri = f"{self.uri}?client_id={self.client_id}"
            self.logger.info(f"Подключение к {full_uri}")

            self.websocket = await websockets.connect(full_uri)
            self.connected = True

            if self._on_connect: await self._on_connect()

            # Запускаем прослушивание сообщений в фоне
            asyncio.create_task(self._listen_messages())

            return True

        except Exception as e:
            self.logger.error(f"Ошибка подключения: {e}")
            return False

    async def disconnect(self):
        """Отключение от сервера"""
        if self.websocket and self.connected:
            await self.websocket.close()
            self.connected = False
            self.logger.info("Отключен от сервера")

            if self._on_disconnect: await self._on_disconnect()

    async def _listen_messages(self):
        """Прослушивание входящих сообщений"""
        try:
            async for message in self.websocket:
                await self._handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            self.logger.warning("Соединение закрыто сервером")
            self.connected = False
            await self._on_disconnect()

        except Exception as e:
            self.logger.error(f"Ошибка при прослушивании: {e}")
            self.connected = False

    async def _handle_message(self, message: str):
        """Обработка полученного сообщения"""
        try:
            data = json.loads(message)
            message_type = data.get("type", "unknown")
            
            # Вызываем зарегистрированный обработчик
            if message_type in self.message_handlers:
                handler = self.message_handlers[message_type]
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            else:
                # Обработчик по умолчанию
                if getenv("DEBUG") == 'true':
                    self.logger.debug(f"Нет обработчика для типа '{message_type}': {data}")

        except json.JSONDecodeError:
            self.logger.warning(f"Получено не-JSON сообщение: {message}")
        except Exception as e:
            self.logger.error(f"Ошибка обработки сообщения: {e}")

    async def send_message(self, message_type: str, content: str = "", **kwargs) -> bool:
        """
        Отправка сообщения на сервер
        
        Args:
            message_type: Тип сообщения (ping, broadcast, private, echo)
            content: Содержимое сообщения
            **kwargs: Дополнительные параметры (например, target для private)
        """
        if not self.connected or not self.websocket:
            self.logger.error("Нет подключения к серверу")
            return False

        try:
            message = {
                "type": message_type,
                "content": content,
                "timestamp": time.time(),
                **kwargs
            }

            await self.websocket.send(json.dumps(message, ensure_ascii=False))

            if getenv("DEBUG") == 'true':
                self.logger.debug(f"Отправлено: {message_type}")

            return True

        except Exception as e:
            self.logger.error(f"Ошибка отправки сообщения: {e}")
            return False

    async def ping(self) -> bool: return await self.send_message("ping")

    def is_connected(self) -> bool: return self.connected

    def get_client_id(self) -> str: return self.client_id

# Фабричная функция для создания клиента
def create_client(uri: str = "ws://localhost:8000/ws/connect", 
                 client_id: str = None,
                 logger = None) -> WebSocketClient:
    """
    Создать WebSocket клиент

    Args:
        uri: URI WebSocket сервера
        client_id: ID клиента (если None, будет сгенерирован)

    Returns:
        WebSocketClient
    """
    if client_id is None:
        client_id = f"client_{int(time.time())}"

    return WebSocketClient(uri, client_id, logger)