import textwrap

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageToDeleteNotFound

from elasticpath_api import fetch_products, add_existing_product_to_cart, get_items_cart, get_total_price_cart, \
    delete_item, create_user
from keyboards import get_main_keyboard, get_add_quantity_keyboard, get_delete_item_keyboard
from utils import EmailCheck, get_or_update_token


class UserStates(StatesGroup):
    START = State()
    HANDLE_MENU = State()
    HANDLE_DESCRIPTION = State()
    CART_MENU = State()
    WAITING_EMAIL = State()


class ConfigMiddleware(BaseMiddleware):

    def __init__(self, client_id, client_secret, host, port, redis_password):
        super().__init__()
        self.client_id = client_id
        self.client_secret = client_secret
        self.host = host
        self.port = port
        self.redis_password = redis_password

    async def on_pre_process_message(self, message, data):
        message.client_id = self.client_id
        message.client_secret = self.client_secret
        message.host = self.host
        message.port = self.port
        message.redis_password = self.redis_password

    async def on_pre_process_callback_query(self, callback_query: types.CallbackQuery, data):
        callback_query.client_id = self.client_id
        callback_query.client_secret = self.client_secret
        callback_query.host = self.host
        callback_query.port = self.port
        callback_query.redis_password = self.redis_password


async def cmd_start(message: types.Message, state: FSMContext):
    client_id = message.client_id
    client_secret = message.client_secret
    host = message.host
    port = message.port
    redis_password = message.redis_password
    try:
        await message.delete()
    except MessageToDeleteNotFound:
        pass
    await UserStates.START.set()

    data = await state.get_data()
    products = data.get("products")
    if not products:
        token = await get_or_update_token(client_id, client_secret, host, port, redis_password)

        products = await fetch_products(token)
        await state.set_data({"products": products})
    buttons = []
    for product in products:
        buttons.append({'text': product['name'], 'callback_data': f"chosen_{product['id']}"})

    await message.answer("Привет! Выбери товар.", reply_markup=get_main_keyboard(buttons))
    await UserStates.HANDLE_MENU.set()


async def get_cart(callback_query: types.CallbackQuery):
    client_id = callback_query.client_id
    client_secret = callback_query.client_secret
    host = callback_query.host
    port = callback_query.port
    redis_password = callback_query.redis_password
    await callback_query.message.delete()
    token = await get_or_update_token(client_id, client_secret, host, port, redis_password)
    cart_items = await get_items_cart(callback_query.from_user.id, token)
    if not cart_items:
        await callback_query.message.answer("Ваша корзина пуста.", reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(text='Назад', callback_data='back')))
        await UserStates.CART_MENU.set()
        return
    total_price = await get_total_price_cart(callback_query.from_user.id, token)
    cart_text = ""
    buttons = []
    for item in cart_items:
        cart_text += (f'Наименование товара: {item["name"]}\n'
                      f'Количество: {item["quantity"]}\n'
                      f'Цена: {item["price"]}\n\n')
        buttons.append({'text': f'Убрать {item["name"]}', 'callback_data': f'remove_{item["id"]}'})

    await callback_query.message.answer(f"В корзине:\n\n{cart_text}Общая сумма: {total_price}",
                                        reply_markup=get_delete_item_keyboard(buttons))
    await UserStates.CART_MENU.set()


async def handle_menu(callback_query: types.CallbackQuery, state: FSMContext):
    product_id = callback_query.data.replace("chosen_", "")
    user_data = await state.get_data()
    products = user_data.get("products")
    chosen_product = {}
    for product in products:
        if product['id'] == product_id:
            chosen_product = {
                'name': product['name'],
                'sku': product['sku'],
                'price': product['price'],
                'id': product['id'],
                'description': product['description'],
                'url': product['url']
            }
    await state.update_data({"chosen_product": chosen_product})
    await callback_query.message.delete()
    caption = textwrap.dedent(f"""
        Вы выбрали {chosen_product['name']}

        Описание: {chosen_product['description']}

        Цена: {chosen_product['price']}

        SKU: {chosen_product['sku']}

        ID: {chosen_product['id']}
    """)
    await callback_query.message.answer_photo(
        photo=chosen_product['url'],
        caption=caption,
        reply_markup=get_add_quantity_keyboard()
    )
    await UserStates.HANDLE_DESCRIPTION.set()


async def cmd_back(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    message = callback_query.message
    message.client_id = callback_query.client_id
    message.client_secret = callback_query.client_secret
    message.host = callback_query.host
    message.port = callback_query.port
    message.redis_password = callback_query.redis_password
    await cmd_start(callback_query.message, state)


async def handle_description(callback_query: types.CallbackQuery, state: FSMContext):
    client_id = callback_query.client_id
    client_secret = callback_query.client_secret
    host = callback_query.host
    port = callback_query.port
    redis_password = callback_query.redis_password
    user_data = await state.get_data()
    chosen_product = user_data.get("chosen_product")
    qty = int(callback_query.data)
    token = await get_or_update_token(client_id, client_secret, host, port, redis_password)
    await add_existing_product_to_cart(
        chosen_product['id'],
        callback_query.from_user.id,
        token,
        qty
    )
    await callback_query.answer("Товар добавлен в корзину!")


async def handle_remove_item(callback_query: types.CallbackQuery):
    client_id = callback_query.client_id
    client_secret = callback_query.client_secret
    host = callback_query.host
    port = callback_query.port
    redis_password = callback_query.redis_password
    token = await get_or_update_token(client_id, client_secret, host, port, redis_password)
    item_id = callback_query.data.replace("remove_", "")
    await delete_item(callback_query.from_user.id, item_id, token)
    await callback_query.answer("Товар удален из корзины!")
    await get_cart(callback_query)


async def handle_pay(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Пришлите мне пожалуйста вашу почту.")
    await UserStates.WAITING_EMAIL.set()


async def handle_email(message: types.Message, state: FSMContext):
    client_id = message.client_id
    client_secret = message.client_secret
    host = message.host
    port = message.port
    redis_password = message.redis_password
    check_email = await EmailCheck().check(message)
    if not check_email:
        await message.answer("Неверный формат почты. Попробуйте еще раз.")
        return
    await message.answer(f"Спасибо за заказ! Ваша почта {message.text} принята.")
    await state.finish()
    token = await get_or_update_token(client_id, client_secret, host, port, redis_password)
    await create_user(str(message.from_user.id), message.text, token)
    await cmd_start(message, state)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=['start'], state="*")
    dp.register_message_handler(handle_email, state=UserStates.WAITING_EMAIL)

    dp.register_callback_query_handler(
        get_cart,
        lambda callback_query: callback_query.data == "cart",
        state=[UserStates.HANDLE_MENU, UserStates.HANDLE_DESCRIPTION]
    )
    dp.register_callback_query_handler(
        handle_menu,
        lambda callback_query: callback_query.data.startswith("chosen_"),
        state=UserStates.HANDLE_MENU
    )
    dp.register_callback_query_handler(
        cmd_back,
        lambda callback_query: callback_query.data == "back",
        state=[UserStates.HANDLE_DESCRIPTION, UserStates.CART_MENU]
    )
    dp.register_callback_query_handler(
        handle_description,
        state=UserStates.HANDLE_DESCRIPTION
    )
    dp.register_callback_query_handler(
        handle_remove_item,
        lambda callback_query: callback_query.data.startswith("remove_"),
        state=UserStates.CART_MENU
    )
    dp.register_callback_query_handler(
        handle_pay,
        lambda callback_query: callback_query.data == "pay", state=UserStates.CART_MENU
    )
