#!/usr/bin/env python3
"""
Скрипт для быстрого запуска обучения нейросети из консоли
Использование: python train.py [опции]

Примеры:
    python train.py --easy --episodes 100
    python train.py --hard --episodes 1000
    python train.py --multi
"""

import asyncio
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Добавляем текущую директорию в path для импорта локальных модулей
sys.path.insert(0, str(Path(__file__).parent))

from main import AITrainerApp


def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description="Обучение нейросети для игры SEG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Обучение легкого бота (100 эпизодов)
  python train.py --easy --episodes 100 --name bot_easy

  # Обучение сложного бота (1000 эпизодов)
  python train.py --hard --episodes 1000 --name bot_hard

  # Обучение всех версий (easy, medium, hard)
  python train.py --multi --name bot_complete

  # Тестирование модели
  python train.py --test --name bot_easy --version 1

  # Список всех моделей
  python train.py --list

  # Список моделей сложности easy
  python train.py --list --easy
        """
    )
    
    # Группа действий
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument("--train", action="store_true", default=True,
                             help="Обучение модели (по умолчанию)")
    action_group.add_argument("--multi", action="store_true",
                             help="Обучение всех версий (easy, medium, hard)")
    action_group.add_argument("--test", action="store_true",
                             help="Тестирование модели")
    action_group.add_argument("--list", action="store_true",
                             help="Показать список моделей")
    action_group.add_argument("--info", action="store_true",
                             help="Информация о модели")
    
    # Группа сложности
    difficulty_group = parser.add_mutually_exclusive_group()
    difficulty_group.add_argument("--easy", action="store_const", const="easy", dest="difficulty",
                                 help="Легкая сложность (100 эпизодов)")
    difficulty_group.add_argument("--medium", action="store_const", const="medium", dest="difficulty",
                                 help="Средняя сложность (500 эпизодов)")
    difficulty_group.add_argument("--hard", action="store_const", const="hard", dest="difficulty",
                                 help="Сложная (1000 эпизодов)")
    difficulty_group.add_argument("--expert", action="store_const", const="expert", dest="difficulty",
                                 help="Экспертная (2000 эпизодов)")
    
    # Параметры
    parser.add_argument("--name", type=str, help="Название модели")
    parser.add_argument("--version", type=int, help="Версия модели (для test/info)")
    parser.add_argument("--episodes", type=int, help="Количество эпизодов (переопределяет сложность)")
    parser.add_argument("--config", type=str, default="config.json", help="Путь к конфигурации")
    parser.add_argument("--description", type=str, default="", help="Описание модели")
    
    return parser.parse_args()


async def main():
    """Главная функция"""
    args = parse_arguments()
    
    # Инициализация приложения
    try:
        app = AITrainerApp(args.config)
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return 1
    
    print("\n" + "="*60)
    print("🤖 Система обучения нейросети для SEG")
    print("="*60 + "\n")
    
    try:
        if args.list:
            # Показать список моделей
            result = app.list_models(args.difficulty)
            
            if result["total_models"] == 0:
                print("📭 Моделей не найдено")
            else:
                print(f"📊 Найдено моделей: {result['total_models']}\n")
                
                for model in result["models"]:
                    print(f"  📦 {model['name']} v{model['version']}")
                    print(f"     Сложность: {model['difficulty']}")
                    print(f"     Сохранена: {model['saved_at']}")
                    print()
        
        elif args.info:
            if not args.name or args.version is None:
                print("❌ Требуются параметры: --name и --version")
                return 1
            
            result = app.get_model_info(args.name, args.version)
            
            if result["success"]:
                info = result["info"]
                print(f"\n📋 Информация о модели {args.name} v{args.version}:\n")
                print(json.dumps(info, indent=2, ensure_ascii=False))
            else:
                print(f"❌ {result['error']}")
                return 1
        
        elif args.test:
            if not args.name or args.version is None:
                print("❌ Требуются параметры: --name и --version")
                return 1
            
            print(f"🧪 Тестирование модели {args.name} v{args.version}...")
            result = await app.test_model(args.name, args.version, num_test_games=5)
            
            if result["success"]:
                print(f"\n✅ Тестирование завершено")
                print(f"   Средний рейтинг: {result['average_rank']:.2f}")
                print(f"   Игр сыграно: {len(result['games'])}")
            else:
                print(f"❌ {result.get('error', 'Неизвестная ошибка')}")
                return 1
        
        elif args.multi:
            if not args.name:
                print("❌ Требуется параметр: --name")
                return 1
            
            print(f"🚀 Обучение всех версий модели {args.name}...\n")
            
            # Определение конфигурации для каждой версии
            versions_config = {
                "easy": 100,
                "medium": 500,
                "hard": 1000
            }
            
            result = await app.train_multiple_versions(args.name, versions_config)
            
            if all(v.get("success") for v in result["versions"].values()):
                print("\n✅ Все версии успешно обучены!\n")
                
                for difficulty, version_result in result["versions"].items():
                    if version_result.get("success"):
                        print(f"  ✓ {difficulty.upper()}: {version_result['model_version']} "
                             f"(v{version_result['model_version']})")
                        print(f"    Средняя награда: {version_result['average_reward']:.2f}")
            else:
                print("\n⚠️ Некоторые версии не обучены:")
                for difficulty, version_result in result["versions"].items():
                    if not version_result.get("success"):
                        print(f"  ✗ {difficulty}: {version_result.get('error', 'Unknown error')}")
                return 1
        
        else:  # Обучение одной модели
            if not args.name:
                print("❌ Требуется параметр: --name")
                print("Например: python train.py --name bot_easy --easy")
                return 1
            
            difficulty = args.difficulty or "easy"
            episodes = args.episodes
            
            print(f"🚀 Обучение модели: {args.name}")
            print(f"   Сложность: {difficulty}")
            if episodes:
                print(f"   Эпизодов: {episodes}")
            print()
            
            result = await app.train_model(
                name=args.name,
                difficulty=difficulty,
                episodes=episodes,
                description=args.description or f"Training {difficulty} model"
            )
            
            if result["success"]:
                print(f"\n✅ Обучение завершено!\n")
                print(f"  📦 Модель: {result['model_name']} v{result['model_version']}")
                print(f"  🎓 Эпизодов: {result['episodes_trained']}")
                print(f"  📊 Средняя награда: {result['average_reward']:.2f}")
                print(f"  🏆 Лучшая награда: {result['best_reward']:.2f}")
            else:
                print(f"\n❌ Ошибка обучения: {result.get('error', 'Unknown error')}")
                return 1
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Обучение прервано пользователем")
        return 1
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n" + "="*60 + "\n")
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
