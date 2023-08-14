import sys

from aiogram import types
from aiogram.utils import executor
from loguru import logger

from handlers import dp

logger.add('debug.log',
           format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}',
           level='INFO',
           rotation="1 MB",
           compression='zip',
           retention="2 days")
# logger.add(sys.stdout,
#            format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}',
#            level='INFO')


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand('start', 'Запустить бота'),
        ]
    )



async def on_startup(dp):
    await set_default_commands(dp)


if __name__ == '__main__':
    logger.info("Бот был запущен")
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
