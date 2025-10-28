"""
Управление хранилищем моделей
Позволяет сохранять и загружать разные версии обученных ботов
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from neural_network import SEGNeuralNetwork


class BotDifficulty(Enum):
    """Уровни сложности ботов"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


@dataclass
class ModelMetadata:
    """Метаданные модели"""
    name: str
    difficulty: str
    version: int
    created_at: str
    trained_episodes: int
    average_reward: float
    best_reward: float
    description: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ModelStorage:
    """Хранилище моделей"""
    
    def __init__(self, models_dir: str = "/models", checkpoints_dir: str = "/checkpoints"):
        """
        Инициализация хранилища
        
        Args:
            models_dir: Директория для сохранения моделей
            checkpoints_dir: Директория для сохранения checkpoint'ов
        """
        self.models_dir = Path(models_dir)
        self.checkpoints_dir = Path(checkpoints_dir)
        self.logger = logging.getLogger("model_storage")
        
        # Создание директорий
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        
        # Файл реестра моделей
        self.registry_file = self.models_dir / "registry.json"
        self._load_registry()
    
    def _load_registry(self):
        """Загрузка реестра моделей"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    self.registry = json.load(f)
                self.logger.info(f"Реестр загружен. Моделей: {len(self.registry)}")
            except Exception as e:
                self.logger.error(f"Ошибка при загрузке реестра: {e}")
                self.registry = {}
        else:
            self.registry = {}
    
    def _save_registry(self):
        """Сохранение реестра моделей"""
        try:
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(self.registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении реестра: {e}")
    
    def save_model(self, model: SEGNeuralNetwork, metadata: ModelMetadata) -> bool:
        """
        Сохранение модели
        
        Args:
            model: Модель для сохранения
            metadata: Метаданные модели
            
        Returns:
            True если успешно, False если ошибка
        """
        try:
            # Создание пути для модели
            model_path = self.models_dir / f"{metadata.name}_v{metadata.version}.h5"
            
            # Сохранение модели
            model.save(str(model_path))
            
            # Сохранение метаданных
            metadata_path = self.models_dir / f"{metadata.name}_v{metadata.version}_metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Обновление реестра
            model_key = f"{metadata.name}_v{metadata.version}"
            self.registry[model_key] = {
                "name": metadata.name,
                "version": metadata.version,
                "difficulty": metadata.difficulty,
                "model_path": str(model_path),
                "metadata_path": str(metadata_path),
                "saved_at": datetime.now().isoformat()
            }
            self._save_registry()
            
            self.logger.info(f"Модель сохранена: {model_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении модели: {e}")
            return False
    
    def load_model(self, name: str, version: int) -> Optional[Tuple[SEGNeuralNetwork, ModelMetadata]]:
        """
        Загрузка модели
        
        Args:
            name: Название модели
            version: Версия модели
            
        Returns:
            Кортеж (модель, метаданные) или None если не найдена
        """
        try:
            model_key = f"{name}_v{version}"
            
            if model_key not in self.registry:
                self.logger.error(f"Модель не найдена: {model_key}")
                return None
            
            model_info = self.registry[model_key]
            model_path = Path(model_info["model_path"])
            metadata_path = Path(model_info["metadata_path"])
            
            # Загрузка модели
            if not model_path.exists():
                self.logger.error(f"Файл модели не найден: {model_path}")
                return None
            
            model = SEGNeuralNetwork()
            model.load(str(model_path))
            
            # Загрузка метаданных
            if metadata_path.exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata_dict = json.load(f)
                    metadata = ModelMetadata(**metadata_dict)
            else:
                metadata = ModelMetadata(
                    name=name,
                    version=version,
                    difficulty=model_info.get("difficulty", "unknown"),
                    created_at=model_info.get("saved_at", ""),
                    trained_episodes=0,
                    average_reward=0.0,
                    best_reward=0.0
                )
            
            self.logger.info(f"Модель загружена: {model_key}")
            return model, metadata
            
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке модели: {e}")
            return None
    
    def list_models(self, difficulty: Optional[str] = None) -> List[Dict]:
        """
        Получить список моделей
        
        Args:
            difficulty: Фильтр по сложности
            
        Returns:
            Список моделей
        """
        models_list = []
        
        for model_key, model_info in self.registry.items():
            if difficulty and model_info.get("difficulty") != difficulty:
                continue
            
            models_list.append({
                "key": model_key,
                "name": model_info.get("name"),
                "version": model_info.get("version"),
                "difficulty": model_info.get("difficulty"),
                "saved_at": model_info.get("saved_at")
            })
        
        return sorted(models_list, key=lambda x: (x["name"], -x["version"]))
    
    def get_latest_model(self, name: str) -> Optional[Tuple[SEGNeuralNetwork, ModelMetadata]]:
        """
        Получить последнюю версию модели
        
        Args:
            name: Название модели
            
        Returns:
            Кортеж (модель, метаданные) или None если не найдена
        """
        matching_models = [
            (k, v) for k, v in self.registry.items()
            if v.get("name") == name
        ]
        
        if not matching_models:
            return None
        
        # Найти модель с наибольшей версией
        latest = max(matching_models, key=lambda x: x[1].get("version", 0))
        model_key = latest[0]
        
        # Извлечь версию из ключа
        version = int(model_key.split("_v")[-1])
        
        return self.load_model(name, version)
    
    def save_checkpoint(self, model: SEGNeuralNetwork, name: str, episode: int) -> bool:
        """
        Сохранение checkpoint модели
        
        Args:
            model: Модель для сохранения
            name: Название модели
            episode: Номер эпизода
            
        Returns:
            True если успешно, False если ошибка
        """
        try:
            checkpoint_path = self.checkpoints_dir / f"{name}_episode_{episode}.h5"
            model.save(str(checkpoint_path))
            self.logger.info(f"Checkpoint сохранен: {checkpoint_path}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении checkpoint: {e}")
            return False
    
    def load_checkpoint(self, name: str, episode: int) -> Optional[SEGNeuralNetwork]:
        """
        Загрузка checkpoint модели
        
        Args:
            name: Название модели
            episode: Номер эпизода
            
        Returns:
            Модель или None если не найдена
        """
        try:
            checkpoint_path = self.checkpoints_dir / f"{name}_episode_{episode}.h5"
            
            if not checkpoint_path.exists():
                self.logger.error(f"Checkpoint не найден: {checkpoint_path}")
                return None
            
            model = SEGNeuralNetwork()
            model.load(str(checkpoint_path))
            self.logger.info(f"Checkpoint загружен: {checkpoint_path}")
            return model
            
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке checkpoint: {e}")
            return None
    
    def delete_model(self, name: str, version: int) -> bool:
        """
        Удаление модели
        
        Args:
            name: Название модели
            version: Версия модели
            
        Returns:
            True если успешно, False если ошибка
        """
        try:
            model_key = f"{name}_v{version}"
            
            if model_key not in self.registry:
                self.logger.error(f"Модель не найдена: {model_key}")
                return False
            
            model_info = self.registry[model_key]
            
            # Удаление файлов
            model_path = Path(model_info["model_path"])
            metadata_path = Path(model_info["metadata_path"])
            
            if model_path.exists():
                model_path.unlink()
            if metadata_path.exists():
                metadata_path.unlink()
            
            # Обновление реестра
            del self.registry[model_key]
            self._save_registry()
            
            self.logger.info(f"Модель удалена: {model_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при удалении модели: {e}")
            return False
    
    def create_model_version(self, name: str, difficulty: str, 
                           trained_episodes: int, avg_reward: float,
                           best_reward: float, description: str = "") -> ModelMetadata:
        """
        Создание метаданных для новой версии модели
        
        Args:
            name: Название модели
            difficulty: Сложность
            trained_episodes: Количество обученных эпизодов
            avg_reward: Средняя награда
            best_reward: Лучшая награда
            description: Описание
            
        Returns:
            Объект метаданных
        """
        # Найти последнюю версию
        max_version = 0
        for model_key in self.registry.keys():
            if model_key.startswith(f"{name}_v"):
                version = int(model_key.split("_v")[-1])
                max_version = max(max_version, version)
        
        new_version = max_version + 1
        
        metadata = ModelMetadata(
            name=name,
            difficulty=difficulty,
            version=new_version,
            created_at=datetime.now().isoformat(),
            trained_episodes=trained_episodes,
            average_reward=avg_reward,
            best_reward=best_reward,
            description=description
        )
        
        return metadata
    
    def get_model_info(self, name: str, version: int) -> Optional[Dict]:
        """
        Получить информацию о модели
        
        Args:
            name: Название модели
            version: Версия модели
            
        Returns:
            Информация о модели или None
        """
        model_key = f"{name}_v{version}"
        
        if model_key not in self.registry:
            return None
        
        model_info = self.registry[model_key]
        metadata_path = Path(model_info.get("metadata_path", ""))
        
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    return metadata
            except Exception as e:
                self.logger.error(f"Ошибка при чтении метаданных: {e}")
        
        return model_info
    
    def cleanup_old_checkpoints(self, name: str, keep_last: int = 5):
        """
        Удаление старых checkpoint'ов
        
        Args:
            name: Название модели
            keep_last: Количество последних checkpoint'ов для сохранения
        """
        try:
            checkpoints = sorted(
                self.checkpoints_dir.glob(f"{name}_episode_*.h5"),
                key=lambda x: int(x.stem.split("_")[-1]),
                reverse=True
            )
            
            for checkpoint in checkpoints[keep_last:]:
                checkpoint.unlink()
                self.logger.info(f"Checkpoint удален: {checkpoint}")
                
        except Exception as e:
            self.logger.error(f"Ошибка при очистке checkpoint'ов: {e}")


# Импорт для удаления циклической зависимости
from typing import Tuple
