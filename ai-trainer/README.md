# 🤖 Система обучения нейросети для SEG

Полная система обучения и управления нейросетями для игры SEG (Simple Economic Game). Позволяет обучать ботов с разными уровнями сложности, сохранять модели и тестировать их.

## 📋 Содержание

- [Требования](#требования)
- [Установка](#установка)
- [Использование](#использование)
  - [Быстрый старт](#быстрый-старт)
  - [Командная строка](#командная-строка)
  - [Интерактивный режим](#интерактивный-режим)
- [Архитектура](#архитектура)
- [Конфигурация](#конфигурация)
- [Примеры](#примеры)

## 🛠️ Требования

- Python 3.11+
- TensorFlow 2.16+
- WebSocket сервер SEG (api:81)

## 📦 Установка

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

Зависимости включают:
- `tensorflow` - для нейросетей (может быть заменено на pytorch)
- `numpy` - для работы с массивами
- `websockets` - для подключения к серверу
- `pydantic` - для валидации данных
- `python-dotenv` - для переменных окружения

### 2. Конфигурация

Скопируйте файл конфигурации:

```bash
cp config.json.example config.json
```

Отредактируйте `config.json` при необходимости:

```json
{
  "game_server": {
    "ws_uri": "ws://localhost:81/ws/connect",
    "update_password": "your_password"
  },
  "training_difficulty_levels": {
    "easy": {
      "iterations": 100,
      "learning_rate": 0.001
    },
    "hard": {
      "iterations": 1000,
      "learning_rate": 0.0001
    }
  }
}
```

### 3. Переменные окружения

Создайте файл `.env`:

```bash
cp .env.example .env
```

Отредактируйте `.env`:

```env
UPDATE_PASSWORD=your_update_password
WS_SERVER_URI=ws://localhost:81/ws/connect
DEBUG=false
```

## 🚀 Использование

### Быстрый старт

#### 1️⃣ Интерактивный режим (рекомендуется для начинающих)

```bash
python interactive.py
```

Откроется интерактивное меню с опциями:

```
📋 ГЛАВНОЕ МЕНЮ:

  1. 🚀 Обучить новую модель
  2. 🔄 Обучить несколько версий (Easy, Medium, Hard)
  3. 🧪 Тестировать модель
  4. 📊 Показать все модели
  5. ℹ️  Информация о модели
  6. 🗑️  Удалить модель
  0. ❌ Выход
```

#### 2️⃣ Командная строка

##### Обучение легкого бота

```bash
python train.py --easy --name bot_easy
```

##### Обучение сложного бота с 1000 эпизодов

```bash
python train.py --hard --episodes 1000 --name bot_hard
```

##### Обучение всех версий

```bash
python train.py --multi --name bot_complete
```

##### Тестирование модели

```bash
python train.py --test --name bot_easy --version 1
```

##### Просмотр всех моделей

```bash
python train.py --list
```

##### Информация о конкретной модели

```bash
python train.py --info --name bot_easy --version 1
```

## 📁 Архитектура

### Модули

| Файл | Описание |
|------|---------|
| `main.py` | Главное приложение, управление всем процессом |
| `train.py` | CLI скрипт для быстрого запуска из консоли |
| `interactive.py` | Интерактивный интерфейс меню |
| `neural_network.py` | Архитектура нейросети (Q-Learning) |
| `trainer.py` | Логика обучения и вознаграждения |
| `training_session.py` | Управление игровой сессией без таймеров |
| `ai_ws_client.py` | WebSocket клиент для взаимодействия с игрой |
| `model_storage.py` | Хранилище моделей и версионирование |
| `config.json` | Конфигурация всей системы |

### Поток данных

```
train.py/interactive.py
    ↓
AITrainerApp (main.py)
    ↓
Trainer (trainer.py)
    ├→ SEGNeuralNetwork (neural_network.py)
    ├→ TrainingSession (training_session.py)
    │   ├→ AIGameClient (ai_ws_client.py)
    │   └→ GameState (neural_network.py)
    ├→ ReplayBuffer (neural_network.py)
    └→ RewardCalculator (trainer.py)
    ↓
ModelStorage (model_storage.py)
    ├→ /models (сохраненные модели)
    ├→ /checkpoints (промежуточные checkpoint'ы)
    └→ /logs (логи обучения)
```

## ⚙️ Конфигурация

### config.json

```json
{
  "game_server": {
    "ws_uri": "ws://api:81/ws/connect",
    "update_password": "${UPDATE_PASSWORD}",
    "timeout": 60
  },
  
  "action_timeouts": {
    "inventory_open": 3,
    "market_sell_item": 15,
    "cell_select": 8
    // ... другие действия
  },
  
  "training_difficulty_levels": {
    "easy": {
      "iterations": 100,
      "learning_rate": 0.001,
      "batch_size": 32,
      "epochs": 5
    },
    "medium": {
      "iterations": 500,
      "learning_rate": 0.0005,
      "batch_size": 16,
      "epochs": 10
    },
    "hard": {
      "iterations": 1000,
      "learning_rate": 0.0001,
      "batch_size": 8,
      "epochs": 20
    },
    "expert": {
      "iterations": 2000,
      "learning_rate": 0.00005,
      "batch_size": 4,
      "epochs": 40
    }
  },
  
  "reward_system": {
    "capital_weight": 0.4,
    "reputation_weight": 0.3,
    "economic_level_weight": 0.3,
    "win_bonus": 1000,
    "loss_penalty": -100
  },
  
  "training_session": {
    "max_players": 4,
    "max_game_turns": 100,
    "skip_timers": true,
    "debug_mode": false
  },
  
  "model_storage": {
    "models_dir": "./models",
    "checkpoints_dir": "./checkpoints",
    "logs_dir": "./logs",
    "save_interval": 10
  }
}
```

### Уровни сложности

| Уровень | Итерации | Learning Rate | Описание |
|---------|----------|---------------|---------|
| **Easy** | 100 | 0.001 | Для тестирования, быстрое обучение |
| **Medium** | 500 | 0.0005 | Балансированный уровень |
| **Hard** | 1000 | 0.0001 | Серьезное обучение |
| **Expert** | 2000 | 0.00005 | Максимальное качество |

### Система наград

- **Капитал** (40%): Рост финансов
- **Репутация** (30%): Социальный статус
- **Экономический уровень** (30%): Развитие компании
- **Бонусы**: +1000 за победу, -100 за поражение

## 📚 Примеры

### Пример 1: Быстрое тестирование

```bash
# Обучить простую модель (10 эпизодов для теста)
python train.py --easy --episodes 10 --name test_bot

# Посмотреть результаты
python train.py --list

# Информация о модели
python train.py --info --name test_bot --version 1
```

### Пример 2: Полное обучение

```bash
# Обучить все версии с установками по умолчанию
python train.py --multi --name production_bot

# После завершения можно тестировать
python train.py --test --name production_bot_easy --version 1
```

### Пример 3: Кастомные параметры

```bash
# Обучить сложного бота с 2000 эпизодов и описанием
python train.py --hard \
  --episodes 2000 \
  --name expert_trader \
  --description "Эксперт в торговле акциями"
```

### Пример 4: Использование интерактивного режима

```bash
python interactive.py

# Интерактивно:
# 1. Обучить новую модель → выбрать easy/medium/hard/expert
# 2. Получить информацию о моделях
# 3. Тестировать модели
# 4. Удалить старые версии
```

## 🎓 Как работает обучение

### 1. Создание сессии

Создается игровая сессия с несколькими AI игроками.

### 2. Игровой цикл

На каждом ходу AI:
- Получает состояние игры
- Нейросеть выбирает действие
- Действие выполняется в игре
- Получается награда

### 3. Обучение

- Опыт сохраняется в буфер
- Нейросеть обучается на батчах
- Q-значения обновляются
- Модель улучшается

### 4. Сохранение

После каждого эпизода:
- Вычисляется финальная награда
- Модель сохраняется (периодически)
- Логи записываются

## 📊 Мониторинг

### Логи

Логи сохраняются в `/logs`:

```
logs/
├── training_20251029_120000.log
├── training_20251029_130000.log
└── ...
```

### Модели

Модели сохраняются в `/models`:

```
models/
├── registry.json
├── bot_easy_v1.h5
├── bot_easy_v1_metadata.json
├── bot_hard_v1.h5
└── ...
```

### Checkpoint'ы

Промежуточные checkpoint'ы в `/checkpoints`:

```
checkpoints/
├── bot_easy_episode_10.h5
├── bot_easy_episode_20.h5
└── ...
```

## 🔧 Поиск и устранение неисправностей

### Проблема: "ModuleNotFoundError: No module named 'tensorflow'"

**Решение:**
```bash
pip install tensorflow==2.16.0
```

### Проблема: "ConnectionRefusedError: [Errno 111] Connection refused"

**Решение:** Убедитесь, что WebSocket сервер запущен на указанном адресе:

```bash
# Проверьте WS_SERVER_URI в .env
# По умолчанию: ws://localhost:81/ws/connect
```

### Проблема: Обучение очень медленное

**Решение:**
- Уменьшите количество эпизодов
- Проверьте `batch_size` в конфиге
- Используйте GPU (установите `tensorflow-gpu`)

## 🚦 Статус

- ✅ Основная архитектура
- ✅ Q-Learning нейросеть
- ✅ Система тренировки
- ✅ Управление моделями
- ✅ Интерактивный CLI
- ⏳ Поддержка PyTorch
- ⏳ REST API для управления
- ⏳ WebUI для мониторинга

## 📝 Лицензия

MIT

## 👥 Авторы

SEG AI Trainer Team

---

**Последнее обновление:** 29 октября 2025

**Версия:** 1.0.0
