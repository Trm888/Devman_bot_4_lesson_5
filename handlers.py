from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
import redis
from loader import dp, redis_db
from keyboards import get_main_keyboard
from test import fetch_products


class UserStates(StatesGroup):
    START = State()
    ECHO = State()


@dp.message_handler(commands="start", state='*')
async def cmd_start(message: types.Message):
    await UserStates.START.set()
    r = redis_db
    keys = await r._redis.keys('*')
    values = await r._redis.mget(*keys)
    print(keys)
    print(values)
    products = await fetch_products()
    print(products)
    buttons = []
    for product in products:
        buttons.append({'text': product['attributes']['name'], 'callback_data': product['id']})

    await message.answer("Привет! Напиши мне что-нибудь и я отвечу тем же.", reply_markup=get_main_keyboard(buttons))
    await UserStates.ECHO.set()


@dp.message_handler(content_types=types.ContentTypes.TEXT, state=UserStates.ECHO)
async def echo(message: types.Message):
    user_id = str(message.from_user.id)
    print(user_id)
    r = redis_db
    keys = await r._redis.keys('*')
    values = await r._redis.mget(*keys)
    print(keys)
    print(values)
    await UserStates.ECHO.set()
    await message.answer(message.text)
