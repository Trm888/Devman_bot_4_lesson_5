from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2




def get_dispatcher(bot, host, port, redis_password):
    storage = RedisStorage2(host=host, port=port, password=redis_password)
    return Dispatcher(bot, storage=storage)
