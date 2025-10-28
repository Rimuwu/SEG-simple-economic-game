"""
Модуль обучения и оценки нейросети
Управляет процессом обучения модели на основе игровых сессий
"""
import asyncio
import numpy as np
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

from neural_network import SEGNeuralNetwork, ReplayBuffer, GameState, Action
from training_session import TrainingSession


@dataclass
class RewardMetrics:
    """Метрики награждения"""
    capital_score: float
    reputation_score: float
    economic_level_score: float
    total_reward: float
    rank: int


class RewardCalculator:
    """Расчет наград для обучения"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Инициализация калькулятора наград
        
        Args:
            config: Конфигурация
        """
        self.config = config
        self.reward_config = config.get("reward_system", {})
        self.logger = logging.getLogger("reward_calculator")
    
    def calculate_reward(self, player_rank: int, total_players: int,
                        capital_delta: int, reputation: int, 
                        economic_level: int) -> RewardMetrics:
        """
        Расчет награды для игрока
        
        Args:
            player_rank: Место игрока в рейтинге (1 - лучше)
            total_players: Общее количество игроков
            capital_delta: Изменение капитала
            reputation: Репутация
            economic_level: Экономический уровень
            
        Returns:
            Объект с метриками наград
        """
        # Нормализация коэффициентов
        capital_weight = self.reward_config.get("capital_weight", 0.4)
        reputation_weight = self.reward_config.get("reputation_weight", 0.3)
        economic_level_weight = self.reward_config.get("economic_level_weight", 0.3)
        
        # Расчет индивидуальных оценок
        capital_score = max(0, capital_delta / 10000)  # нормализация
        capital_score = min(capital_score, 100)  # cap
        
        reputation_score = reputation / 1000
        reputation_score = min(reputation_score, 100)
        
        economic_level_score = economic_level / 100
        economic_level_score = min(economic_level_score, 100)
        
        # Базовая награда за место
        rank_bonus = (total_players - player_rank + 1) / total_players * 100
        if player_rank == 1:
            rank_bonus += self.reward_config.get("win_bonus", 1000)
        elif player_rank == total_players:
            rank_bonus += self.reward_config.get("loss_penalty", -100)
        
        # Общая награда
        total_reward = (
            capital_score * capital_weight +
            reputation_score * reputation_weight +
            economic_level_score * economic_level_weight +
            rank_bonus
        )
        
        return RewardMetrics(
            capital_score=capital_score,
            reputation_score=reputation_score,
            economic_level_score=economic_level_score,
            total_reward=total_reward,
            rank=player_rank
        )


