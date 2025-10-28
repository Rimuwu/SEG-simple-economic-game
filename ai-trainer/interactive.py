#!/usr/bin/env python3
"""
Интерактивный тренер с меню
Позволяет управлять обучением через интерактивное меню
"""

import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import asyncio
import sys
import json
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from os import environ

from main import AITrainerApp


class InteractiveTrainer:
    """Интерактивный интерфейс для тренера"""
    
    def __init__(self):
        self.app = None
        self.running = True
    
    async def initialize(self):
        """Инициализация приложения"""
        try:
            self.app = AITrainerApp("config.json")
            return True
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            return False
    
    def print_header(self):
        """Печать заголовка"""
        print("\n" + "="*70)
        print("🤖 ИНТЕРАКТИВНЫЙ ТРЕНЕР НЕЙРОСЕТИ ДЛЯ SEG")
        print("="*70 + "\n")
    
    def print_menu(self):
        """Печать главного меню"""
        print("\n📋 ГЛАВНОЕ МЕНЮ:\n")
        print("  1. 🚀 Обучить новую модель")
        print("  2. 🔄 Обучить несколько версий (Easy, Medium, Hard)")
        print("  3. 🧪 Тестировать модель")
        print("  4. 📊 Показать все модели")
        print("  5. ℹ️  Информация о модели")
        print("  6. 🗑️  Удалить модель")
        print("  0. ❌ Выход")
        print("\n" + "-"*70)
    
    async def train_single_model(self):
        """Обучение одной модели"""
        print("\n🎓 ОБУЧЕНИЕ ОДНОЙ МОДЕЛИ\n")
        
        name = input("Введите название модели: ").strip()
        if not name:
            print("❌ Название не может быть пустым")
            return
        
        print("\nВыберите сложность:")
        print("  1. Easy (100 эпизодов)")
        print("  2. Medium (500 эпизодов)")
        print("  3. Hard (1000 эпизодов)")
        print("  4. Expert (2000 эпизодов)")
        
        choice = input("\nВведите номер (1-4): ").strip()
        difficulty_map = {
            "1": ("easy", 100),
            "2": ("medium", 500),
            "3": ("hard", 1000),
            "4": ("expert", 2000)
        }
        
        if choice not in difficulty_map:
            print("❌ Неверный выбор")
            return
        
        difficulty, default_episodes = difficulty_map[choice]
        
        episodes_input = input(f"Количество эпизодов [{default_episodes}]: ").strip()
        episodes = int(episodes_input) if episodes_input else default_episodes
        
        num_agents_input = input("Количество AI ботов в сессии [2]: ").strip()
        num_agents = int(num_agents_input) if num_agents_input else 2
        num_agents = max(2, num_agents)  # Минимум 2 бота
        
        description = input("Описание модели (опционально): ").strip()
        
        print(f"\n⏳ Обучение {name} ({difficulty}, {episodes} эпизодов, {num_agents} ботов)...")
        print("   Это может занять время...\n")
        
        result = await self.app.train_model(
            name=name,
            difficulty=difficulty,
            episodes=episodes,
            description=description,
            num_agents=num_agents
        )
        
        if result["success"]:
            print(f"\n✅ Успешно!\n")
            print(f"  📦 Модель: {result['model_name']} v{result['model_version']}")
            print(f"  🎓 Эпизодов: {result['episodes_trained']}")
            print(f"  📊 Средняя награда: {result['average_reward']:.2f}")
            print(f"  🏆 Лучшая награда: {result['best_reward']:.2f}")
        else:
            print(f"❌ Ошибка: {result.get('error', 'Unknown error')}")
    
    async def train_multiple_versions(self):
        """Обучение нескольких версий"""
        print("\n🔄 ОБУЧЕНИЕ ВСЕХ ВЕРСИЙ\n")
        
        base_name = input("Введите базовое название модели: ").strip()
        if not base_name:
            print("❌ Название не может быть пустым")
            return
        
        print("\nУкажите параметры обучения для каждой версии:")
        print("Нажмите Enter для использования значений по умолчанию\n")
        
        versions_config = {}
        
        for difficulty, default_episodes in [("easy", 100), ("medium", 500), ("hard", 1000)]:
            episodes_input = input(f"  {difficulty.upper()} [{default_episodes}]: ").strip()
            episodes = int(episodes_input) if episodes_input else default_episodes
            versions_config[difficulty] = episodes
        
        print(f"\n⏳ Обучение {base_name} (все версии)...")
        print("   Это может занять продолжительное время...\n")
        
        result = await self.app.train_multiple_versions(base_name, versions_config)
        
        print(f"\n✅ Обучение завершено!\n")
        
        for difficulty, version_result in result["versions"].items():
            if version_result.get("success"):
                print(f"  ✓ {difficulty.upper()}: v{version_result['model_version']}")
                print(f"    Награда: {version_result['average_reward']:.2f}")
            else:
                print(f"  ✗ {difficulty.upper()}: {version_result.get('error')}")
    
    async def test_model(self):
        """Тестирование модели"""
        print("\n🧪 ТЕСТИРОВАНИЕ МОДЕЛИ\n")
        
        name = input("Введите название модели: ").strip()
        if not name:
            print("❌ Название не может быть пустым")
            return
        
        version_input = input("Введите версию модели: ").strip()
        if not version_input.isdigit():
            print("❌ Версия должна быть числом")
            return
        
        version = int(version_input)
        
        num_games_input = input("Количество тестовых игр [5]: ").strip()
        num_games = int(num_games_input) if num_games_input else 5
        
        print(f"\n⏳ Тестирование {name} v{version}...")
        
        result = await self.app.test_model(name, version, num_games)
        
        if result.get("success"):
            print(f"\n✅ Тестирование завершено!\n")
            print(f"  🎮 Игр сыграно: {len(result['games'])}")
            print(f"  📊 Средний рейтинг: {result['average_rank']:.2f}")
        else:
            print(f"❌ Ошибка: {result.get('error')}")
    
    def show_models(self):
        """Показать все модели"""
        print("\n📊 СПИСОК ВСЕХ МОДЕЛЕЙ\n")
        
        print("Выберите сложность:")
        print("  1. Все")
        print("  2. Easy")
        print("  3. Medium")
        print("  4. Hard")
        print("  5. Expert")
        
        choice = input("\nВведите номер (1-5): ").strip()
        difficulty_map = {
            "1": None,
            "2": "easy",
            "3": "medium",
            "4": "hard",
            "5": "expert"
        }
        
        if choice not in difficulty_map:
            print("❌ Неверный выбор")
            return
        
        difficulty = difficulty_map[choice]
        result = self.app.list_models(difficulty)
        
        if result["total_models"] == 0:
            print("\n📭 Моделей не найдено")
        else:
            print(f"\n📦 Найдено моделей: {result['total_models']}\n")
            
            for model in result["models"]:
                print(f"  {model['name']} v{model['version']}")
                print(f"    Сложность: {model['difficulty']}")
                print(f"    Сохранена: {model['saved_at']}")
                print()
    
    def show_model_info(self):
        """Показать информацию о модели"""
        print("\n ℹ️  ИНФОРМАЦИЯ О МОДЕЛИ\n")
        
        name = input("Введите название модели: ").strip()
        if not name:
            print("❌ Название не может быть пустым")
            return
        
        version_input = input("Введите версию модели: ").strip()
        if not version_input.isdigit():
            print("❌ Версия должна быть числом")
            return
        
        version = int(version_input)
        result = self.app.get_model_info(name, version)
        
        if result["success"]:
            print(f"\n📋 Информация о {name} v{version}:\n")
            info = result["info"]
            
            if "name" in info:
                print(f"  Название: {info.get('name')}")
                print(f"  Версия: {info.get('version')}")
                print(f"  Сложность: {info.get('difficulty')}")
                print(f"  Создана: {info.get('created_at')}")
                print(f"  Эпизодов: {info.get('trained_episodes')}")
                print(f"  Средняя награда: {info.get('average_reward'):.2f}")
                print(f"  Лучшая награда: {info.get('best_reward'):.2f}")
                if info.get('description'):
                    print(f"  Описание: {info.get('description')}")
            else:
                print(json.dumps(info, indent=2, ensure_ascii=False))
        else:
            print(f"❌ {result['error']}")
    
    def delete_model(self):
        """Удалить модель"""
        print("\n🗑️  УДАЛЕНИЕ МОДЕЛИ\n")
        
        name = input("Введите название модели: ").strip()
        if not name:
            print("❌ Название не может быть пустым")
            return
        
        version_input = input("Введите версию модели: ").strip()
        if not version_input.isdigit():
            print("❌ Версия должна быть числом")
            return
        
        version = int(version_input)
        
        confirm = input(f"\nУдалить {name} v{version}? (да/нет): ").strip().lower()
        if confirm != "да":
            print("❌ Удаление отменено")
            return
        
        result = self.app.delete_model(name, version)
        
        if result["success"]:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ {result['message']}")
    
    async def run(self):
        """Главной цикл"""
        print("Запуск интерактивного тренера нейросети для SEG....\n")
        if not await self.initialize():
            print("❌ Не удалось инициализировать приложение")
            return

        self.print_header()
        print("✅ Приложение инициализировано\n")
        
        while self.running:
            try:
                self.print_menu()
                choice = input("Введите команду: ").strip()
                
                if choice == "1":
                    await self.train_single_model()
                elif choice == "2":
                    await self.train_multiple_versions()
                elif choice == "3":
                    await self.test_model()
                elif choice == "4":
                    self.show_models()
                elif choice == "5":
                    self.show_model_info()
                elif choice == "6":
                    self.delete_model()
                elif choice == "0":
                    print("\n👋 До встречи!\n")
                    self.running = False
                else:
                    print("❌ Неверный выбор")
            
            except KeyboardInterrupt:
                print("\n\n👋 До встречи!")
                self.running = False
            except Exception as e:
                print(f"❌ Ошибка: {e}")


async def main():
    print("Запуск интерактивного тренера нейросети для SEG....\n")
    trainer = InteractiveTrainer()
    await trainer.run()


if __name__ == "__main__":
    print("Запуск интерактивного тренера нейросети для SEG...\n")
    asyncio.run(main())
