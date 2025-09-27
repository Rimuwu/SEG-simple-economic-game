from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import os

from modules.keyboards import *
from modules.ws_client import *
from filters.admins import *
from app.states import *

from bot_instance import dp, bot


# Список ID администраторов
UPDATE_PASSWORD = os.getenv("UPDATE_PASSWORD", "default_password")

@dp.message(Command("connect"))
async def connect(message: Message, state: FSMContext):
    session = await get_sessions()
    for s in session:
        s_id = s['session_id']
        user = await get_user(id=message.from_user.id, session_id=s_id)
        if user is not None:
            await message.delete()
            await message.answer("❌ Вы уже подключены к сессии.")
            return
    await state.update_data(msg_id=message.message_id + 1, chat_id=message.chat.id)
    await message.answer(text="Введите ваш никнейм для подключения к игре: ", reply_markup=cancel_kb)
    await state.set_state(CreateUserStates.waiting_for_username)


@dp.message(CreateUserStates.waiting_for_username)
async def process_username(message: Message, state: FSMContext):
    username = message.text.strip()
    data = await state.get_data()
    msg_id = data.get("msg_id")
    chat_id = data.get("chat_id")
    if not username:
        await message.answer("❌ Никнейм не может быть пустым. Пожалуйста, введите корректный никнейм:")
        return
    await message.delete()
    await message.bot.edit_message_text(f"Теперь введите id сессии для подключения, {username}:", message_id=msg_id, chat_id=chat_id, reply_markup=cancel_kb)
    await state.update_data(username=username)
    await state.set_state(CreateUserStates.waiting_for_session_id)


@dp.message(CreateUserStates.waiting_for_session_id)
async def process_session_id(message: Message, state: FSMContext):
    session_id = message.text
    data = await state.get_data()
    username = data.get("username")
    msg_id = data['msg_id']
    chat_id = data['chat_id']
    if len(session_id.split()) != 1:
        await message.bot.edit_message_text("❌ ID сессии должен состоять из одного слова. Пожалуйста, введите корректный ID сессии:", message_id=msg_id, chat_id=chat_id, reply_markup=cancel_kb)
        return
    response = await get_sessions(stage='FreeUserConnect')
    for session in response:
        if session['session_id'] == session_id:
            break
    else:
        await message.bot.edit_message_text("❌ ID сессии не найден. Пожалуйста, введите корректный ID сессии:", message_id=msg_id, chat_id=chat_id, reply_markup=cancel_kb)
        return

    await create_user(
        user_id=message.from_user.id,
        username=username,
        session_id=session_id,
        password=UPDATE_PASSWORD
    )
    await message.delete()
    await message.bot.edit_message_text(
        f"✅ Вы успешно подключены к игре с ID сессии: {session_id}\n\n"
        f"Выберите действие:",
        reply_markup=create_company_keyboard,
        message_id=msg_id,
        chat_id=chat_id
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


# Обработчики для управления компанией
@dp.callback_query(F.data == "create_company")
async def create_company_start(callback: CallbackQuery, state: FSMContext):
    """
    Начинаем процесс создания компании
    """
    # Сохраняем ID исходного сообщения и chat_id в состоянии
    await state.update_data(
        original_message_id=callback.message.message_id,
        chat_id=callback.message.chat.id
    )
    
    await callback.message.edit_text(
        "🏢 Создание компании\n\nВведите название для вашей компании:",
        reply_markup=cancel_kb
    )
    await state.set_state(CreateCompanyStates.waiting_for_company_name)
    await callback.answer()


@dp.message(CreateCompanyStates.waiting_for_company_name)
async def process_company_name(message: Message, state: FSMContext):
    """
    Обрабатываем название компании и создаем её
    """
    company_name = message.text.strip()
    
    # Получаем данные из состояния
    data = await state.get_data()
    original_message_id = data.get('original_message_id')
    chat_id = data.get('chat_id')
    
    # Создаем компанию
    response = await create_company(
        name=company_name,
        who_create=message.from_user.id,
        password=UPDATE_PASSWORD
    )
    
    # Удаляем сообщение с вводом названия
    await message.delete()
    
    # Редактируем исходное сообщение с информацией о компании
    company_info = (
        f"🏢 **{company_name}**\n\n"
        f"👥 Количество участников: 1\n"
        f"🔑 Секретный код: {response['company']['secret_code']}"
    )
    
    # Используем bot из message для редактирования исходного сообщения
    await message.bot.edit_message_text(
        chat_id=chat_id,
        message_id=original_message_id,
        text=company_info,
        parse_mode="Markdown"
    )
    
    await state.clear()


@dp.callback_query(F.data == "join_company")
async def join_company_start(callback: CallbackQuery, state: FSMContext):
    """
    Начинаем процесс присоединения к компании
    """
    # Сохраняем ID исходного сообщения и chat_id в состоянии
    await state.update_data(
        original_message_id=callback.message.message_id,
        chat_id=callback.message.chat.id
    )
    
    await callback.message.edit_text(
        "🤝 Присоединение к компании\n\nВведите секретный код компании:",
        reply_markup=cancel_kb
    )
    await state.set_state(JoinCompanyStates.waiting_for_secret_code)
    await callback.answer()


@dp.message(JoinCompanyStates.waiting_for_secret_code)
async def process_secret_code(message: Message, state: FSMContext):
    """
    Обрабатываем секретный код и присоединяем к компании
    """
    secret_code = message.text.strip()
    
    if not secret_code:
        await message.answer("❌ Секретный код не может быть пустым. Введите корректный код:")
        return
    
    # Получаем данные из состояния
    data = await state.get_data()
    original_message_id = data.get('original_message_id')
    chat_id = data.get('chat_id')
    
    # Присоединяемся к компании
    response = await update_company_add_user(
        user_id=message.from_user.id,
        secret_code=int(secret_code),
        password=UPDATE_PASSWORD
    )
    
    # Удаляем сообщение с вводом кода
    await message.delete()
    
    # Редактируем исходное сообщение с информацией о компании
    company_info = (
        f"🏢 **Название компании**\n\n"
        f"👥 Количество участников: 5\n"
        f"🔑 Секретный код: {secret_code}"
    )
    
    # Используем bot из message для редактирования исходного сообщения
    await message.bot.edit_message_text(
        chat_id=chat_id,
        message_id=original_message_id,
        text=company_info,
        parse_mode="Markdown"
    )
    
    await state.clear()

# Добавляем обработчик для отмены создания игры
@dp.callback_query(F.data == "cancel_ac")
async def cancel_creation(callback: CallbackQuery, state: FSMContext):
    """
    Отменяем создание игры
    """
    current_state = await state.get_state()
    if current_state is None:
        await callback.answer("Нет активного процесса для отмены.", show_alert=True)
        return
    
    await state.clear()
    
    # Удаляем сообщение с кнопкой
    await callback.message.delete()
    
    # Отправляем новое сообщение об отмене
    await callback.message.answer("❌ Действие отменено.")
    
    # Подтверждаем нажатие кнопки
    await callback.answer()

