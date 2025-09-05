"""
Redis Client for Proyecto Semilla WebSocket Collaboration
Handles pub/sub messaging for real-time features
"""

import redis.asyncio as redis
import json
import logging
from typing import Optional, Callable, Any
from app.core.config import settings


logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client for real-time collaboration features"""

    def __init__(self):
        self.redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379')
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.Redis] = None
        self.is_connected = False

    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.Redis.from_url(self.redis_url, decode_responses=True)
            self.pubsub = redis.Redis.from_url(self.redis_url, decode_responses=True)
            await self.redis_client.ping()
            self.is_connected = True
            logger.info("✅ Connected to Redis for collaboration")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            self.is_connected = False

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
        if self.pubsub:
            await self.pubsub.close()
        self.is_connected = False
        logger.info("🔌 Disconnected from Redis")

    async def publish(self, channel: str, message: dict):
        """Publish message to Redis channel"""
        if not self.is_connected or not self.redis_client:
            logger.warning("Redis not connected, skipping publish")
            return

        try:
            message_json = json.dumps(message)
            await self.redis_client.publish(channel, message_json)
            logger.debug(f"Published to {channel}: {message}")
        except Exception as e:
            logger.error(f"Error publishing to Redis: {e}")

    async def subscribe(self, channel: str, callback: Callable[[dict], Any]):
        """Subscribe to Redis channel"""
        if not self.is_connected or not self.pubsub:
            logger.warning("Redis not connected, skipping subscribe")
            return

        try:
            pubsub = self.pubsub.pubsub()
            await pubsub.subscribe(channel)

            logger.info(f"Subscribed to Redis channel: {channel}")

            async for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        await callback(data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON in Redis message: {e}")
                    except Exception as e:
                        logger.error(f"Error processing Redis message: {e}")

        except Exception as e:
            logger.error(f"Error subscribing to Redis channel {channel}: {e}")

    async def set_cache(self, key: str, value: Any, expire: Optional[int] = None):
        """Set cache value in Redis"""
        if not self.is_connected or not self.redis_client:
            return

        try:
            value_json = json.dumps(value)
            if expire:
                await self.redis_client.setex(key, expire, value_json)
            else:
                await self.redis_client.set(key, value_json)
        except Exception as e:
            logger.error(f"Error setting Redis cache: {e}")

    async def get_cache(self, key: str) -> Optional[Any]:
        """Get cache value from Redis"""
        if not self.is_connected or not self.redis_client:
            return None

        try:
            value_json = await self.redis_client.get(key)
            if value_json:
                return json.loads(value_json)
            return None
        except Exception as e:
            logger.error(f"Error getting Redis cache: {e}")
            return None

    async def delete_cache(self, key: str):
        """Delete cache value from Redis"""
        if not self.is_connected or not self.redis_client:
            return

        try:
            await self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Error deleting Redis cache: {e}")

    async def get_room_participants(self, room_id: str) -> list:
        """Get active participants for a room from Redis"""
        cache_key = f"room:{room_id}:participants"
        participants = await self.get_cache(cache_key)
        return participants or []

    async def add_room_participant(self, room_id: str, user_id: str, user_data: dict):
        """Add participant to room in Redis"""
        cache_key = f"room:{room_id}:participants"
        participants = await self.get_room_participants(room_id)

        # Remove existing user if present
        participants = [p for p in participants if p.get('user_id') != user_id]

        # Add user
        participants.append({
            'user_id': user_id,
            **user_data
        })

        # Cache for 1 hour
        await self.set_cache(cache_key, participants, 3600)

    async def remove_room_participant(self, room_id: str, user_id: str):
        """Remove participant from room in Redis"""
        cache_key = f"room:{room_id}:participants"
        participants = await self.get_room_participants(room_id)

        # Remove user
        participants = [p for p in participants if p.get('user_id') != user_id]

        # Update cache
        if participants:
            await self.set_cache(cache_key, participants, 3600)
        else:
            await self.delete_cache(cache_key)

    async def get_user_cursor(self, room_id: str, user_id: str) -> Optional[dict]:
        """Get user cursor position from Redis"""
        cache_key = f"room:{room_id}:cursor:{user_id}"
        return await self.get_cache(cache_key)

    async def set_user_cursor(self, room_id: str, user_id: str, cursor_data: dict):
        """Set user cursor position in Redis"""
        cache_key = f"room:{room_id}:cursor:{user_id}"
        # Cache for 5 minutes
        await self.set_cache(cache_key, cursor_data, 300)

    async def get_room_cursors(self, room_id: str) -> list:
        """Get all active cursors for a room"""
        # This would need to be implemented with Redis sets or keys pattern
        # For now, return empty list
        return []


# Global Redis client instance
redis_client = RedisClient()


async def get_redis_client() -> RedisClient:
    """Dependency injection for Redis client"""
    if not redis_client.is_connected:
        await redis_client.connect()
    return redis_client