import re
import time

import aioredis
from aiogram import types
from aiogram.dispatcher.filters import Filter

from elasticpath_api import get_access_token


class EmailCheck(Filter):
    key = 'is_valid_email'
    pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

    async def check(self, msg: types.Message):
        return self.pattern.match(msg.text)


async def get_redis_storage(host, port, redis_password):
    return await aioredis.from_url(f'redis://{host}:{port}', password=redis_password)


async def get_or_update_token(client_id, client_secret, host, port, redis_password):
    storage = await get_redis_storage(host, port, redis_password)
    current_token = await storage.get("token")
    expires = await storage.get("expires")

    if not current_token:
        current_token, expires = await get_access_token(client_id, client_secret)
        decode_expires = expires
        await storage.set("token", current_token)
        await storage.set("expires", decode_expires)
        return current_token
    else:
        now_time = time.time()
        expires = int(expires.decode("utf-8"))
        time_left = expires - now_time
        if time_left <= 0:
            current_token, expires = await get_access_token(client_id, client_secret)
            await storage.set("token", current_token)
            await storage.set("expires", expires)
            return current_token
        else:
            return current_token.decode("utf-8")
