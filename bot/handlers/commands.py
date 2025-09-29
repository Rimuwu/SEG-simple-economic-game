from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import os
import asyncio

from modules.keyboards import *
from modules.ws_client import *
from modules.utils import go_to_page
from filters.admins import *
from app.states import *

from bot_instance import dp, bot


# Список ID администраторов
UPDATE_PASSWORD = os.getenv("UPDATE_PASSWORD", "default_password")


@dp.message(AdminFilter(), Command("start_game"))
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
    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=msg_id,
        text=f"✅ Сессия с ID `{session_id}` успешно запущена!",
        parse_mode="Markdown"
    )
    await state.clear()
    

@dp.message(AdminFilter(), Command("create_game"))
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
    
    if response is None:
        await message.answer("❌ Ошибка при создании сессии. Ответа нет.")
        await state.clear()
        return
    
    elif "error" in response.keys():
        await message.answer(f"❌ Ошибка при создании сессии: {response['error']}")
        await state.clear()
        return
    
    await update_session_stage(
        session_id=response["session"]['session_id'],
        stage='FreeUserConnect',
    )
    await message.delete()
    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=msg_id,
        text=f"✅ Успешно создана игровая сессия!\n🆔 Код сессии: `{response['session']['session_id']}`",
        parse_mode="Markdown"
    )
    await state.clear()
