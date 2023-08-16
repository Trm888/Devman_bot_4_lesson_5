from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_keyboard(buttons: list):
    keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    for button in buttons:
        keyboard.insert(InlineKeyboardButton(text=button['text'], callback_data=button['callback_data']))
    keyboard.add(InlineKeyboardButton(text='Корзина', callback_data='cart'))
    return keyboard


def get_add_quantity_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    for num in range(5):
        keyboard.insert(InlineKeyboardButton(text=f'{num + 1} кг', callback_data=str(num + 1)))
    keyboard.add(InlineKeyboardButton(text='Корзина', callback_data='cart'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='back'))
    return keyboard


def get_delete_item_keyboard(buttons: list):
    keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    for button in buttons:
        keyboard.insert(InlineKeyboardButton(text=button['text'], callback_data=button['callback_data']))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='back'))
    keyboard.add(InlineKeyboardButton(text='Оплатить', callback_data='pay'))
    return keyboard
