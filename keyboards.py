
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_keyboard(buttons: list):
    keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    for button in buttons:
        keyboard.insert(InlineKeyboardButton(text=button['text'], callback_data=button['callback_data']))
    return keyboard
