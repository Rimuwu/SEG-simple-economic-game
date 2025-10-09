import json
import os

# Путь к файлу с ресурсами
RESOURCES_PATH = os.path.join(os.path.dirname(__file__), '..', 'json', 'resources.json')

# Загрузка ресурсов из JSON
def load_resources():
    """Загрузить маппинг ресурсов из JSON файла"""
    with open(RESOURCES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

# Глобальный объект с ресурсами
RESOURCES = load_resources()

def get_resource_name(resource_key: str) -> str:
    """Получить русское название ресурса с эмодзи"""
    resource_info = RESOURCES.get(resource_key, {"name": resource_key, "emoji": "📦"})
    return f"{resource_info['emoji']} {resource_info['name']}"

def get_resource_emoji(resource_key: str) -> str:
    """Получить только эмодзи ресурса"""
    resource_info = RESOURCES.get(resource_key, {"emoji": "📦"})
    return resource_info['emoji']
