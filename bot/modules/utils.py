from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from modules.ws_client import get_users, get_company
from oms import scene_manager

def list_to_inline(buttons, row_width=3):
    """ Преобразует список кнопок в inline-клавиатуру 
         Example:
              buttons = [ {'text': 'Кнопка 1', 'callback_data': 'btn1'},
                          {'text': 'Кнопка 2', 'callback_data': 'btn2', 'ignore_row': 'true'},
                          {'text': 'Кнопка 3', 'callback_data': 'btn3'} ]
              
              > Кнопка 1 | Кнопка 2 
                    | Кнопка 3
    """

    inline_keyboard = []
    row = []
    for button in buttons:

        if 'ignore_row' in button and (button['ignore_row'].lower() == 'true' or button['ignore_row'] == True):
            inline_keyboard.append(row)
            row = []
            inline_keyboard.append([InlineKeyboardButton(**button)])
            continue
        row.append(InlineKeyboardButton(**button))
        if len(row) == row_width:
            inline_keyboard.append(row)
            row = []
    if row:
        inline_keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


async def update_page(session_id, user_company_id, user_id, page_name):
    company_users = await get_users(session_id=session_id, company_id=user_company_id)
    for user in company_users:
        user_id_2 = user.get('id')
        if user_id_2 != user_id:
            if user_id_2 and scene_manager.has_scene(user_id_2):
                scene = scene_manager.get_scene(user_id_2)
                if scene and scene.page:
                    current_page_name = scene.page
                    if current_page_name == page_name:
                        await scene.update_message()
