"""
Главное приложение для обучения нейросети на игре SEG
Управляет процессом обучения, сохранением и тестированием моделей
"""
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import asyncio
import json
import logging
import argparse
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from neural_network import SEGNeuralNetwork
from trainer import Trainer
from multi_agent_trainer import MultiAgentTrainer
from model_storage import ModelStorage, ModelMetadata
from training_session import TrainingSession


# Настройка логирования
def setup_logging(log_dir: str = "/logs"):
    """Настройка логирования"""
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    log_file = log_path / f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("seg_trainer")


class AITrainerApp:
    """Главное приложение тренера"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Инициализация приложения
        
        Args:
            config_path: Путь к файлу конфигурации
        """
        self.logger = setup_logging()
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.storage = ModelStorage(
            models_dir=self.config.get("model_storage", {}).get("models_dir", "/models"),
            checkpoints_dir=self.config.get("model_storage", {}).get("checkpoints_dir", "/checkpoints")
        )
        self.logger.info("Приложение инициализировано")
    
    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке конфига: {e}")
            raise
    
    async def train_model(self, name: str, difficulty: str = "easy", 
                         episodes: Optional[int] = None, 
                         description: str = "", num_agents: int = 2) -> Dict[str, Any]:
        """
        Обучение новой модели
        
        Args:
            name: Название модели
            difficulty: Уровень сложности (easy, medium, hard, expert)
            episodes: Количество эпизодов (если None, берется из config)
            description: Описание модели
            num_agents: Количество AI ботов в сессии (минимум 2)
            
        Returns:
            Результаты обучения
        """
        self.logger.info(f"Начало обучения модели: {name} ({difficulty}) с {num_agents} агентами")
        
        # Создание новой модели
        model = SEGNeuralNetwork(
            state_size=16,
            learning_rate=self.config.get("training_difficulty_levels", {})
                .get(difficulty, {}).get("learning_rate", 0.001)
        )
        
        # Создание многоагентного тренера
        multi_agent_trainer = MultiAgentTrainer(self.config, num_agents=num_agents)
        multi_agent_trainer.set_main_model(model)
        multi_agent_trainer.set_opponent_models()  # Создаст копии основной модели для оппонентов
        
        # Определение количества эпизодов
        if episodes is None:
            episodes = self.config.get("training_difficulty_levels", {}).get(difficulty, {}).get("episodes", 100)
        
        # Обучение
        try:
            training_result = await multi_agent_trainer.train(
                num_episodes=episodes,
                difficulty=difficulty
            )
            
            # Сохранение модели
            main_rewards = training_result.get("main_rewards", [0])
            avg_reward = sum(main_rewards) / len(main_rewards) if main_rewards else 0
            best_reward = max(main_rewards) if main_rewards else 0
            
            metadata = self.storage.create_model_version(
                name=name,
                difficulty=difficulty,
                trained_episodes=training_result.get("episodes_completed", 0),
                avg_reward=avg_reward,
                best_reward=best_reward,
                description=description
            )
            
            self.storage.save_model(model, metadata)
            
            # Сохранение результатов
            results_file = Path(self.config.get("model_storage", {}).get("models_dir", "/models")) / f"{name}_training_results.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(training_result, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Модель обучена и сохранена: {name} v{metadata.version}")
            
            return {
                "success": True,
                "model_name": name,
                "model_version": metadata.version,
                "difficulty": difficulty,
                "episodes_trained": training_result.get("episodes_completed", 0),
                "average_reward": avg_reward,
                "best_reward": best_reward,
                "training_result": training_result
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка при обучении модели: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e)
            }
    
    async def train_multiple_versions(self, base_name: str, 
                                     versions: Dict[str, Optional[int]]) -> Dict[str, Any]:
        """
        Обучение нескольких версий моделей с разной сложностью
        
        Args:
            base_name: Базовое название модели
            versions: Словарь {сложность: количество_эпизодов}
                     Например: {"easy": 100, "hard": 1000}
            
        Returns:
            Результаты обучения всех версий
        """
        self.logger.info(f"Начало обучения множественных версий: {base_name}")
        
        results = {
            "base_name": base_name,
            "versions": {},
            "start_time": datetime.now().isoformat()
        }
        
        for difficulty, episodes in versions.items():
            model_name = f"{base_name}_{difficulty}"
            
            result = await self.train_model(
                name=model_name,
                difficulty=difficulty,
                episodes=episodes,
                description=f"Версия {difficulty} для {base_name}"
            )
            
            results["versions"][difficulty] = result
            
            self.logger.info(f"Версия {difficulty} завершена")
        
        results["end_time"] = datetime.now().isoformat()
        return results
    
    async def test_model(self, name: str, version: int, num_test_games: int = 5) -> Dict[str, Any]:
        """
        Тестирование модели
        
        Args:
            name: Название модели
            version: Версия модели
            num_test_games: Количество тестовых игр
            
        Returns:
            Результаты тестирования
        """
        self.logger.info(f"Начало тестирования: {name} v{version}")
        
        # Загрузка модели
        loaded = self.storage.load_model(name, version)
        if not loaded:
            return {
                "success": False,
                "error": f"Модель не найдена: {name} v{version}"
            }
        
        model, metadata = loaded
        
        test_results = {
            "model_name": name,
            "model_version": version,
            "num_games": num_test_games,
            "games": []
        }
        
        try:
            for game_num in range(num_test_games):
                session_id = f"test_{name}_v{version}_game{game_num}"
                session = TrainingSession(session_id, self.config)
                
                # Инициализация и добавление игроков
                await session.initialize()
                await session.add_player(0, f"{name}_AI", 10000)
                await session.add_player(1, "Random_AI", 10000)
                
                # Запуск игры
                await session.start_game()
                
                while session.current_turn < session.max_turns:
                    # Действия первого игрока (AI)
                    game_state = await session.get_game_state(0)
                    state_features = game_state.get_features()
                    action_id = model.predict_action(state_features, epsilon=0.05)
                    # ... выполнение действия
                    
                    await session.next_turn()
                
                # Завершение игры
                result = await session.finish_game()
                test_results["games"].append(result)
                
                await session.cleanup()
            
            # Статистика
            avg_rank = sum(g.get("rankings", [{}])[0].get("rank", 0) 
                          for g in test_results["games"]) / num_test_games
            test_results["average_rank"] = avg_rank
            test_results["success"] = True
            
            self.logger.info(f"Тестирование завершено. Средний рейтинг: {avg_rank:.2f}")
            return test_results
            
        except Exception as e:
            self.logger.error(f"Ошибка при тестировании: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_models(self, difficulty: Optional[str] = None) -> Dict[str, Any]:
        """Получить список моделей"""
        models = self.storage.list_models(difficulty)
        
        return {
            "total_models": len(models),
            "models": models
        }
    
    def get_model_info(self, name: str, version: int) -> Dict[str, Any]:
        """Получить информацию о модели"""
        info = self.storage.get_model_info(name, version)
        
        if info:
            return {
                "success": True,
                "info": info
            }
        else:
            return {
                "success": False,
                "error": "Модель не найдена"
            }
    
    def delete_model(self, name: str, version: int) -> Dict[str, Any]:
        """Удалить модель"""
        success = self.storage.delete_model(name, version)
        
        return {
            "success": success,
            "message": f"Модель удалена" if success else "Ошибка при удалении модели"
        }


async def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description="Тренер нейросети для SEG")
    parser.add_argument("--command", choices=["train", "train-multi", "test", "list", "info", "delete"],
                       default="train", help="Команда для выполнения")
    parser.add_argument("--name", type=str, help="Название модели")
    parser.add_argument("--difficulty", choices=["easy", "medium", "hard", "expert"],
                       default="easy", help="Уровень сложности")
    parser.add_argument("--episodes", type=int, help="Количество эпизодов")
    parser.add_argument("--version", type=int, help="Версия модели")
    parser.add_argument("--description", type=str, default="", help="Описание модели")
    parser.add_argument("--config", type=str, default="config.json", help="Путь к конфигурации")
    
    args = parser.parse_args()
    
    # Инициализация приложения
    app = AITrainerApp(args.config)
    
    if args.command == "train":
        if not args.name:
            print("Ошибка: требуется параметр --name")
            return
        
        result = await app.train_model(
            name=args.name,
            difficulty=args.difficulty,
            episodes=args.episodes,
            description=args.description
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.command == "train-multi":
        if not args.name:
            print("Ошибка: требуется параметр --name")
            return
        
        # Обучение всех версий
        versions = {
            "easy": 100,
            "medium": 500,
            "hard": 1000
        }
        
        result = await app.train_multiple_versions(args.name, versions)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.command == "test":
        if not args.name or args.version is None:
            print("Ошибка: требуются параметры --name и --version")
            return
        
        result = await app.test_model(args.name, args.version)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.command == "list":
        result = app.list_models(args.difficulty)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.command == "info":
        if not args.name or args.version is None:
            print("Ошибка: требуются параметры --name и --version")
            return
        
        result = app.get_model_info(args.name, args.version)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.command == "delete":
        if not args.name or args.version is None:
            print("Ошибка: требуются параметры --name и --version")
            return
        
        result = app.delete_model(args.name, args.version)
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
