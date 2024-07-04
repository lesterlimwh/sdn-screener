import json
import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv
import aioredis

class RedisUtil:
    def __init__(self):
        load_dotenv()
        redis_url = os.getenv('REDIS_URL')

        # Redis connection pool
        self.redis = aioredis.from_url(redis_url, encoding="utf-8")

    async def get(self, key: Any) -> Optional[Any]:
        # Check if the data is in cache
        cached_data = await self.redis.get(key)
        if cached_data:
            return cached_data

        return None

    async def get_dict(self, key: Any) -> Optional[Dict[Any, Any]]:
        try:
            data_json = await self.redis.get(key)
            if data_json:
                # Deserialize JSON string to dictionary
                return json.loads(data_json)
            return None
        except TypeError as err:
            print(f"Redis - Error decoding JSON when fetching: {err}")
            raise err

    async def set(self, key: Any, data: Any, ex=3600) -> None:
        await self.redis.set(key, data, ex)

    async def set_dict(self, key: Any, data: Dict, ex=3600) -> None:
        try:
            data_json = json.dumps(data)
            # Store JSON string in Redis
            await self.redis.set(key, data_json, ex)
        except TypeError as err:
            print(f"Redis - Error encoding JSON when setting: {err}")
            raise err

    async def clear_cache(self, key: Any) -> None:
        await self.redis.delete(key)
