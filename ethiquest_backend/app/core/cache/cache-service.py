import asyncio
from typing import Optional, Dict, Any
import hashlib
import json
import redis.asyncio as redis
from datetime import timedelta

class CacheService:
    """Handles caching of AI responses and game states"""
    
    def __init__(
        self,
        redis_url: str,
        default_ttl: int = 3600,  # 1 hour default
        prefix: str = "ethiquest:"
    ):
        self.redis = redis.from_url(redis_url)
        self.default_ttl = default_ttl
        self.prefix = prefix

    async def get_scenario(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Get cached scenario for prompt"""
        key = self._generate_key("scenario", prompt)
        cached = await self.redis.get(key)
        
        if cached:
            try:
                return json.loads(cached)
            except json.JSONDecodeError:
                await self.redis.delete(key)
                return None
        return None

    async def store_scenario(
        self,
        prompt: str,
        response: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> None:
        """Store scenario in cache"""
        key = self._generate_key("scenario", prompt)
        ttl = ttl or self.default_ttl
        
        try:
            await self.redis.setex(
                key,
                ttl,
                json.dumps(response)
            )
        except Exception as e:
            print(f"Cache storage error: {str(e)}")

    async def get_player_state(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Get cached player state"""
        key = self._generate_key("player", player_id)
        cached = await self.redis.get(key)
        
        if cached:
            try:
                return json.loads(cached)
            except json.JSONDecodeError:
                await self.redis.delete(key)
                return None
        return None

    async def store_player_state(
        self,
        player_id: str,
        state: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> None:
        """Store player state in cache"""
        key = self._generate_key("player", player_id)
        ttl = ttl or self.default_ttl * 24  # Longer TTL for player states
        
        try:
            await self.redis.setex(
                key,
                ttl,
                json.dumps(state)
            )
        except Exception as e:
            print(f"Cache storage error: {str(e)}")

    async def invalidate_scenario(self, prompt: str) -> None:
        """Invalidate cached scenario"""
        key = self._generate_key("scenario", prompt)
        await self.redis.delete(key)

    async def invalidate_player_state(self, player_id: str) -> None:
        """Invalidate cached player state"""
        key = self._generate_key("player", player_id)
        await self.redis.delete(key)

    def _generate_key(self, type_: str, identifier: str) -> str:
        """Generate cache key"""
        hash_value = hashlib.sha256(identifier.encode()).hexdigest()[:12]
        return f"{self.prefix}{type_}:{hash_value}"

    async def close(self):
        """Close Redis connection"""
        await self.redis.close()

    async def cleanup_expired(self):
        """Cleanup expired cache entries"""
        try:
            pattern = f"{self.prefix}*"
            cursor = 0
            while True:
                cursor, keys = await self.redis.scan(
                    cursor=cursor,
                    match=pattern,
                    count=100
                )
                for key in keys:
                    if not await self.redis.ttl(key):
                        await self.redis.delete(key)
                if cursor == 0:
                    break
        except Exception as e:
            print(f"Cache cleanup error: {str(e)}")

    async def start_cleanup_task(self, interval: int = 3600):
        """Start periodic cleanup task"""
        while True:
            await self.cleanup_expired()
            await asyncio.sleep(interval)

# Example usage:
async def main():
    cache = CacheService(
        redis_url="redis://localhost:6379/0",
        default_ttl=3600,
        prefix="ethiquest:"
    )
    
    # Store scenario
    await cache.store_scenario(
        "sample_prompt",
        {"title": "Test Scenario", "description": "Test Description"}
    )
    
    # Retrieve scenario
    scenario = await cache.get_scenario("sample_prompt")
    print(f"Retrieved scenario: {scenario}")
    
    # Cleanup
    await cache.close()

if __name__ == "__main__":
    asyncio.run(main())