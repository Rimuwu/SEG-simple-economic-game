"""
Модуль для работы с ресурсами игры.
Использует конфигурацию из global_modules/load_config.py
"""
from global_modules.load_config import ALL_CONFIGS
from global_modules.models.resources import Resources, Resource

# Получаем объект Resources из конфигурации
_resources_config: Resources = ALL_CONFIGS['resources']

# Создаем словарь для быстрого доступа в старом формате (для совместимости)
RESOURCES = {}
for resource_key, resource_obj in _resources_config.resources.items():
    RESOURCES[resource_key] = {
        "name": resource_obj.label,
        "emoji": resource_obj.emoji,
        "basePrice": resource_obj.basePrice,
        "massModifier": resource_obj.massModifier,
        "raw": resource_obj.raw,
        "lvl": resource_obj.lvl
    }
    if resource_obj.production:
        RESOURCES[resource_key]["production"] = {
            "materials": resource_obj.production.materials,
            "turns": resource_obj.production.turns,
            "output": resource_obj.production.output
        }


def get_resource_name(resource_key: str) -> str:
    """Получить русское название ресурса с эмодзи"""
    resource_obj = _resources_config.get_resource(resource_key)
    if resource_obj:
        return f"{resource_obj.emoji} {resource_obj.label}"
    return f"📦 {resource_key}"


def get_resource_emoji(resource_key: str) -> str:
    """Получить только эмодзи ресурса"""
    resource_obj = _resources_config.get_resource(resource_key)
    if resource_obj:
        return resource_obj.emoji
    return "📦"


def get_resource(resource_key: str) -> Resource | None:
    """Получить объект ресурса"""
    return _resources_config.get_resource(resource_key)


def get_raw_resources() -> dict[str, Resource]:
    """Получить все сырьевые ресурсы"""
    return _resources_config.get_raw_resources()


def get_produced_resources() -> dict[str, Resource]:
    """Получить все производимые ресурсы"""
    return _resources_config.get_produced_resources()
