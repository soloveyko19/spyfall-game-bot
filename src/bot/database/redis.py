from config import conf

from aiogram.fsm.storage.redis import RedisStorage


storage = RedisStorage.from_url(url=f"redis://{conf.REDIS_HOST}:6379/0")
