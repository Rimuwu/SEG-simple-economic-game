from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Production:
    """Производственная цепочка ресурса"""
    materials: Dict[str, int]  # Материалы для производства {ресурс: количество}
    turns: int  # Количество ходов на производство
    output: int  # Количество на выходе


@dataclass
class Resource:
    """Ресурс в игре"""
    label: str  # Название ресурса
    emoji: str  # Эмодзи ресурса
    basePrice: int  # Базовая цена
    massModifier: float  # Модификатор массы
    raw: bool = field(default=False)  # Является ли сырьём
    production: Production | None = field(default=None)  # Производственная цепочка

    @classmethod
    def load_from_json(cls, data: dict):
        production = None
        if "production" in data:
            production = Production(**data["production"])
        
        return cls(
            label=data["label"],
            emoji=data["emoji"],
            basePrice=data["basePrice"],
            massModifier=data["massModifier"],
            raw=data.get("raw", False),
            production=production
        )


@dataclass
class Resources:
    """Все ресурсы в игре"""
    resources: Dict[str, Resource] = field(default_factory=dict)

    @classmethod
    def load_from_json(cls, data: dict):
        resources = {}
        for resource_id, resource_data in data.items():
            resources[resource_id] = Resource.load_from_json(resource_data)
        return cls(resources=resources)

    def get_resource(self, resource_id: str) -> Resource | None:
        """Получить ресурс по ID"""
        return self.resources.get(resource_id)

    def get_raw_resources(self) -> Dict[str, Resource]:
        """Получить все сырьевые ресурсы"""
        return {rid: res for rid, res in self.resources.items() if res.raw}

    def get_produced_resources(self) -> Dict[str, Resource]:
        """Получить все производимые ресурсы"""
        return {rid: res for rid, res in self.resources.items() if res.production is not None}