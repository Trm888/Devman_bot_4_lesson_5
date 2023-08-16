from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageToDeleteNotFound

from elasticpath_api import fetch_products, add_existing_product_to_cart, get_items_cart, get_total_price_cart, \
    delete_item, create_user
from keyboards import get_main_keyboard, get_add_quantity_keyboard, get_delete_item_keyboard
# from loader import dp
from utils import EmailCheck


class UserStates(StatesGroup):
    START = State()
    HANDLE_MENU = State()
    HANDLE_DESCRIPTION = State()
    CART_MENU = State()
    WAITING_EMAIL = State()


def register_handlers(dp, client_id, client_secret):
    @dp.message_handler(commands="start", state='*')
    async def cmd_start(message: types.Message, state: FSMContext):
        try:
            await message.delete()
        except MessageToDeleteNotFound:
            pass
        await UserStates.START.set()

        data = await state.get_data()
        products = data.get("products")
        if not products:
            products = await fetch_products(client_id, client_secret)
            await state.set_data({"products": products})
        buttons = []
        for product in products:
            buttons.append({'text': product['name'], 'callback_data': f"chosen_{product['id']}"})

        await message.answer("Привет! Выбери товар.", reply_markup=get_main_keyboard(buttons))
        await UserStates.HANDLE_MENU.set()

    @dp.callback_query_handler(lambda callback_query: callback_query.data == "cart",
                               state=[UserStates.HANDLE_MENU, UserStates.HANDLE_DESCRIPTION])
    async def get_cart(callback_query: types.CallbackQuery):
        await callback_query.message.delete()
        cart_items = await get_items_cart(callback_query.from_user.id, client_id, client_secret)
        if not cart_items:
            await callback_query.message.answer("Ваша корзина пуста.", reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(text='Назад', callback_data='back')))
            await UserStates.CART_MENU.set()
            return
        total_price = await get_total_price_cart(callback_query.from_user.id, client_id, client_secret)
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

    @dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("chosen_"),
                               state=UserStates.HANDLE_MENU)
    async def handle_menu(callback_query: types.CallbackQuery, state: FSMContext):
        product_id = callback_query.data.replace("chosen_", "")
        # button_text = callback_query.message.reply_markup.inline_keyboard[0][0].text
        # print(button_text)
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
        await callback_query.message.answer_photo(
            photo=chosen_product['url'],
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
            reply_markup=get_add_quantity_keyboard()
        )
        await UserStates.HANDLE_DESCRIPTION.set()

    @dp.callback_query_handler(lambda callback_query: callback_query.data == "back",
                               state=[UserStates.HANDLE_DESCRIPTION, UserStates.CART_MENU])
    async def cmd_back(callback_query: types.CallbackQuery, state: FSMContext):
        await callback_query.message.delete()
        await cmd_start(callback_query.message, state)

    @dp.callback_query_handler(state=UserStates.HANDLE_DESCRIPTION)
    async def handle_description(callback_query: types.CallbackQuery, state: FSMContext):
        user_data = await state.get_data()
        chosen_product = user_data.get("chosen_product")
        qty = int(callback_query.data)
        await add_existing_product_to_cart(
            chosen_product['id'],
            callback_query.from_user.id,
            client_id,
            client_secret,
            qty
        )
        await callback_query.answer("Товар добавлен в корзину!")

    @dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("remove_"),
                               state=UserStates.CART_MENU)
    async def handle_remove_item(callback_query: types.CallbackQuery):
        item_id = callback_query.data.replace("remove_", "")
        await delete_item(callback_query.from_user.id, item_id, client_id, client_secret)
        await callback_query.answer("Товар удален из корзины!")
        await get_cart(callback_query)

    @dp.callback_query_handler(lambda callback_query: callback_query.data == "pay", state=UserStates.CART_MENU)
    async def handle_pay(callback_query: types.CallbackQuery):
        await callback_query.message.edit_text("Пришлите мне пожалуйста вашу почту.")
        await UserStates.WAITING_EMAIL.set()

    @dp.message_handler(state=UserStates.WAITING_EMAIL)
    async def handle_email(message: types.Message, state: FSMContext):
        check_email = await EmailCheck().check(message)
        if not check_email:
            await message.answer("Неверный формат почты. Попробуйте еще раз.")
            return
        await message.answer(f"Спасибо за заказ! Ваша почта {message.text} принята.")
        await state.finish()
        await create_user(str(message.from_user.id), message.text, client_id, client_secret)
        await cmd_start(message, state)
