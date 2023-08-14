from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup

from keyboards import get_main_keyboard
from loader import dp
from elasticpath_api import fetch_products


class UserStates(StatesGroup):
    START = State()
    HANDLE_MENU = State()


@dp.message_handler(commands="start", state='*')
async def cmd_start(message: types.Message):
    await UserStates.START.set()
    # r = redis_db
    # keys = await r._redis.keys('*')
    # values = await r._redis.mget(*keys)
    # print(keys)
    # print(values)
    products = await fetch_products()
    buttons = []
    for product in products:
        buttons.append({'text': product['name'], 'callback_data': product['id']})

    await message.answer("Привет! Выбери товар.", reply_markup=get_main_keyboard(buttons))
    await UserStates.HANDLE_MENU.set()


@dp.callback_query_handler(state=UserStates.HANDLE_MENU)
async def handle_menu(callback_query: types.CallbackQuery):
    product_id = callback_query.data
    # button_text = callback_query.message.reply_markup.inline_keyboard[0][0].text
    # print(button_text)

    products = await fetch_products()
    chosen_product = {}
    for product in products:
        if product['id'] == product_id:
            chosen_product = {'name': product['name'],
                              'sku': product['sku'],
                              'price': product['price'],
                              'id': product['id'],
                              'description': product['description'],
                              'url': product['url']}
    await callback_query.message.delete()
    await callback_query.message.answer_photo(photo=chosen_product['url'],
                                              caption=f"Вы выбрали {chosen_product['name']}"
                                                      f"\n\n"
                                                      f"Описание: {chosen_product['description']}"
                                                      f"\n\n"
                                                      f"Цена: {chosen_product['price']}"
                                                      f"\n\n"
                                                      f"SKU: {chosen_product['sku']}"
                                                      f"\n\n"
                                                      f"ID: {chosen_product['id']}"
                                                      f"\n\n"
                                                      f"Хотите добавить в корзину?")
    await UserStates.HANDLE_MENU.set()

# @dp.message_handler(content_types=types.ContentTypes.TEXT, state=UserStates.ECHO)
# async def echo(message: types.Message):
#     user_id = str(message.from_user.id)
#     print(user_id)
#     r = redis_db
#     keys = await r._redis.keys('*')
#     values = await r._redis.mget(*keys)
#     print(keys)
#     print(values)
#     await UserStates.ECHO.set()
#     await message.answer(message.text)