class Trainer:
    """Тренер для обучения нейросети"""
    
    def __init__(self, config: Dict[str, Any], model: Optional[SEGNeuralNetwork] = None):
        """
        Инициализация тренера
        
        Args:
            config: Конфигурация
            model: Модель нейросети (если None, создается новая)
        """
        self.config = config
        self.logger = logging.getLogger("trainer")
        self.reward_calc = RewardCalculator(config)
        
        # Инициализация модели
        if model is None:
            self.model = SEGNeuralNetwork(
                state_size=16,  # должно соответствовать GameState
                action_size=Action.ACTION_COUNT,
                learning_rate=config.get("training_difficulty_levels", {})
                    .get("easy", {}).get("learning_rate", 0.001)
            )
        else:
            self.model = model
        
        # Буфер опыта
        self.replay_buffer = ReplayBuffer(max_size=10000)
        
        # Статистика обучения
        self.training_stats = {
            "episodes_trained": 0,
            "total_rewards": [],
            "average_rewards": [],
            "model_losses": []
        }
    
    async def train_episode(self, session: TrainingSession, num_players: int = 2,
                           difficulty: str = "easy") -> Dict[str, Any]:
        """
        Обучение на одном эпизоде (сессии игры)
        
        Args:
            session: Тренировочная сессия
            num_players: Количество игроков (в т.ч. AI)
            difficulty: Уровень сложности
            
        Returns:
            Статистика эпизода
        """
        difficulty_config = self.config.get("training_difficulty_levels", {}).get(difficulty, {})
        epsilon = 1.0 / (difficulty_config.get("iterations", 100) + 1)  # epsilon decay
        
        episode_rewards = []
        episode_states = []
        episode_actions = []
        
        try:
            # Инициализация сессии
            await session.initialize()
            
            # Добавление игроков
            for i in range(num_players):
                await session.add_player(
                    player_id=i,
                    company_name=f"AI_Player_{i}_{self.training_stats['episodes_trained']}",
                    initial_capital=10000
                )
            
            # Начало игры
            await session.start_game()
            
            # Игровой цикл
            while session.current_turn < session.max_turns:
                # Каждый игрок выполняет действие
                for player_id in range(num_players):
                    try:
                        # Получение состояния
                        game_state = await session.get_game_state(player_id)
                        state_features = game_state.get_features()
                        
                        # Выбор действия
                        action_id = self.model.predict_action(state_features, epsilon)
                        
                        # Выполнение действия
                        action_params = self._get_action_params(game_state, action_id)
                        result = await session.execute_action(player_id, action_id, action_params)
                        
                        # Сохранение в буфер
                        episode_states.append(state_features)
                        episode_actions.append(action_id)
                        
                    except Exception as e:
                        self.logger.error(f"Ошибка в ходе игрока {player_id}: {e}")
                
                # Переход на следующий ход
                turn_data = await session.next_turn()
            
            # Завершение игры и получение наград
            result = await session.finish_game()
            rankings = result.get("rankings", [])
            
            # Расчет наград для каждого игрока
            for player_ranking in rankings:
                player_id = player_ranking.get("player_id", 0)
                rank = player_ranking.get("rank", 1)
                
                reward_metrics = self.reward_calc.calculate_reward(
                    player_rank=rank,
                    total_players=num_players,
                    capital_delta=player_ranking.get("profit", 0),
                    reputation=player_ranking.get("reputation", 0),
                    economic_level=player_ranking.get("economic_level", 0)
                )
                
                episode_rewards.append(reward_metrics.total_reward)
            
            # Обучение модели на буфере опыта
            if len(self.replay_buffer) > 32:
                loss = self._train_on_batch()
                self.training_stats["model_losses"].append(loss)
            
            # Статистика эпизода
            avg_reward = np.mean(episode_rewards) if episode_rewards else 0
            self.training_stats["episodes_trained"] += 1
            self.training_stats["total_rewards"].append(sum(episode_rewards))
            self.training_stats["average_rewards"].append(avg_reward)
            
            episode_result = {
                "episode": self.training_stats["episodes_trained"],
                "total_reward": sum(episode_rewards),
                "average_reward": avg_reward,
                "rankings": rankings,
                "epsilon": epsilon
            }
            
            self.logger.info(f"Эпизод {self.training_stats['episodes_trained']} завершен. "
                           f"Ср. награда: {avg_reward:.2f}")
            
            return episode_result
            
        except Exception as e:
            self.logger.error(f"Ошибка при обучении на эпизоде: {e}")
            raise
        finally:
            await session.cleanup()
    
    async def train(self, difficulty: str = "easy", num_episodes: Optional[int] = None) -> Dict:
        """
        Обучение модели
        
        Args:
            difficulty: Уровень сложности (easy, medium, hard, expert)
            num_episodes: Количество эпизодов (если None, используется из config)
            
        Returns:
            Результаты обучения
        """
        difficulty_config = self.config.get("training_difficulty_levels", {}).get(difficulty, {})
        iterations = num_episodes or difficulty_config.get("iterations", 100)
        
        self.logger.info(f"Начало обучения ({difficulty}, {iterations} эпизодов)")
        
        training_results = {
            "difficulty": difficulty,
            "total_episodes": iterations,
            "episodes_completed": 0,
            "episodes_data": [],
            "start_time": datetime.now().isoformat()
        }
        
        for episode in range(iterations):
            try:
                # Создание новой сессии для каждого эпизода
                session_id = f"{difficulty}_{episode}_{int(datetime.now().timestamp())}"
                session = TrainingSession(session_id, self.config)
                
                # Обучение на эпизоде
                result = await self.train_episode(session, num_players=2, difficulty=difficulty)
                training_results["episodes_data"].append(result)
                training_results["episodes_completed"] += 1
                
                # Периодическое сохранение модели
                if (episode + 1) % self.config.get("model_storage", {}).get("save_interval", 10) == 0:
                    self._save_checkpoint(difficulty, episode + 1)
                
                self.logger.info(f"Прогресс: {episode + 1}/{iterations}")
                
            except Exception as e:
                self.logger.error(f"Ошибка в эпизоде {episode}: {e}")
                continue
        
        training_results["end_time"] = datetime.now().isoformat()
        training_results["training_stats"] = self.training_stats
        
        self.logger.info(f"Обучение завершено ({difficulty})")
        return training_results
    
    def _get_action_params(self, game_state: GameState, action_id: int) -> Dict:
        """Получение параметров для действия"""
        action_name = Action.get_action_name(action_id)
        
        if action_id == Action.MOVE_CELL:
            return {"x": np.random.randint(0, 10), "y": np.random.randint(0, 10)}
        elif action_id == Action.BUY_ITEM:
            return {"market_item_id": 0, "quantity": 1}
        elif action_id == Action.SELL_ITEM:
            return {"item_id": 0, "price": 100, "quantity": 1}
        elif action_id == Action.IMPROVE:
            return {"improvement_type": "workshop"}
        elif action_id == Action.TAKE_CREDIT:
            return {"amount": 1000, "period": 10}
        elif action_id == Action.PAY_CREDIT:
            return {"credit_index": 0, "amount": 500}
        elif action_id == Action.PAY_TAXES:
            return {"amount": 100}
        elif action_id == Action.INTERACT:
            return {"x": np.random.randint(0, 10), "y": np.random.randint(0, 10)}
        else:
            return {}
    
    def _train_on_batch(self) -> float:
        """Обучение на батче из буфера опыта"""
        if len(self.replay_buffer) < 32:
            return 0.0
        
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(32)
        history = self.model.train(states, actions, rewards, next_states, dones)
        
        return history.get("loss", [0])[-1] if "loss" in history else 0.0
    
    def _save_checkpoint(self, difficulty: str, episode: int):
        """Сохранение checkpoint модели"""
        try:
            models_dir = Path(self.config.get("model_storage", {}).get("models_dir", "/models"))
            models_dir.mkdir(parents=True, exist_ok=True)
            
            checkpoint_path = models_dir / f"{difficulty}_episode_{episode}.h5"
            self.model.save(str(checkpoint_path))
            
            self.logger.info(f"Checkpoint сохранен: {checkpoint_path}")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении checkpoint: {e}")
    
    def save_model(self, name: str):
        """Сохранение модели"""
        models_dir = Path(self.config.get("model_storage", {}).get("models_dir", "/models"))
        models_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = models_dir / f"{name}.h5"
        self.model.save(str(filepath))
        self.logger.info(f"Модель сохранена: {filepath}")
    
    def load_model(self, name: str):
        """Загрузка модели"""
        models_dir = Path(self.config.get("model_storage", {}).get("models_dir", "/models"))
        filepath = models_dir / f"{name}.h5"
        
        if filepath.exists():
            self.model.load(str(filepath))
            self.logger.info(f"Модель загружена: {filepath}")
        else:
            self.logger.error(f"Файл модели не найден: {filepath}")
    
    def get_training_stats(self) -> Dict:
        """Получение статистики обучения"""
        return {
            "episodes_trained": self.training_stats["episodes_trained"],
            "avg_reward_history": self.training_stats["average_rewards"],
            "total_rewards": self.training_stats["total_rewards"],
            "model_losses": self.training_stats["model_losses"]
        }
