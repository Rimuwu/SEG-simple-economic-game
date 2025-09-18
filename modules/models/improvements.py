from dataclasses import dataclass, field


@dataclass
class ImprovementLevel:
    """Уровень улучшения с характеристиками"""
    cost: int
    capacity: int | None = field(default=None)  # Для складов
    max: int | None = field(default=None)  # Для контрактов
    productsPerTurn: int | None = field(default=None)  # Для станций
    tasksPerTurn: int | None = field(default=None)  # Для фабрик
    factories: int | None = field(default=None)  # Для фабрик


@dataclass
class ImprovementType:
    """Тип улучшения со всеми уровнями"""
    levels: dict[str, ImprovementLevel] = field(default_factory=dict)

    @classmethod
    def load_from_json(cls, data: dict):
        levels = {}
        for level_key, level_data in data.items():
            levels[level_key] = ImprovementLevel(**level_data)
        return cls(levels=levels)


@dataclass
class ResourceImprovements:
    """Улучшения для ресурса (станция и фабрика)"""
    station: ImprovementType = field(default_factory=ImprovementType)
    factory: ImprovementType = field(default_factory=ImprovementType)

    @classmethod
    def load_from_json(cls, data: dict):
        station = ImprovementType.load_from_json(data.get("station", {}))
        factory = ImprovementType.load_from_json(data.get("factory", {}))
        return cls(station=station, factory=factory)


@dataclass
class Improvements:
    """Все улучшения в игре"""
    warehouse: ImprovementType = field(default_factory=ImprovementType)
    contracts: ImprovementType = field(default_factory=ImprovementType)
    mountain: ResourceImprovements = field(default_factory=ResourceImprovements)
    forest: ResourceImprovements = field(default_factory=ResourceImprovements)
    water: ResourceImprovements = field(default_factory=ResourceImprovements)
    field: ResourceImprovements = field(default_factory=ResourceImprovements)

    @classmethod
    def load_from_json(cls, data: dict):
        warehouse = ImprovementType.load_from_json(data.get("warehouse", {}))
        contracts = ImprovementType.load_from_json(data.get("contracts", {}))
        mountain = ResourceImprovements.load_from_json(data.get("mountain", {}))
        forest = ResourceImprovements.load_from_json(data.get("forest", {}))
        water = ResourceImprovements.load_from_json(data.get("water", {}))
        field = ResourceImprovements.load_from_json(data.get("field", {}))

        return cls(
            warehouse=warehouse,
            contracts=contracts,
            mountain=mountain,
            forest=forest,
            water=water,
            field=field
        )
