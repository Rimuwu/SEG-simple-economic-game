"""
Нейронная сеть для обучения игре в SEG
Использует TensorFlow/Keras для создания модели
"""
import numpy as np
import json
from typing import Tuple, List, Dict, Optional, Any
from pathlib import Path
import logging

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    logging.warning("TensorFlow не установлен. Установите: pip install tensorflow")


class GameState:
    """Представление состояния игры для нейросети"""
    
    def __init__(self, state_dict: Dict[str, Any]):
        """
        Инициализация состояния игры
        
        Args:
            state_dict: Словарь с информацией о состоянии игры
        """
        self.state_dict = state_dict
        self.features = self._extract_features()
    
    def _extract_features(self) -> np.ndarray:
        """Извлечение признаков из состояния игры"""
        features = []
        
        # Финансовая информация
        company = self.state_dict.get("company", {})
        features.extend([
            company.get("balance", 0) / 100000,  # нормализация
            company.get("reputation", 0) / 1000,
            company.get("economic_level", 0) / 100,
        ])
        
        # Информация об инвентаре
        inventory = self.state_dict.get("inventory", [])
        features.append(len(inventory) / 50)  # максимум предметов
        inventory_value = sum(item.get("value", 0) for item in inventory)
        features.append(inventory_value / 50000)
        
        # Информация о ячейке
        cell_info = self.state_dict.get("current_cell", {})
        features.extend([
            cell_info.get("x", 0) / 10,
            cell_info.get("y", 0) / 10,
            cell_info.get("resource_type", 0) / 10,
            cell_info.get("resource_amount", 0) / 1000,
        ])
        
        # Информация о кредитах
        credits = self.state_dict.get("credits", [])
        features.append(len(credits))  # количество кредитов
        total_debt = sum(c.get("remaining", 0) for c in credits)
        features.append(total_debt / 100000)
        
        # Информация о налогах
        taxes = self.state_dict.get("taxes", {})
        features.append(taxes.get("amount", 0) / 50000)
        
        # Рыночная информация
        market_items = self.state_dict.get("market_items", [])
        features.append(len(market_items) / 100)
        
        return np.array(features, dtype=np.float32)
    
    def get_features(self) -> np.ndarray:
        """Получить вектор признаков"""
        return self.features.reshape(1, -1)


class Action:
    """Представление действия в игре"""
    
    # Типы действий
    NOOP = 0  # Ничего не делать
    MOVE_CELL = 1  # Переместиться на другую ячейку
    BUY_ITEM = 2  # Купить товар
    SELL_ITEM = 3  # Продать товар
    IMPROVE = 4  # Улучшить компанию
    TAKE_CREDIT = 5  # Получить кредит
    PAY_CREDIT = 6  # Погасить кредит
    PAY_TAXES = 7  # Оплатить налоги
    INTERACT = 8  # Взаимодействие с NPC
    
    ACTION_COUNT = 9
    
    @staticmethod
    def get_action_name(action_id: int) -> str:
        """Получить название действия"""
        names = {
            0: "NOOP",
            1: "MOVE_CELL",
            2: "BUY_ITEM",
            3: "SELL_ITEM",
            4: "IMPROVE",
            5: "TAKE_CREDIT",
            6: "PAY_CREDIT",
            7: "PAY_TAXES",
            8: "INTERACT"
        }
        return names.get(action_id, "UNKNOWN")


