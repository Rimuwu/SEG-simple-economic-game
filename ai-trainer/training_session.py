"""
Управление тренировочной сессией без таймеров и таймаутов
Позволяет пошагово управлять игровой сессией для обучения нейросети
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from ai_ws_client import AIGameClient, AIGameClient
from neural_network import GameState, Action


class GamePhase(Enum):
    """Фазы игровой сессии"""
    SETUP = "setup"  # Подготовка
    RUNNING = "running"  # Игра идет
    EVALUATION = "evaluation"  # Оценка результатов
    FINISHED = "finished"  # Завершена


@dataclass
class PlayerStats:
    """Статистика игрока"""
    player_id: int
    company_id: int
    name: str
    initial_capital: int
    final_capital: int = 0
    reputation: int = 0
    economic_level: int = 0
    rank: int = 0


class TrainingSession:
    """Управление тренировочной сессией"""
    
    def __init__(self, session_id: str, config: Dict[str, Any]):
        """
        Инициализация сессии
        
        Args:
            session_id: Уникальный идентификатор сессии
            config: Конфигурация из config.json
        """
        self.session_id = session_id
        self.config = config
        self.logger = logging.getLogger("training_session")
        
        self.game_client = AIGameClient(
            training_mode=True,
            skip_timers=config.get("training_session", {}).get("skip_timers", True)
        )
        
        self.current_phase = GamePhase.SETUP
        self.players: Dict[int, PlayerStats] = {}
        self.game_history: List[Dict] = []
        self.current_turn = 0
        self.max_turns = config.get("training_session", {}).get("max_game_turns", 100)
    
    async def initialize(self):
        """Инициализация сессии"""
        try:
            await self.game_client.connect()
            
            # Создание новой игровой сессии
            result = await self.game_client.create_session()
            
            # Проверяем наличие session_id в результате (сервер может вернуть просто id вместо session_id)
            session_id = result.get("session_id") or result.get("id")
            if session_id:
                # Сохраняем полученный session_id
                self.session_id = session_id
                # Сохраняем session_id в game_client для последующих операций
                self.game_client.current_session = self.session_id
                self.logger.info(f"Сессия инициализирована: {self.session_id}")
                self.current_phase = GamePhase.SETUP
                return True
            else:
                self.logger.error(f"Ошибка инициализации сессии: {result}")
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка при инициализации: {e}")
            raise
    
    async def add_player(self, player_id: int, company_name: str, 
                        initial_capital: int = 10000) -> Dict[str, Any]:
        """
        Добавление игрока в сессию
        
        Args:
            player_id: ID игрока
            company_name: Название компании
            initial_capital: Начальный капитал
            
        Returns:
            Информация о созданной компании
        """
        try:
            # Создание компании для игрока
            # Передаем session_id явно чтобы избежать ошибки "Сессия не найдена"
            result = await self.game_client.create_company(
                company_name,
                who_create=player_id,
                session_id=self.session_id
            )
            
            # Проверяем наличие company_id в результате
            company_id = result.get("company_id") or result.get("id")
            if company_id:
                
                # Регистрация игрока в сессии
                player_stats = PlayerStats(
                    player_id=player_id,
                    company_id=company_id,
                    name=company_name,
                    initial_capital=initial_capital
                )
                self.players[player_id] = player_stats
                
                self.logger.info(f"Игрок добавлен: {company_name} (ID: {player_id})")
                return {
                    "success": True,
                    "player_id": player_id,
                    "company_id": company_id,
                    "company_name": company_name
                }
            else:
                self.logger.error(f"Ошибка при создании компании: {result}")
                return {"success": False, "error": result.get("error")}
                
        except Exception as e:
            self.logger.error(f"Ошибка при добавлении игрока: {e}")
            raise
    
    async def start_game(self):
        """Начало игры"""
        if len(self.players) < 2:
            raise ValueError("Минимум 2 игрока для начала игры")
        
        self.current_phase = GamePhase.RUNNING
        self.current_turn = 0
        self.logger.info(f"Игра начата с {len(self.players)} игроками")
    
    async def execute_action(self, player_id: int, action_id: int, 
                            action_params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Выполнение действия игроком
        
        Args:
            player_id: ID игрока
            action_id: ID действия
            action_params: Параметры действия
            
        Returns:
            Результат действия
        """
        if player_id not in self.players:
            raise ValueError(f"Игрок {player_id} не найден")
        
        if self.current_phase != GamePhase.RUNNING:
            raise ValueError(f"Игра не в режиме выполнения (фаза: {self.current_phase.value})")
        
        player = self.players[player_id]
        action_name = Action.get_action_name(action_id)
        
        # Инициализируем params если None
        params = action_params or {}
        
        try:
            result = None
            
            if action_id == Action.NOOP:
                result = {"success": True, "action": "NOOP"}
            
            elif action_id == Action.MOVE_CELL:
                x = params.get("x", 0)
                y = params.get("y", 0)
                result = await self.game_client.set_company_position(
                    x, y, player.company_id
                )
            
            elif action_id == Action.BUY_ITEM:
                market_item_id = params.get("market_item_id", 0)
                quantity = params.get("quantity", 1)
                result = await self.game_client.buy_exchange_offer(
                    market_item_id, player.company_id, quantity
                )
            
            elif action_id == Action.SELL_ITEM:
                item_id = params.get("item_id", 0)
                price = params.get("price", 100)
                quantity = params.get("quantity", 1)
                result = await self.game_client.create_exchange_offer(
                    player.company_id, self.session_id, str(item_id), quantity,
                    1, "money", price=price
                )
            
            elif action_id == Action.IMPROVE:
                improvement_type = params.get("improvement_type", "workshop")
                result = await self.game_client.update_company_improve(
                    player.company_id, improvement_type
                )
            
            elif action_id == Action.TAKE_CREDIT:
                amount = params.get("amount", 1000)
                period = params.get("period", 10)
                result = await self.game_client.company_take_credit(
                    player.company_id, amount, period
                )
            
            elif action_id == Action.PAY_CREDIT:
                credit_index = params.get("credit_index", 0)
                amount = params.get("amount", 500)
                result = await self.game_client.company_pay_credit(
                    player.company_id, credit_index, amount
                )
            
            elif action_id == Action.PAY_TAXES:
                amount = params.get("amount", 100)
                result = await self.game_client.company_pay_taxes(player.company_id, amount)
            
            elif action_id == Action.INTERACT:
                x = params.get("x", 0)
                y = params.get("y", 0)
                result = await self.game_client.set_company_position(
                    player.company_id, x, y
                )
            
            # Сохранение в историю
            self.game_history.append({
                "turn": self.current_turn,
                "player_id": player_id,
                "action": action_name,
                "params": action_params,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            self.logger.info(f"Действие {action_name} выполнено игроком {player_id}")
            return {
                "success": True,
                "action": action_name,
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка при выполнении действия {action_name}: {e}")
            return {
                "success": False,
                "action": action_name,
                "error": str(e)
            }
    
    async def next_turn(self) -> Dict[str, Any]:
        """Переход на следующий ход"""
        if self.current_phase != GamePhase.RUNNING:
            raise ValueError("Игра не запущена")
        
        self.current_turn += 1
        
        # Получение информации всех игроков
        turn_data = {
            "turn": self.current_turn,
            "players": {}
        }
        
        for player_id, player in self.players.items():
            try:
                company_info = await self.game_client.get_company(player.company_id)
                turn_data["players"][player_id] = company_info
            except Exception as e:
                self.logger.error(f"Ошибка получения информации игрока {player_id}: {e}")
        
        # Проверка условий окончания игры
        if self.current_turn >= self.max_turns:
            await self.finish_game()
        
        self.logger.info(f"Ход {self.current_turn} завершен")
        return turn_data
    
    async def get_game_state(self, player_id: int) -> GameState:
        """Получение состояния игры для игрока"""
        if player_id not in self.players:
            raise ValueError(f"Игрок {player_id} не найден")
        
        player = self.players[player_id]
        
        try:
            # Получение информации о компании
            company_info = await self.game_client.get_company(player.company_id)
            
            # Получение информации об улучшениях
            improvement_info = await self.game_client.get_company_improvement_info(player.company_id)
            
            # Получение товаров на бирже
            exchange_info = await self.game_client.get_exchanges(session_id=self.session_id, company_id=player.company_id)
            
            # Построение состояния
            state_dict = {
                "company": company_info.get("company", {}),
                "exchanges": exchange_info.get("exchanges", []) if exchange_info else [],
                "improvements": improvement_info.get("improvements", []) if improvement_info else [],
                "current_cell": {
                    "x": company_info.get("company", {}).get("x", 0),
                    "y": company_info.get("company", {}).get("y", 0),
                    "resource_type": 0,
                    "resource_amount": 0
                },
                "credits": company_info.get("company", {}).get("credits", []),
                "taxes": {"amount": 0}
            }
            
            return GameState(state_dict)
            
        except Exception as e:
            self.logger.error(f"Ошибка получения состояния игры: {e}")
            raise
    
    async def finish_game(self):
        """Завершение игры и оценка результатов"""
        self.current_phase = GamePhase.EVALUATION
        
        # Получение финальной информации о всех игроках
        rankings = []
        for player_id, player in self.players.items():
            try:
                company_info = await self.game_client.get_company(player.company_id)
                company = company_info.get("company", {})
                
                player.final_capital = company.get("balance", 0)
                player.reputation = company.get("reputation", 0)
                player.economic_level = company.get("economic_level", 0)
                
                rankings.append({
                    "player_id": player_id,
                    "company_name": player.name,
                    "capital": player.final_capital,
                    "reputation": player.reputation,
                    "economic_level": player.economic_level,
                    "profit": player.final_capital - player.initial_capital
                })
            except Exception as e:
                self.logger.error(f"Ошибка получения финальной информации игрока {player_id}: {e}")
        
        # Сортировка по капиталу
        rankings.sort(key=lambda x: x["capital"], reverse=True)
        for rank, player_data in enumerate(rankings, 1):
            player_data["rank"] = rank
        
        self.current_phase = GamePhase.FINISHED
        self.logger.info(f"Игра завершена. Рейтинг: {rankings}")
        
        return {
            "session_id": self.session_id,
            "total_turns": self.current_turn,
            "rankings": rankings,
            "game_history_length": len(self.game_history)
        }
    
    async def get_session_info(self) -> Dict[str, Any]:
        """Получение информации о сессии"""
        return {
            "session_id": self.session_id,
            "phase": self.current_phase.value,
            "current_turn": self.current_turn,
            "max_turns": self.max_turns,
            "player_count": len(self.players),
            "players": [asdict(p) for p in self.players.values()],
            "history_length": len(self.game_history)
        }
    
    async def cleanup(self):
        """Очистка ресурсов"""
        try:
            await self.game_client.disconnect()
            self.logger.info("Сессия очищена")
        except Exception as e:
            self.logger.error(f"Ошибка при очистке: {e}")
