from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from typing import Optional, Dict, List, Tuple
import time
import logging
from datetime import datetime
import asyncio
from redis.asyncio import Redis

from .error_handler import RateLimitError
from ...config import Settings, get_settings

logger = logging.getLogger(__name__)

class RateLimitManager:
    """Manages rate limiting using Redis"""

    def __init__(self, redis: Redis, prefix: str = "ratelimit:"):
        self.redis = redis
        self.prefix = prefix

    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int
    ) -> Tuple[bool, Dict]:
        """
        Check if request is within rate limit
        Returns: (is_allowed, limit_info)
        """
        redis_key = f"{self.prefix}{key}"
        current_time = int(time.time())
        window_start = current_time - window

        async with self.redis.pipeline(transaction=True) as pipe:
            try:
                # Clean old requests
                await pipe.zremrangebyscore(redis_key, 0, window_start)
                # Count requests in window
                await pipe.zcard(redis_key)
                # Add current request
                await pipe.zadd(redis_key, {str(current_time): current_time})
                # Set expiry
                await pipe.expire(redis_key, window)
                
                _, request_count, _, _ = await pipe.execute()

                is_allowed = request_count <= limit
                
                return is_allowed, {
                    "limit": limit,
                    "remaining": max(0, limit - request_count),
                    "reset": window_start + window,
                    "window": window
                }

            except Exception as e:
                logger.error(f"Rate limit check error: {str(e)}")
                # On error, allow request but log issue
                return True, {
                    "limit": limit,
                    "remaining": 1,
                    "reset": window_start + window,
                    "window": window
                }

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""

    def __init__(
        self,
        app,
        redis_url: Optional[str] = None,
        limit: int = 60,
        window: int = 60,
        exempted_paths: Optional[List[str]] = None
    ):
        super().__init__(app)
        self.settings = get_settings()
        self.redis_url = redis_url or self.settings.REDIS_URL
        self.limit = limit
        self.window = window
        self.exempted_paths = set(exempted_paths or [])
        self.rate_limit_manager = None
        self._setup_task = None

    async def setup(self):
        """Initialize rate limit manager"""
        try:
            redis = Redis.from_url(self.redis_url, decode_responses=True)
            await redis.ping()
            self.rate_limit_manager = RateLimitManager(redis)
            logger.info("Rate limit manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize rate limit manager: {str(e)}")
            self.rate_limit_manager = None

    def get_limit_key(self, request: Request) -> str:
        """Generate rate limit key based on request"""
        # Get client IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        # Get authenticated user if available
        user_id = getattr(request.state, "user_id", None)
        
        if user_id:
            # Use user ID for authenticated requests
            return f"user:{user_id}"
        else:
            # Use IP for unauthenticated requests
            return f"ip:{client_ip}"

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        """Handle rate limiting for requests"""
        # Initialize rate limit manager if needed
        if not self.rate_limit_manager and not self._setup_task:
            self._setup_task = asyncio.create_task(self.setup())
            await self._setup_task

        # Check if path is exempted
        if request.url.path in self.exempted_paths:
            return await call_next(request)

        # Skip rate limiting if manager isn't available
        if not self.rate_limit_manager:
            logger.warning("Rate limit manager not available, skipping check")
            return await call_next(request)

        try:
            # Get rate limit key
            limit_key = self.get_limit_key(request)
            
            # Check rate limit
            is_allowed, limit_info = await self.rate_limit_manager.check_rate_limit(
                limit_key,
                self.limit,
                self.window
            )

            # Add rate limit headers
            headers = {
                "X-RateLimit-Limit": str(limit_info["limit"]),
                "X-RateLimit-Remaining": str(limit_info["remaining"]),
                "X-RateLimit-Reset": str(limit_info["reset"]),
                "X-RateLimit-Window": str(limit_info["window"])
            }

            if not is_allowed:
                raise RateLimitError(
                    details={
                        "retry_after": limit_info["reset"] - int(time.time())
                    }
                )

            # Process request
            response = await call_next(request)
            
            # Add rate limit headers to response
            for header, value in headers.items():
                response.headers[header] = value

            return response

        except RateLimitError:
            raise
        except Exception as e:
            logger.error(f"Rate limit middleware error: {str(e)}")
            # On error, allow request but log issue
            return await call_next(request)

    async def close(self):
        """Cleanup resources"""
        if self.rate_limit_manager and self.rate_limit_manager.redis:
            await self.rate_limit_manager.redis.close()

class RateLimitConfig:
    """Rate limit configuration for different endpoints"""
    
    DEFAULT = {
        "limit": 60,
        "window": 60
    }
    
    AUTH = {
        "limit": 5,
        "window": 60
    }
    
    API = {
        "limit": 30,
        "window": 60
    }
    
    SCENARIOS = {
        "limit": 10,
        "window": 60
    }

    @classmethod
    def get_config(cls, endpoint_type: str) -> Dict:
        """Get rate limit config for endpoint type"""
        return getattr(cls, endpoint_type.upper(), cls.DEFAULT)

# Example usage in main.py:
"""
from app.api.middleware.rate_limit import RateLimitMiddleware, RateLimitConfig

# Add rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    limit=RateLimitConfig.API["limit"],
    window=RateLimitConfig.API["window"],
    exempted_paths=["/health", "/metrics"]
)
"""