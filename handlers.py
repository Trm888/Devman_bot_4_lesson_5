from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from elasticpath_api import fetch_products, add_existing_product_to_cart
from keyboards import get_main_keyboard, get_qty_keyboard
from loader import dp


class UserStates(StatesGroup):
    START = State()
    HANDLE_MENU = State()
    HANDLE_DESCRIPTION = State()


@dp.message_handler(commands="start", state='*')
async def cmd_start(message: types.Message, state: FSMContext):
    await UserStates.START.set()

    data = await state.get_data()
    products = data.get("products")
    print(products)
    if not products:
        products = await fetch_products()
        await state.set_data({"products": products})
    # r = redis_db
    # keys = await r._redis.keys('*')
    # values = await r._redis.mget(*keys)
    # print(keys)
    # print(values)
    # products = await fetch_products()
    buttons = []
    for product in products:
        buttons.append({'text': product['name'], 'callback_data': product['id']})

    await message.answer("Привет! Выбери товар.", reply_markup=get_main_keyboard(buttons))
    await UserStates.HANDLE_MENU.set()


@dp.callback_query_handler(state=UserStates.HANDLE_MENU)
async def handle_menu(callback_query: types.CallbackQuery, state: FSMContext):
    product_id = callback_query.data
    # button_text = callback_query.message.reply_markup.inline_keyboard[0][0].text
    # print(button_text)
    user_data = await state.get_data()
    products = user_data.get("products")
    chosen_product = {}
    for product in products:
        if product['id'] == product_id:
            chosen_product = {'name': product['name'],
                              'sku': product['sku'],
                              'price': product['price'],
                              'id': product['id'],
                              'description': product['description'],
                              'url': product['url']}
    await state.update_data({"chosen_product": chosen_product})
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
                                                      f"\n\n",
                                              reply_markup=get_qty_keyboard()
                                              )
    await UserStates.HANDLE_DESCRIPTION.set()


@dp.callback_query_handler(lambda callback_query: callback_query.data == "back", state=UserStates.HANDLE_DESCRIPTION)
async def cmd_back(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await cmd_start(callback_query.message, state)


@dp.callback_query_handler(state=UserStates.HANDLE_DESCRIPTION)
async def handle_description(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    chosen_product = user_data.get("chosen_product")
    user_id = str(callback_query.from_user.id)

    qty = int(callback_query.data)
    await add_existing_product_to_cart(chosen_product['id'], user_id, qty)
    print(user_id)


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
