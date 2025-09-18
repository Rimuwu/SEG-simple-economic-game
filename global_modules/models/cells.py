from dataclasses import dataclass, field


@dataclass
class SetLocation:
    start_point: str | None = field(default=None)
    x: int | None = field(default=None)
    y: int | None = field(default=None)

@dataclass
class CellType:
    id: str
    label: str
    resource_id: str | None = field(default=None)
    max_amount: int = field(default=1)
    pickable: bool = field(default=False)
    locations: list[SetLocation] = field(default_factory=list)

    @classmethod
    def load_from_json(cls, data: dict):
        id = data.get("id", "")
        label = data.get("label", "")
        resource_id = data.get("resource")
        max_amount = data.get("max_amount", 1)
        pickable = data.get("pickable", False)
        
        locations = []
        for loc in data.get("locations", []):
            if isinstance(loc, str):
                # Парсим строку формата "center_-1_1" или "center"
                parts = loc.split("_")
                if len(parts) == 1:
                    locations.append(SetLocation(start_point=parts[0]))
                elif len(parts) == 3:
                    locations.append(SetLocation(
                        start_point=parts[0],
                        x=int(parts[1]),
                        y=int(parts[2])
                    ))
            elif isinstance(loc, dict):
                locations.append(SetLocation(**loc))

        return cls(
            id=id,
            label=label,
            resource_id=resource_id,
            max_amount=max_amount,
            pickable=pickable,
            locations=locations
        )


@dataclass
class Cells:
    """Все типы клеток в игре"""
    types: dict[str, CellType] = field(default_factory=dict)

    @classmethod
    def load_from_json(cls, data: dict):
        types = {}
        for cell_id, cell_data in data.items():
            cell_data["id"] = cell_id
            types[cell_id] = CellType.load_from_json(cell_data)
        return cls(types=types)