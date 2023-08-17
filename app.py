from aiogram import types
from aiogram.utils import executor
from environs import Env
from loguru import logger

import handlers
from loader import get_bot, get_dispatcher

logger.add('debug.log',
           format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}',
           level='INFO',
           rotation="1 MB",
           compression='zip',
           retention="2 days")


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand('start', 'Запустить бота'),
        ]
    )


async def on_startup(dp):
    await set_default_commands(dp)


if __name__ == '__main__':
    env = Env()
    env.read_env()
    bot_token = env.str('TG_TOKEN')
    host = env.str('REDIS_HOST')
    port = env.int('REDIS_PORT')
    redis_password = env.str('REDIS_PASSWORD')
    client_secret = env.str("ELASTICPATH_CLIENT_SECRET")
    client_id = env.str("ELASTICPATH_CLIENT_ID")
    bot = get_bot(bot_token)
    dp = get_dispatcher(bot, host, port, redis_password)
    handlers.register_handlers(dp, client_id, client_secret, host, port, redis_password)
    logger.info("Бот был запущен")
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
