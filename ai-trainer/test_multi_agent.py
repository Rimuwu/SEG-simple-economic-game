#!/usr/bin/env python3
"""
Тестирование многоагентного тренера
"""
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from main import AITrainerApp


async def test_multi_agent_training():
    """Тест обучения с несколькими агентами"""
    try:
        # Инициализация приложения
        app = AITrainerApp("config.json")
        
        print("✅ Приложение инициализировано\n")
        
        # Обучение модели с 2 агентами (основной + 1 оппонент)
        print("🤖 Начало обучения модели с 2 агентами...")
        result = await app.train_model(
            name="test_multi_agent",
            difficulty="easy",
            episodes=2,  # Только 2 эпизода для теста
            description="Тест многоагентного обучения",
            num_agents=2
        )
        
        if result["success"]:
            print(f"\n✅ Обучение успешно завершено!")
            print(f"  📦 Модель: {result['model_name']} v{result['model_version']}")
            print(f"  📊 Эпизодов: {result['episodes_trained']}")
            print(f"  🏆 Средняя награда: {result['average_reward']:.2f}")
            print(f"  🥇 Лучшая награда: {result['best_reward']:.2f}")
        else:
            print(f"\n❌ Ошибка обучения: {result.get('error')}")
            
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_multi_agent_training())
