from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2



def get_bot(bot_token):
    return Bot(bot_token, parse_mode=types.ParseMode.HTML)


def get_dispatcher(bot, host, port, redis_password):
    storage = RedisStorage2(host=host, port=port, password=redis_password)
    return Dispatcher(bot, storage=storage)
