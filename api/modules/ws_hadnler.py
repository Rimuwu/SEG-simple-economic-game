# Реестр обработчиков сообщений
from typing import Callable, Dict, List, Union
from modules.websocket_manager import websocket_manager
from global_modules.logs import main_logger

MESSAGE_HANDLERS: Dict[str, dict[str, Union[Callable, str]]] = {}

def message_handler(message_type: str, 
                    doc: str = "", 
                    datatypes: list[str] = [],
                    messages: list[dict] = []
                    ):
    """
    Декоратор для регистрации обработчиков сообщений

    Пример использования:
    @message_handler("ping")
    async def handle_ping(client_id: str, message: dict):
        # обработка ping сообщений
        pass
    
    Args:
        message_type: Тип сообщения, который будет обрабатываться
        doc: Описание обработчика
        datatypes: Список типов данных, которые ожидает обработчик [user_id: int, action: Optional[str], ...]
        messages: На какие типы сообщений отправляет ответ при обработке
    """
    def decorator(func: Callable):
        MESSAGE_HANDLERS[message_type] = {
            "handler": func, "doc": doc,
            "datatypes": datatypes,
            "messages": messages
            }
        main_logger.info(f"Зарегистрирован обработчик для типа сообщения: {message_type}")
        return func
    return decorator

async def handle_message(client_id: str, message: dict):
    """
    Обработчик входящих сообщений от клиентов через систему декораторов
    
    Args:
        client_id: ID клиента, отправившего сообщение
        message: Сообщение от клиента
    """
    message_type = message.get("type", "unknown")

    # Ищем зарегистрированный обработчик
    if message_type in MESSAGE_HANDLERS:
        try:
            handler = MESSAGE_HANDLERS[message_type]["handler"]
            result = await handler(client_id, message)

            if 'request_id' in message:
                # Если есть request_id, отправляем ответ
                response = {
                    "type": "response",
                    "request_id": message["request_id"],
                    "data": result
                }
                await websocket_manager.send_message(client_id, response)

        except Exception as e:
            main_logger.error(f"Ошибка в обработчике {message_type}: {e}")
            error_message = {
                "type": "error",
                "message": f"Ошибка обработки сообщения типа {message_type}: {str(e)}"
            }
            await websocket_manager.send_message(client_id, error_message)
    else:
        # Неизвестный тип сообщения
        main_logger.warning(f"Неизвестный тип сообщения от {client_id}: {message_type}")

        available_types = []
        for m_type in MESSAGE_HANDLERS.keys():
            available_types.append(m_type)

        error_message = {
            "type": "error",
            "message": f"Неизвестный тип сообщения: {message_type}",
            "available_types": available_types
        }
        await websocket_manager.send_message(client_id, error_message)

# Функция для получения списка зарегистрированных обработчиков
def get_registered_handlers() -> List[str]:
    """Получить список всех зарегистрированных типов сообщений"""
    return MESSAGE_HANDLERS