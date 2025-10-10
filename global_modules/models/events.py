from dataclasses import dataclass, field
from typing import Optional, Dict
from enum import Enum


class EventCategory(str, Enum):
    """Категория события"""
    POSITIVE = "positive"  # Положительное событие
    NEGATIVE = "negative"  # Отрицательное событие


class EventType(str, Enum):
    """Тип события"""
    CELL_TYPE_EVENT = "cell_type_event"  # События для конкретных типов клеток
    GLOBAL_EVENT = "global_event"  # Глобальные события


@dataclass
class EventDuration:
    """Длительность события в годах"""
    min: int | None = field(default=None)
    max: int | None = field(default=None)


@dataclass
class EventEffects:
    """Эффекты события"""
    # Модификаторы дохода для cell_type_event
    income_multiplier: float | None = field(default=None)
    
    # Модификаторы цены и спроса на предметы
    increase_price: dict[str, float] = field(default_factory=dict)
    increase_demand: dict[str, float] = field(default_factory=dict)

    # Модификаторы скорости и лимитов
    tasks_speed: float | None = field(default=None)
    resource_extraction_speed: float | None = field(default=None)
    contracts_limit_decrease: int | None = field(default=None)

    # Логистика
    cell_logistics: float | None = field(default=None)

    # Налоги
    tax_rate_small: float | None = field(default=None)
    tax_rate_large: float | None = field(default=None)

    @classmethod
    def load_from_json(cls, data: dict):
        return cls(
            income_multiplier=data.get("income_multiplier"),
            increase_price=data.get("increase_price", {}),
            increase_demand=data.get("increase_demand", {}),
            tasks_speed=data.get("tasks_speed"),
            resource_extraction_speed=data.get("resource_extraction_speed"),
            contracts_limit_decrease=data.get("contracts_limit_decrease"),
            cell_logistics=data.get("cell_logistics"),
            tax_rate_small=data.get("tax_rate_small"),
            tax_rate_large=data.get("tax_rate_large")
        )


@dataclass
class Event:
    """Базовая модель события"""
    id: str
    name: str
    description: str
    type: EventType
    category: EventCategory
    cell_type: str | None = field(default=None)
    predictability: bool = field(default=False)
    effects: EventEffects = field(default_factory=EventEffects)
    duration: EventDuration = field(default_factory=EventDuration)

    @classmethod
    def load_from_json(cls, event_id: str, data: dict):
        event_type = EventType(data.get("type", "global_event"))
        category = EventCategory(data.get("category", "neutral"))
        
        # Загружаем duration
        duration_data = data.get("duration", {})
        duration = EventDuration(
            min=duration_data.get("min"),
            max=duration_data.get("max")
        )
        
        # Загружаем effects
        effects_data = data.get("effects", {})
        effects = EventEffects.load_from_json(effects_data)
        
        return cls(
            id=event_id,
            name=data.get("name", ""),
            description=data.get("description", ""),
            type=event_type,
            category=category,
            cell_type=data.get("cell_type"),
            predictability=data.get("predictability", False),
            effects=effects,
            duration=duration
        )


@dataclass
class Events:
    """Все события в игре"""
    events: dict[str, Event] = field(default_factory=dict)

    @classmethod
    def load_from_json(cls, data: dict):
        events = {}
        events_data = data.get("events", {})
        
        for event_id, event_data in events_data.items():
            events[event_id] = Event.load_from_json(event_id, event_data)

        return cls(events=events)