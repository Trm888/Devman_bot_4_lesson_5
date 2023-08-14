import re

from aiogram import types
from aiogram.dispatcher.filters import Filter


class EmailCheck(Filter):
    key = 'is_valid_email'
    pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

    async def check(self, msg: types.Message):
        return self.pattern.match(msg.text)
