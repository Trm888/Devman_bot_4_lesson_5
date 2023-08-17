from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2


def get_redis_storage_for_state(host, port, redis_password):
    return RedisStorage2(host=host, port=port, password=redis_password)


def get_bot(bot_token):
    return Bot(bot_token, parse_mode=types.ParseMode.HTML)


def get_dispatcher(bot, host, port, redis_password):
    storage = get_redis_storage_for_state(host, port, redis_password)
    return Dispatcher(bot, storage=storage)
