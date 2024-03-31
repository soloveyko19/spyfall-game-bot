from config import conf

from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis


storage = RedisStorage.from_url(url=f"redis://{conf.REDIS_HOST}:6379/0")
storage_antispam = Redis.from_url(url=f"redis://{conf.REDIS_HOST}:6379/1")
storage_restrict = Redis.from_url(url=f"redis://{conf.REDIS_HOST}:6379/2")
