from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import os
import asyncio

from modules.ws_client import *
from modules.utils import go_to_page, update_page
from modules.db import db
from filters.admins import *
from app.states import *

from bot_instance import dp, bot


# Список ID администраторов
UPDATE_PASSWORD = os.getenv("UPDATE_PASSWORD", "default_password")


@dp.message(AdminFilter(), Command("sg"))
async def start_game(message: Message, state: FSMContext):
    msg = await message.answer("Введите ID сессии для её старта:")
    await state.update_data(msg_id=msg.message_id)
    await state.set_state(StartGameStates.waiting_for_session_id)

@dp.message(StartGameStates.waiting_for_session_id)
async def process_start_session_id(message: Message, state: FSMContext):
    session_id = message.text
    data = await state.get_data()
    msg_id = data['msg_id']
    response = await update_session_stage(
        session_id=session_id,
        stage='CellSelect',
    )
    
    await message.delete()
    if "error" in response.keys():
        await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=msg_id,
        text=f"❌ Ошибка при запуске сессии: {response['error']}"
        )
        await state.clear()
        return
    
    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=msg_id,
        text=f"✅ Сессия с ID `{session_id}` успешно запущена!",
        parse_mode="Markdown"
    )
    db.drop_all()
    await state.clear()
    

@dp.message(AdminFilter(), Command("cg"))
async def create_game(message: Message, state: FSMContext):
    msg = await message.answer("Введите ID сессии для новой игры или '-' для генерации ID:")
    await state.update_data(msg_id=msg.message_id)
    await state.set_state(CreateGameStates.waiting_for_session_id)


@dp.message(CreateGameStates.waiting_for_session_id)
async def process_session_id(message: Message, state: FSMContext):
    session_id = message.text
    data = await state.get_data()
    msg_id = data['msg_id']
    session_id_i = None if session_id == "-" else session_id
    response = await create_session(
        session_id=session_id_i
    )
    await message.delete()
    if response is None:
        await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=msg_id,
        text=f"❌ Ошибка при создании сессии. Ответа нет."
        )
        await state.clear()
        return
    
    elif "error" in response.keys():
        await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=msg_id,
        text=f"❌ Ошибка при создании сессии: {response['error']}"
        )
        await state.clear()
        return
    
    await update_session_stage(
        session_id=response["session"]['session_id'],
        stage='FreeUserConnect',
    )
    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=msg_id,
        text=f"✅ Успешно создана игровая сессия!\n🆔 Код сессии: `{response['session']['session_id']}`",
        parse_mode="Markdown"
    )
    await state.clear()

@dp.message(AdminFilter(), Command("ds"))
async def delete_session_command(message: Message, state: FSMContext):
    msg = await message.answer("Введите ID сессии для её удаления:")
    await state.update_data(msg_id=msg.message_id)
    await state.set_state(DeleteSessionStates.waiting_for_session_id)


@dp.message(DeleteSessionStates.waiting_for_session_id)
async def process_delete_session_id(message: Message, state: FSMContext):
    session_id = message.text
    data = await state.get_data()
    msg_id = data['msg_id']
    response = await delete_session(
        session_id=session_id,
        really=True
    )
    
    await message.delete()
    if response is not None and "error" in response.keys():
        await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=msg_id,
        text=f"❌ Ошибка при удалении сессии: {response['error']}"
        )
        await state.clear()
        return
    
    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=msg_id,
        text=f"✅ Сессия с ID `{session_id}` успешно удалена!",
        parse_mode="Markdown"
    )
    db.drop_all()
    await state.clear()

    
# http://localhost:8000/ws/status - тут можно посмотреть статус вебсокета и доступные типы для отправки сообщений через send_message
@dp.message(Command("ping"))
async def ping_command(message: Message):
    """Обработчик команды /ping"""
    try:
        # Отправляем ping через клиент
        response = await ws_client.send_message(
            "ping", {'from': message.from_user.id})
        print(f"Ответ от сервера: {response}")
    except Exception as e:
        await message.answer(f"Ошибка при выполнении ping: {str(e)}")

@ws_client.on_message('pong')
async def on_pong(message: dict):
    """Обработчик ответа pong от сервера"""
    print(f"Получен pong от сервера: {message}")

    from_id = message.get('content', {}).get('from')

    await bot.send_message(from_id, "Pong! 🏓")

@ws_client.on_event("connect")
async def on_connect():
    print("🔗 Подключено к WebSocket серверу")


@ws_client.on_message('api-update_session_stage')
async def on_update_session_stage(message: dict):
    """Обработчик обновления стадии сессии"""
    print(message)
    data = message.get('data', {})
    session_id = data.get('session_id')
    new_stage = data.get('new_stage')
    print("=====================", session_id, new_stage)
    if new_stage == "CellSelect":
        await go_to_page(session_id, "wait-start-page", "select-cell-page")
    elif new_stage == "Game":
        await go_to_page(session_id, "wait-game-stage-page", "main-page")


@ws_client.on_event("disconnect")
async def on_disconnect():
    print("❌ Отключено от WebSocket сервера")

    for _ in range(15, 0, -1):
        print(f"🔄 Попытка подключения...")
        await ws_client.connect(max_attempts=10)
        if ws_client.is_connected():
            print("✅ Повторное подключение успешно!")
            return

        print(f"❌ Не удалось подключиться, повтор через 1 секунду...")
        await asyncio.sleep(1)

    print("❌ Не удалось подключиться после 15 попыток, выход.")