import asyncio

import aioredis
import aioredis.sentinel

from settings import config
from utils.var import redis_var

_redis = None
_sentinel_client = None


async def get_redis_sentinel():
    global _redis
    if _redis is None:
        try:
            redis = redis_var.get()
        except LookupError:
            if config.REDIS_SENTINELS:
                sentinel_client = aioredis.sentinel.Sentinel(config.REDIS_SENTINELS,
                                                             sentinel_kwargs={"password": config.REDIS_SENTINEL_PWD})
                redis: aioredis.Redis = sentinel_client.master_for("mymaster", password=config.REDIS_MASTER_PWD)
                await redis.execute_command("select", 1)
                # await redis.set("username", 3)
                info = await redis.get("username")
                print(info)
            elif config.REDIS_URL:
                loop = asyncio.get_event_loop()
                redis = aioredis.from_url(
                    config.REDIS_URL, minsize=5, maxsize=20, loop=loop)
            else:
                raise
        _redis = redis
    return _redis


if __name__ == "__main__":
    asyncio.run(get_redis_sentinel())
