import json
from pathlib import Path

from global_modules.models.cells import Cells
from global_modules.models.capital import Capital
from global_modules.models.improvements import Improvements
from global_modules.models.reputation import Reputation
from global_modules.models.resources import Resources
from global_modules.models.settings import Settings


def load_json(filename: str, config_dir: Path) -> dict:
    with open(config_dir / filename, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = [line[:line.index('//')] if '//' in line else line for line in content.split('\n')]
    return json.loads('\n'.join(lines))


def load_configs(config_dir: str = "config"):
    config_path = Path(config_dir)
    if not config_path.exists():
        config_path = Path(__file__).parent.parent / "config"

    cells = Cells.load_from_json(
        load_json("cells.json", config_path))
    capital = Capital.load_from_json(
        load_json("capital.json", config_path))
    improvements = Improvements.load_from_json(
        load_json("improvements.json", config_path))
    reputation = Reputation.load_from_json(
        load_json("reputation.json", config_path))
    resources = Resources.load_from_json(
        load_json("resources.json", config_path))
    settings = Settings.load_from_json(
        load_json("settings.json", config_path))

    return cells, capital, improvements, reputation, resources, settings


def get_configs(config_dir: str = "config"):
    CELLS_CONFIG, CAPITAL_CONFIG, IMPROVEMENTS_CONFIG, REPUTATION_CONFIG, RESOURCES_CONFIG, SETTINGS_CONFIG = load_configs(config_dir)

    ALL_CONFIGS = {
        "cells": CELLS_CONFIG,
        "capital": CAPITAL_CONFIG,
        "improvements": IMPROVEMENTS_CONFIG,
        "reputation": REPUTATION_CONFIG,
        "resources": RESOURCES_CONFIG,
        "settings": SETTINGS_CONFIG
    }

    return ALL_CONFIGS

ALL_CONFIGS = get_configs()