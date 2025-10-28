"""
Многоагентный тренер для SEG
Управляет обучением нескольких AI ботов, играющих друг против друга
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

from neural_network import SEGNeuralNetwork, GameState, Action
from training_session import TrainingSession


@dataclass
class AgentConfig:
    """Конфигурация для AI агента"""
    agent_id: int
    name: str
    model: Optional[SEGNeuralNetwork] = None
    is_trainable: bool = True  # Если True, модель обучается
    epsilon: float = 0.1  # Коэффициент исследования (для epsilon-greedy)


class MultiAgentTrainer:
    """Тренер для обучения нескольких AI агентов"""
    
    def __init__(self, config: Dict[str, Any], num_agents: int = 2):
        """
        Инициализация многоагентного тренера
        
        Args:
            config: Конфигурация
            num_agents: Количество AI агентов в сессии (минимум 2)
        """
        self.config = config
        self.num_agents = max(2, num_agents)  # Минимум 2 агента
        self.logger = logging.getLogger("multi_agent_trainer")
        
        # Основной тренируемый агент
        self.main_agent = AgentConfig(
            agent_id=0,
            name="MainAgent",
            is_trainable=True
        )
        
        # Оппоненты (могут быть копиями модели или случайными)
        self.opponent_agents: List[AgentConfig] = []
        for i in range(1, num_agents):
            self.opponent_agents.append(
                AgentConfig(
                    agent_id=i,
                    name=f"Opponent_{i}",
                    is_trainable=False  # Оппоненты не обучаются во время игры
                )
            )
        
        self.logger.info(f"Инициализирован многоагентный тренер с {num_agents} агентами")
    
    def set_main_model(self, model: SEGNeuralNetwork):
        """Установка модели для основного агента"""
        self.main_agent.model = model
        self.logger.info("Модель установлена для основного агента")
    
    def set_opponent_models(self, models: Optional[List[SEGNeuralNetwork]] = None):
        """
        Установка моделей для оппонентов
        
        Args:
            models: Список моделей для оппонентов. 
                   Если None, используются копии основной модели.
        """
        if models is None:
            # Если моделей нет, создаем копии основной модели
            if self.main_agent.model is None:
                raise ValueError("Основная модель не установлена")
            
            for opponent in self.opponent_agents:
                # Копируем веса основной модели
                opponent.model = SEGNeuralNetwork(
                    state_size=self.main_agent.model.state_size,
                    learning_rate=self.main_agent.model.learning_rate
                )
                # Копируем веса
                opponent.model.model.set_weights(
                    self.main_agent.model.model.get_weights()
                )
                self.logger.info(f"Копия модели создана для {opponent.name}")
        else:
            # Используем переданные модели
            for i, opponent in enumerate(self.opponent_agents):
                if i < len(models):
                    opponent.model = models[i]
                    self.logger.info(f"Модель установлена для {opponent.name}")
    
    async def train_episode(self, session: TrainingSession, 
                          episode_num: int) -> Dict[str, Any]:
        """
        Обучение в течение одного эпизода (игры)
        
        Args:
            session: Тренировочная сессия
            episode_num: Номер эпизода
            
        Returns:
            Результаты эпизода
        """
        self.logger.info(f"Начало эпизода {episode_num} с {self.num_agents} агентами")
        
        # Инициализация сессии
        if not await session.initialize():
            raise RuntimeError("Не удалось инициализировать сессию")
        
        # Добавление всех агентов как игроков
        agent_configs = [self.main_agent] + self.opponent_agents
        for agent_config in agent_configs:
            result = await session.add_player(
                player_id=agent_config.agent_id,
                company_name=agent_config.name,
                initial_capital=self.config.get("training_session", {}).get("initial_capital", 10000)
            )
            
            if not result.get("success"):
                raise RuntimeError(f"Не удалось добавить агента {agent_config.name}")
        
        # Начало игры
        await session.start_game()
        
        # История действий и наград для обучения
        experience_buffer = {
            agent.agent_id: {
                "states": [],
                "actions": [],
                "rewards": [],
                "next_states": []
            }
            for agent in agent_configs
        }
        
        episode_rewards = {agent.agent_id: 0 for agent in agent_configs}
        
        # Основной игровой цикл
        try:
            while session.current_turn < session.max_turns:
                # Шаг для каждого агента
                for agent_config in agent_configs:
                    if agent_config.model is None:
                        continue
                    
                    try:
                        # Получение состояния игры
                        game_state = await session.get_game_state(agent_config.agent_id)
                        state_features = game_state.get_features()
                        
                        # Выбор действия
                        epsilon = agent_config.epsilon if agent_config.is_trainable else 0.05
                        action_id = agent_config.model.predict_action(
                            state_features, 
                            epsilon=epsilon
                        )
                        
                        # Выполнение действия
                        action_result = await session.execute_action(
                            player_id=agent_config.agent_id,
                            action_id=action_id,
                            action_params={}
                        )
                        
                        # Сохранение опыта для обучения
                        if agent_config.is_trainable:
                            experience_buffer[agent_config.agent_id]["states"].append(state_features)
                            experience_buffer[agent_config.agent_id]["actions"].append(action_id)
                    
                    except Exception as e:
                        self.logger.error(f"Ошибка при выполнении действия агента {agent_config.name}: {e}")
                
                # Переход к следующему ходу
                await session.next_turn()
                
                # Получение наград для каждого агента (упрощенная система)
                for agent_config in agent_configs:
                    try:
                        company_info = await session.game_client.get_company(
                            session.players[agent_config.agent_id].company_id
                        )
                        balance = company_info.get("company", {}).get("balance", 0)
                        initial_capital = self.config.get("training_session", {}).get("initial_capital", 10000)
                        reward = (balance - initial_capital) / initial_capital  # Нормализованная награда
                        episode_rewards[agent_config.agent_id] += reward
                    except Exception as e:
                        self.logger.warning(f"Не удалось получить награду для {agent_config.name}: {e}")
        
        except Exception as e:
            self.logger.error(f"Ошибка во время игры: {e}")
        
        # Завершение игры
        final_result = await session.finish_game()
        
        # Обучение основного агента на собранном опыте
        main_experience = experience_buffer[self.main_agent.agent_id]
        if len(main_experience["states"]) > 0 and self.main_agent.model:
            self.logger.info(f"Обучение основного агента на {len(main_experience['states'])} шагах")
            # Здесь можно добавить реальное обучение модели
            # self.main_agent.model.train_on_experience(main_experience)
        
        # Очистка сессии
        await session.cleanup()
        
        return {
            "episode": episode_num,
            "total_turns": session.current_turn,
            "agent_rewards": episode_rewards,
            "final_rankings": final_result.get("rankings", []),
            "main_agent_reward": episode_rewards[self.main_agent.agent_id],
            "experience_size": len(main_experience["states"])
        }
    
    async def train(self, num_episodes: int, difficulty: str = "easy") -> Dict[str, Any]:
        """
        Обучение на нескольких эпизодах
        
        Args:
            num_episodes: Количество эпизодов
            difficulty: Уровень сложности
            
        Returns:
            Статистика обучения
        """
        self.logger.info(f"Начало обучения: {num_episodes} эпизодов, сложность {difficulty}")
        
        training_stats = {
            "episodes": [],
            "main_rewards": [],
            "average_main_reward": 0,
            "total_episodes": num_episodes,
            "difficulty": difficulty
        }
        
        session_counter = 0
        
        for episode_num in range(num_episodes):
            try:
                session_id = f"episode_{difficulty}_{episode_num}_{int(datetime.now().timestamp())}"
                session = TrainingSession(session_id, self.config)
                
                episode_result = await self.train_episode(session, episode_num)
                
                training_stats["episodes"].append(episode_result)
                training_stats["main_rewards"].append(episode_result["main_agent_reward"])
                
                # Логирование прогресса
                avg_reward = sum(training_stats["main_rewards"]) / len(training_stats["main_rewards"])
                self.logger.info(
                    f"Эпизод {episode_num + 1}/{num_episodes} завершен. "
                    f"Награда: {episode_result['main_agent_reward']:.2f}, "
                    f"Средняя: {avg_reward:.2f}"
                )
                
                session_counter += 1
                
            except Exception as e:
                self.logger.error(f"Ошибка при обучении эпизода {episode_num}: {e}")
                continue
        
        training_stats["average_main_reward"] = (
            sum(training_stats["main_rewards"]) / len(training_stats["main_rewards"])
            if training_stats["main_rewards"] else 0
        )
        
        training_stats["episodes_completed"] = session_counter
        
        self.logger.info(
            f"Обучение завершено. "
            f"Средняя награда: {training_stats['average_main_reward']:.2f}"
        )
        
        return training_stats
