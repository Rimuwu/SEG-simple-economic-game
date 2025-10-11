from dataclasses import dataclass
from typing import Dict


@dataclass
class StartImprovementsLevel:
    """Начальные уровни улучшений"""
    warehouse: int
    contracts: int
    station: int
    factory: int


@dataclass
class Settings:
    """Игровые настройки"""
    players_wait_minutes: int  # Время ожидания игроков в минутах
    max_companies: int  # Максимальное количество компаний
    map_side: int  # Размер стороны карты (NxN)
    turn_cell_time_minutes: int  # Время на выбор клетки в минутах
    cell_on_company: int  # Количество клеток на компанию (НЕ ИСПОЛЬЗУЕТСЯ)
    time_on_game_stage: int  # Время на 1 игровой этап в минутах
    time_on_change_stage: int  # Время на смену этапа в минутах
    max_players_in_company: int  # Максимальное количество игроков в компании
    start_improvements_level: StartImprovementsLevel  # Начальные уровни улучшений
    max_credits_per_company: int  # Максимальное количество кредитов на компанию
    start_complectation: Dict[str, str]  # Начальная комплектация
    logistics_speed: int  # Скорость логистики (чем больше, тем быстрее)

    @classmethod
    def load_from_json(cls, data: dict):
        start_improvements = StartImprovementsLevel(**data["start_improvements_level"])

        return cls(
            players_wait_minutes=data["players_wait_minutes"],
            max_companies=data["max_companies"],
            map_side=data["map_side"],
            turn_cell_time_minutes=data["turn_cell_time_minutes"],
            cell_on_company=data["cell_on_company"],
            time_on_game_stage=data["time_on_game_stage"],
            time_on_change_stage=data["time_on_change_stage"],
            max_players_in_company=data["max_players_in_company"],
            start_improvements_level=start_improvements,
            max_credits_per_company=data['max_credits_per_company'],
            start_complectation=data['start_complectation'],
            logistics_speed=data['logistics_speed']
        )