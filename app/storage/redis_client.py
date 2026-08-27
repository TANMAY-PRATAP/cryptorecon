"""Redis Client for Ingestion Queues and Traversal Caching."""

import json
import logging
from typing import Optional, Dict, Any, List
from app.config import get_settings

logger = logging.getLogger(__name__)

try:
    from redis import asyncio as aioredis  # type: ignore
except ImportError:
    aioredis = None  # type: ignore


class RedisManager:
    """Manages async Redis connection with graceful in-memory fallback."""

    def __init__(self, redis_url: Optional[str] = None):
        self.settings = get_settings()
        self.redis_url = redis_url or self.settings.REDIS_URL
        self._client: Optional[Any] = None
        self._is_connected = False
        self._fallback_queue: List[str] = []
        self._fallback_cache: Dict[str, str] = {}

    async def connect(self) -> bool:
        """Establish async Redis connection if library and server are available."""
        if not self.settings.REDIS_ENABLED or aioredis is None:
            logger.info("Redis is disabled or redis package not installed; using in-memory queue fallback.")
            self._is_connected = False
            return False

        try:
            self._client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=self.settings.REDIS_TIMEOUT_SECONDS
            )
            await self._client.ping()
            self._is_connected = True
            logger.info("Connected to Redis successfully.")
            return True
        except Exception as e:
            logger.warning(f"Redis connection failed ({e}); falling back to in-memory queue.")
            self._is_connected = False
            return False

    async def disconnect(self) -> None:
        """Close connection cleanly."""
        if self._client and self._is_connected:
            await self._client.close()
            self._is_connected = False

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    async def enqueue_case(self, queue_name: str, payload: Dict[str, Any]) -> str:
        """Push a case ingestion payload into the traversal queue."""
        data_str = json.dumps(payload, default=str)
        if self._is_connected and self._client:
            try:
                await self._client.rpush(queue_name, data_str)
                return f"redis_queued_{payload.get('complaint_id')}"
            except Exception as e:
                logger.error(f"Redis enqueue error ({e}), falling back to memory queue.")
        
        self._fallback_queue.append(data_str)
        return f"mem_queued_{payload.get('complaint_id')}"

    async def dequeue_case(self, queue_name: str) -> Optional[Dict[str, Any]]:
        """Pop next case payload from queue."""
        if self._is_connected and self._client:
            try:
                item = await self._client.lpop(queue_name)
                if item:
                    return json.loads(item)
            except Exception as e:
                logger.error(f"Redis dequeue error ({e}), falling back to memory queue.")

        if self._fallback_queue:
            return json.loads(self._fallback_queue.pop(0))
        return None

    async def set_cache(self, key: str, value: Any, expire_seconds: int = 3600) -> bool:
        """Cache key-value pair."""
        val_str = json.dumps(value, default=str)
        if self._is_connected and self._client:
            try:
                await self._client.set(key, val_str, ex=expire_seconds)
                return True
            except Exception as e:
                logger.error(f"Redis set error ({e})")
        self._fallback_cache[key] = val_str
        return True

    async def get_cache(self, key: str) -> Optional[Any]:
        """Retrieve key from cache."""
        if self._is_connected and self._client:
            try:
                val = await self._client.get(key)
                if val:
                    return json.loads(val)
            except Exception as e:
                logger.error(f"Redis get error ({e})")
        val = self._fallback_cache.get(key)
        return json.loads(val) if val else None


_redis_manager: Optional[RedisManager] = None


def get_redis_manager() -> RedisManager:
    global _redis_manager
    if _redis_manager is None:
        _redis_manager = RedisManager()
    return _redis_manager
