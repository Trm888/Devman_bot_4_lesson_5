from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
# from environs import Env


def get_bot(bot_token):
    return Bot(bot_token, parse_mode=types.ParseMode.HTML)

def get_dispatcher(bot, host, port, redis_password):
    storage = RedisStorage2(host=host, port=port, password=redis_password)
    return Dispatcher(bot, storage=storage)


# env = Env()
# env.read_env()
# bot_token = env.str('TG_TOKEN')
# host = env.str('REDIS_HOST')
# port = env.int('REDIS_PORT')
# redis_password = env.str('REDIS_PASSWORD')
# redis_db = RedisStorage2(host=host, port=port, password=redis_password)
# bot = Bot(bot_token, parse_mode=types.ParseMode.HTML)
#
# storage = redis_db
# dp = Dispatcher(bot, storage=redis_db)
