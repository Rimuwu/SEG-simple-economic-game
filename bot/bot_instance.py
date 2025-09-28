"""
Модуль для инициализации экземпляров бота и диспетчера.
Этот модуль создан для избежания циклических импортов.
"""
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Инициализация бота и диспетчера с хранилищем для FSM
storage = MemoryStorage()
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(storage=storage)