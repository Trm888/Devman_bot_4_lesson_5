from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_keyboard(buttons: list):
    keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    for button in buttons:
        keyboard.insert(InlineKeyboardButton(text=button['text'], callback_data=button['callback_data']))
    return keyboard


# def get_back_keyboard():
#     keyboard = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#     keyboard.insert(InlineKeyboardButton(text='Назад', callback_data='back'))
#     return keyboard


def get_qty_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    for num in range(5):
        keyboard.insert(InlineKeyboardButton(text=f'{num + 1} кг', callback_data=str(num + 1)))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='back'))
    return keyboard