class SEGNeuralNetwork:
    """Нейронная сеть для игры SEG"""
    
    def __init__(self, state_size: int = 16, action_size: int = Action.ACTION_COUNT,
                 learning_rate: float = 0.001):
        """
        Инициализация нейронной сети
        
        Args:
            state_size: Размер вектора состояния
            action_size: Количество возможных действий
            learning_rate: Скорость обучения
        """
        if not TF_AVAILABLE:
            raise RuntimeError("TensorFlow не установлен")
        
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.model = self._build_model()
        self.target_model = self._build_model()
        self._update_target_model()
    
    def _build_model(self) -> keras.Model:
        """Построение архитектуры нейронной сети"""
        model = models.Sequential([
            layers.Input(shape=(self.state_size,)),
            layers.Dense(256, activation='relu', name='dense_1'),
            layers.Dropout(0.2),
            layers.Dense(128, activation='relu', name='dense_2'),
            layers.Dropout(0.2),
            layers.Dense(64, activation='relu', name='dense_3'),
            layers.Dropout(0.1),
            layers.Dense(self.action_size, activation='linear', name='output')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def _update_target_model(self):
        """Обновление целевой модели"""
        self.target_model.set_weights(self.model.get_weights())
    
    def predict(self, state: np.ndarray) -> np.ndarray:
        """Предсказание Q-значений для состояния"""
        return self.model.predict(state, verbose=0)
    
    def predict_action(self, state: np.ndarray, epsilon: float = 0.0) -> int:
        """
        Предсказание действия (с epsilon-greedy стратегией)
        
        Args:
            state: Вектор состояния
            epsilon: Вероятность случайного выбора
            
        Returns:
            ID действия
        """
        if np.random.random() < epsilon:
            return np.random.randint(0, self.action_size)
        
        q_values = self.predict(state)
        return np.argmax(q_values[0])
    
    def train(self, states: np.ndarray, actions: np.ndarray, rewards: np.ndarray,
              next_states: np.ndarray, dones: np.ndarray, batch_size: int = 32) -> Dict:
        """
        Обучение модели на батче данных
        
        Args:
            states: Вектор состояний [batch_size, state_size]
            actions: Вектор действий [batch_size]
            rewards: Вектор вознаграждений [batch_size]
            next_states: Вектор следующих состояний [batch_size, state_size]
            dones: Вектор флагов окончания [batch_size]
            batch_size: Размер батча
            
        Returns:
            Метрики обучения
        """
        # Вычисление целевых Q-значений
        target_q_values = self.model.predict(states, verbose=0)
        next_q_values = self.target_model.predict(next_states, verbose=0)
        
        for i in range(len(states)):
            if dones[i]:
                target_q_values[i, actions[i]] = rewards[i]
            else:
                target_q_values[i, actions[i]] = rewards[i] + 0.99 * np.max(next_q_values[i])
        
        # Обучение модели
        history = self.model.fit(
            states, target_q_values,
            batch_size=batch_size,
            epochs=1,
            verbose=0
        )
        
        return history.history
    
    def save(self, filepath: str):
        """Сохранение модели"""
        self.model.save(filepath)
        logging.info(f"Модель сохранена: {filepath}")
    
    def load(self, filepath: str):
        """Загрузка модели"""
        self.model = keras.models.load_model(filepath)
        self._update_target_model()
        logging.info(f"Модель загружена: {filepath}")
    
    def get_summary(self) -> str:
        """Получить описание модели"""
        summary = []
        self.model.summary(print_fn=lambda x: summary.append(x))
        return "\n".join(summary)


class ReplayBuffer:
    """Буфер опыта для обучения"""
    
    def __init__(self, max_size: int = 10000):
        """
        Инициализация буфера
        
        Args:
            max_size: Максимальный размер буфера
        """
        self.max_size = max_size
        self.buffer = []
        self.idx = 0
    
    def add(self, state: np.ndarray, action: int, reward: float,
            next_state: np.ndarray, done: bool):
        """Добавление опыта в буфер"""
        experience = (state, action, reward, next_state, done)
        
        if len(self.buffer) < self.max_size:
            self.buffer.append(experience)
        else:
            self.buffer[self.idx] = experience
            self.idx = (self.idx + 1) % self.max_size
    
    def sample(self, batch_size: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray, 
                                                np.ndarray, np.ndarray]:
        """Случайная выборка батча из буфера"""
        indices = np.random.choice(len(self.buffer), batch_size, replace=False)
        
        states = np.array([self.buffer[i][0] for i in indices])
        actions = np.array([self.buffer[i][1] for i in indices])
        rewards = np.array([self.buffer[i][2] for i in indices])
        next_states = np.array([self.buffer[i][3] for i in indices])
        dones = np.array([self.buffer[i][4] for i in indices])
        
        return states, actions, rewards, next_states, dones
    
    def __len__(self) -> int:
        return len(self.buffer)
    
    def clear(self):
        """Очистка буфера"""
        self.buffer.clear()
        self.idx = 0
