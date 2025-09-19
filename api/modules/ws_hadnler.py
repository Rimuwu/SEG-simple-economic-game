# Реестр обработчиков сообщений
from typing import Callable, Dict, List
from modules import websocket_manager
from global_modules.logs import main_logger

MESSAGE_HANDLERS: Dict[str, Callable] = {}

def message_handler(message_type: str):
    """
    Декоратор для регистрации обработчиков сообщений

    Пример использования:
    @message_handler("ping")
    async def handle_ping(client_id: str, message: dict):
        # обработка ping сообщений
        pass
    """
    def decorator(func: Callable):
        MESSAGE_HANDLERS[message_type] = func
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
            handler = MESSAGE_HANDLERS[message_type]
            await handler(client_id, message)
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
        error_message = {
            "type": "error",
            "message": f"Неизвестный тип сообщения: {message_type}",
            "available_types": list(MESSAGE_HANDLERS.keys())
        }
        await websocket_manager.send_message(client_id, error_message)

# Функция для получения списка зарегистрированных обработчиков
def get_registered_handlers() -> List[str]:
    """Получить список всех зарегистрированных типов сообщений"""
    return list(MESSAGE_HANDLERS.keys())