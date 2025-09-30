from dataclasses import dataclass, field
from typing import Dict, Optional, Any
import json


@dataclass
class FunctionWorker:
    """Класс для описания функций-обработчиков"""
    function: Optional[str] = None

@dataclass
class SceneSettings:
    """Настройки сцены"""
    parse_mode: Optional[str] = None
    delete_after_send: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SceneSettings':
        """Создание объекта из словаря"""

        return cls(
            parse_mode=data.get('parse_mode', None),
            delete_after_send=data.get('delete_after_send', False)
        )


@dataclass
class ScenePage:
    """Страница сцены"""
    content: str
    image: Optional[str] = None
    to_pages: Dict[str, str] = field(default_factory=dict)
    content_worker: Optional[FunctionWorker] = None
    buttons_worker: Optional[FunctionWorker] = None
    text_waiter: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScenePage':
        """Создание объекта из словаря"""
        content_worker = None
        if 'content-worker' in data:
            content_worker = FunctionWorker(**data['content-worker'])

        buttons_worker = None
        if 'buttons-worker' in data:
            buttons_worker = FunctionWorker(**data['buttons-worker'])

        return cls(
            image=data['image'],
            content=data['content'],
            to_pages=data.get('to_pages', {}),
            content_worker=content_worker,
            buttons_worker=buttons_worker,
            text_waiter=data.get('text-waiter')
        )


@dataclass
class SceneModel:
    """Основной класс сцены"""
    name: str
    settings: SceneSettings
    pages: Dict[str, ScenePage]

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> 'SceneModel':
        """Создание сцены из словаря"""
        settings = SceneSettings.from_dict(data['settings'])

        pages = {}
        for page_name, page_data in data['pages'].items():
            pages[page_name] = ScenePage.from_dict(page_data)

        return cls(
            name=name,
            settings=settings,
            pages=pages
        )

    def get_page(self, page_name: str) -> Optional[ScenePage]:
        """Получение страницы по имени"""
        return self.pages.get(page_name)

    def get_main_page(self) -> Optional[ScenePage]:
        """Получение главной страницы (первой в списке)"""
        if self.pages:
            return next(iter(self.pages.values()))
        return None


@dataclass
class SceneLoader:
    """Класс для загрузки сцен из JSON"""
    scenes: Dict[str, SceneModel] = field(default_factory=dict)

    def load_from_file(self, file_path: str) -> None:
        """Загрузка сцен из JSON файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Удаляем комментарии из JSON
                content = f.read()
                lines = content.split('\n')
                cleaned_lines = []
                for line in lines:
                    # Удаляем комментарии начинающиеся с //
                    if '//' in line:
                        line = line[:line.index('//')]
                    cleaned_lines.append(line)

                cleaned_content = '\n'.join(cleaned_lines)
                data = json.loads(cleaned_content)

            self.scenes.clear()
            for scene_name, scene_data in data.items():
                self.scenes[scene_name] = SceneModel.from_dict(scene_name, scene_data)

        except FileNotFoundError:
            raise FileNotFoundError(f"Файл конфигурации сцен не найден: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка парсинга JSON: {e}")
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки сцен: {e}")

    def get_scene(self, scene_name: str) -> Optional[SceneModel]:
        """Получение сцены по имени"""
        return self.scenes.get(scene_name)

    def get_all_scenes(self) -> Dict[str, SceneModel]:
        """Получение всех загруженных сцен"""
        return self.scenes.copy()

    def reload_from_file(self, file_path: str) -> None:
        """Перезагрузка сцен из файла"""
        self.load_from_file(file_path)

scenes_loader = SceneLoader()
scenes_loader.load_from_file('json/scenes.json')
print(
    "[SceneLoader] Loaded scenes: ", len(scenes_loader.scenes)
)