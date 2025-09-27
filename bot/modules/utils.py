from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

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