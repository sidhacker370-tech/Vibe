import json
import logging
from typing import Optional, Any
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.redis_client = None
        self._local_cache = {}  # Fallback for Windows local development without Docker
        self._local_ttl = {}

    async def connect(self):
        if settings.REDIS_URL:
            try:
                self.redis_client = await redis.from_url(settings.REDIS_URL, decode_responses=True)
                await self.redis_client.ping()
                logger.info("Connected to Redis cache.")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis at {settings.REDIS_URL}: {e}")
                self.redis_client = None
                logger.info("Using local in-memory fallback cache.")
        else:
            logger.info("REDIS_URL not set. Using local in-memory fallback cache.")

    async def get(self, key: str) -> Optional[Any]:
        if self.redis_client:
            try:
                val = await self.redis_client.get(key)
                if val:
                    return json.loads(val)
            except Exception as e:
                logger.error(f"Redis GET error: {e}")
        else:
            # Local fallback logic
            import time
            if key in self._local_cache:
                expire_time = self._local_ttl.get(key)
                if expire_time and time.time() > expire_time:
                    del self._local_cache[key]
                    if key in self._local_ttl:
                        del self._local_ttl[key]
                    return None
                return self._local_cache[key]
        return None

    async def set(self, key: str, value: Any, ttl_seconds: int = 60):
        if self.redis_client:
            try:
                await self.redis_client.setex(key, ttl_seconds, json.dumps(value))
            except Exception as e:
                logger.error(f"Redis SETEX error: {e}")
        else:
            # Local fallback logic
            import time
            self._local_cache[key] = value
            self._local_ttl[key] = time.time() + ttl_seconds

    async def delete(self, key: str):
        if self.redis_client:
            try:
                await self.redis_client.delete(key)
            except Exception as e:
                logger.error(f"Redis DELETE error: {e}")
        else:
            # Local fallback logic
            if key in self._local_cache:
                del self._local_cache[key]
            if key in self._local_ttl:
                del self._local_ttl[key]

    async def delete_prefix(self, prefix: str):
        if self.redis_client:
            try:
                # Use SCAN for safe prefix deletion
                cursor = '0'
                while cursor != 0:
                    cursor, keys = await self.redis_client.scan(cursor=cursor, match=f"{prefix}*", count=100)
                    if keys:
                        await self.redis_client.delete(*keys)
            except Exception as e:
                logger.error(f"Redis DELETE PREFIX error: {e}")
        else:
            # Local fallback logic
            keys_to_delete = [k for k in self._local_cache if k.startswith(prefix)]
            for k in keys_to_delete:
                del self._local_cache[k]
                if k in self._local_ttl:
                    del self._local_ttl[k]

cache_service = CacheService()
