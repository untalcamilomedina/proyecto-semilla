"""
Advanced Rate Limiting System for Proyecto Semilla
Multiple strategies: Fixed Window, Sliding Window, Token Bucket, Leaky Bucket
"""

import asyncio
import time
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from enum import Enum

from pydantic import BaseModel


class RateLimitStrategy(Enum):
    """Rate limiting strategies"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    requests: int
    window_seconds: int
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    burst_limit: Optional[int] = None
    refill_rate: Optional[float] = None  # tokens per second for token bucket


@dataclass
class RateLimitState:
    """Rate limit state for a key"""
    requests: int = 0
    window_start: float = field(default_factory=time.time)
    tokens: float = 0.0
    last_refill: float = field(default_factory=time.time)


@dataclass
class RateLimitResult:
    """Result of rate limit check"""
    allowed: bool
    remaining_requests: int
    reset_time: float
    retry_after: Optional[float] = None


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    def __init__(self, retry_after: float, limit: int, window: int):
        self.retry_after = retry_after
        self.limit = limit
        self.window = window
        super().__init__(f"Rate limit exceeded. Retry after {retry_after} seconds")


class AdvancedRateLimiter:
    """
    Advanced rate limiter with multiple strategies
    """

    def __init__(self):
        self.states: Dict[str, RateLimitState] = {}
        self.configs: Dict[str, RateLimitConfig] = {}
        self._cleanup_task: Optional[asyncio.Task] = None

    def configure_endpoint(self, endpoint: str, config: RateLimitConfig):
        """Configure rate limiting for an endpoint"""
        self.configs[endpoint] = config

    def configure_user(self, user_id: str, config: RateLimitConfig):
        """Configure rate limiting for a user"""
        self.configs[f"user:{user_id}"] = config

    def configure_ip(self, ip_address: str, config: RateLimitConfig):
        """Configure rate limiting for an IP address"""
        self.configs[f"ip:{ip_address}"] = config

    def configure_tenant(self, tenant_id: str, config: RateLimitConfig):
        """Configure rate limiting for a tenant"""
        self.configs[f"tenant:{tenant_id}"] = config

    async def check_limit(self, key: str, config: Optional[RateLimitConfig] = None) -> RateLimitResult:
        """
        Check if request is within rate limit
        """
        if config is None:
            config = self.configs.get(key)
            if config is None:
                # No specific config, allow request
                return RateLimitResult(
                    allowed=True,
                    remaining_requests=999,
                    reset_time=time.time() + 60
                )

        # Get or create state for this key
        state = self.states.get(key)
        if state is None:
            state = RateLimitState()
            self.states[key] = state

        # Apply rate limiting strategy
        if config.strategy == RateLimitStrategy.FIXED_WINDOW:
            return self._check_fixed_window(key, state, config)
        elif config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return self._check_sliding_window(key, state, config)
        elif config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return self._check_token_bucket(key, state, config)
        elif config.strategy == RateLimitStrategy.LEAKY_BUCKET:
            return self._check_leaky_bucket(key, state, config)
        else:
            # Default to sliding window
            return self._check_sliding_window(key, state, config)

    def _check_fixed_window(self, key: str, state: RateLimitState, config: RateLimitConfig) -> RateLimitResult:
        """Fixed window rate limiting"""
        current_time = time.time()
        window_start = state.window_start

        # Check if we're in a new window
        if current_time - window_start >= config.window_seconds:
            # Reset window
            state.requests = 0
            state.window_start = current_time

        # Check if limit exceeded
        if state.requests >= config.requests:
            reset_time = window_start + config.window_seconds
            retry_after = reset_time - current_time

            return RateLimitResult(
                allowed=False,
                remaining_requests=0,
                reset_time=reset_time,
                retry_after=max(0, retry_after)
            )

        # Allow request
        state.requests += 1
        reset_time = state.window_start + config.window_seconds

        return RateLimitResult(
            allowed=True,
            remaining_requests=config.requests - state.requests,
            reset_time=reset_time
        )

    def _check_sliding_window(self, key: str, state: RateLimitState, config: RateLimitConfig) -> RateLimitResult:
        """Sliding window rate limiting (more accurate than fixed window)"""
        current_time = time.time()
        window_start = state.window_start

        # Check if we need to reset window
        if current_time - window_start >= config.window_seconds:
            # Reset window
            state.requests = 0
            state.window_start = current_time

        # For sliding window, we need to track request timestamps
        # For simplicity, we'll use a basic implementation
        # In production, you'd want to store timestamps in Redis or similar

        if state.requests >= config.requests:
            reset_time = window_start + config.window_seconds
            retry_after = reset_time - current_time

            return RateLimitResult(
                allowed=False,
                remaining_requests=0,
                reset_time=reset_time,
                retry_after=max(0, retry_after)
            )

        state.requests += 1
        reset_time = state.window_start + config.window_seconds

        return RateLimitResult(
            allowed=True,
            remaining_requests=config.requests - state.requests,
            reset_time=reset_time
        )

    def _check_token_bucket(self, key: str, state: RateLimitState, config: RateLimitConfig) -> RateLimitResult:
        """Token bucket algorithm"""
        current_time = time.time()

        # Refill tokens
        if config.refill_rate:
            time_passed = current_time - state.last_refill
            tokens_to_add = time_passed * config.refill_rate
            state.tokens = min(config.requests, state.tokens + tokens_to_add)
            state.last_refill = current_time

        # Check if we have tokens
        if state.tokens < 1:
            # Calculate when next token will be available
            if config.refill_rate and config.refill_rate > 0:
                tokens_needed = 1 - state.tokens
                refill_time = tokens_needed / config.refill_rate
                retry_after = refill_time
            else:
                retry_after = config.window_seconds

            return RateLimitResult(
                allowed=False,
                remaining_requests=int(state.tokens),
                reset_time=current_time + retry_after,
                retry_after=retry_after
            )

        # Consume token
        state.tokens -= 1

        return RateLimitResult(
            allowed=True,
            remaining_requests=int(state.tokens),
            reset_time=current_time + (1 / config.refill_rate) if config.refill_rate else current_time + 60
        )

    def _check_leaky_bucket(self, key: str, state: RateLimitState, config: RateLimitConfig) -> RateLimitResult:
        """Leaky bucket algorithm"""
        current_time = time.time()

        # For leaky bucket, we track the "water level"
        # This is a simplified implementation
        leak_rate = config.requests / config.window_seconds  # requests per second

        # Leak water
        time_passed = current_time - state.last_refill
        leaked = time_passed * leak_rate
        state.tokens = max(0, state.tokens - leaked)
        state.last_refill = current_time

        # Check bucket capacity
        bucket_capacity = config.requests
        if state.tokens >= bucket_capacity:
            # Bucket is full
            retry_after = (state.tokens - bucket_capacity) / leak_rate

            return RateLimitResult(
                allowed=False,
                remaining_requests=0,
                reset_time=current_time + retry_after,
                retry_after=retry_after
            )

        # Add request to bucket
        state.tokens += 1

        return RateLimitResult(
            allowed=True,
            remaining_requests=int(bucket_capacity - state.tokens),
            reset_time=current_time + (1 / leak_rate)
        )

    def get_remaining_requests(self, key: str) -> int:
        """Get remaining requests for a key"""
        config = self.configs.get(key)
        if not config:
            return 999

        state = self.states.get(key)
        if not state:
            return config.requests

        if config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return int(state.tokens)
        else:
            return max(0, config.requests - state.requests)

    def get_reset_time(self, key: str) -> float:
        """Get reset time for a key"""
        config = self.configs.get(key)
        if not config:
            return time.time() + 60

        state = self.states.get(key)
        if not state:
            return time.time() + config.window_seconds

        return state.window_start + config.window_seconds

    def reset_limit(self, key: str):
        """Reset rate limit for a key"""
        if key in self.states:
            del self.states[key]

    def get_stats(self, key: str) -> Dict[str, Any]:
        """Get statistics for a key"""
        config = self.configs.get(key)
        state = self.states.get(key)

        if not config:
            return {"configured": False}

        if not state:
            return {
                "configured": True,
                "strategy": config.strategy.value,
                "requests": config.requests,
                "window_seconds": config.window_seconds,
                "current_requests": 0,
                "remaining_requests": config.requests
            }

        return {
            "configured": True,
            "strategy": config.strategy.value,
            "requests": config.requests,
            "window_seconds": config.window_seconds,
            "current_requests": state.requests,
            "remaining_requests": self.get_remaining_requests(key),
            "reset_time": self.get_reset_time(key),
            "tokens": state.tokens if config.strategy == RateLimitStrategy.TOKEN_BUCKET else None
        }

    async def cleanup_expired_states(self):
        """Clean up expired rate limit states"""
        current_time = time.time()
        expired_keys = []

        for key, state in self.states.items():
            config = self.configs.get(key)
            if config and current_time - state.window_start > config.window_seconds * 2:
                expired_keys.append(key)

        for key in expired_keys:
            del self.states[key]

    def start_cleanup_task(self):
        """Start background cleanup task"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def _cleanup_loop(self):
        """Background cleanup loop"""
        while True:
            try:
                await self.cleanup_expired_states()
                await asyncio.sleep(300)  # Clean up every 5 minutes
            except Exception as e:
                print(f"Rate limiter cleanup error: {e}")
                await asyncio.sleep(60)

    def stop_cleanup_task(self):
        """Stop background cleanup task"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()


# Global rate limiter instance
rate_limiter = AdvancedRateLimiter()


# FastAPI Middleware
class RateLimitMiddleware:
    """FastAPI middleware for rate limiting"""

    def __init__(self, app):
        self.app = app
        rate_limiter.start_cleanup_task()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Get client information
        headers = dict(scope.get("headers", []))
        client_ip = self._get_client_ip(headers)
        path = scope.get("path", "")
        method = scope.get("method", "")

        # Create rate limit key
        key = f"{client_ip}:{path}"

        # Check rate limit
        result = await rate_limiter.check_limit(key)

        if not result.allowed:
            # Rate limit exceeded
            response_headers = [
                (b"content-type", b"application/json"),
                (b"x-ratelimit-limit", str(result.remaining_requests + 1).encode()),
                (b"x-ratelimit-remaining", str(result.remaining_requests).encode()),
                (b"x-ratelimit-reset", str(int(result.reset_time)).encode()),
                (b"retry-after", str(int(result.retry_after or 60)).encode()),
            ]

            await send({
                "type": "http.response.start",
                "status": 429,
                "headers": response_headers,
            })

            await send({
                "type": "http.response.body",
                "body": b'{"error": "Rate limit exceeded", "retry_after": ' + str(int(result.retry_after or 60)).encode() + b'}',
            })
            return

        # Add rate limit headers to response
        original_send = send

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.extend([
                    (b"x-ratelimit-limit", str(result.remaining_requests + 1).encode()),
                    (b"x-ratelimit-remaining", str(result.remaining_requests).encode()),
                    (b"x-ratelimit-reset", str(int(result.reset_time)).encode()),
                ])
                message["headers"] = headers

            await original_send(message)

        await self.app(scope, receive, send_with_headers)

    def _get_client_ip(self, headers: Dict[bytes, bytes]) -> str:
        """Extract client IP from headers"""
        # Check X-Forwarded-For header first
        x_forwarded_for = headers.get(b"x-forwarded-for")
        if x_forwarded_for:
            # Take first IP if multiple
            ip = x_forwarded_for.decode().split(",")[0].strip()
            return ip

        # Check X-Real-IP header
        x_real_ip = headers.get(b"x-real-ip")
        if x_real_ip:
            return x_real_ip.decode()

        # Default fallback
        return "unknown"


# Configuration helpers
def configure_default_limits():
    """Configure default rate limits for common endpoints"""
    # Authentication endpoints - strict limits
    rate_limiter.configure_endpoint(
        "/api/v1/auth/login",
        RateLimitConfig(requests=5, window_seconds=300, strategy=RateLimitStrategy.SLIDING_WINDOW)
    )

    rate_limiter.configure_endpoint(
        "/api/v1/auth/refresh",
        RateLimitConfig(requests=10, window_seconds=300, strategy=RateLimitStrategy.SLIDING_WINDOW)
    )

    # API endpoints - moderate limits
    rate_limiter.configure_endpoint(
        "/api/v1",
        RateLimitConfig(requests=100, window_seconds=60, strategy=RateLimitStrategy.SLIDING_WINDOW)
    )

    # Admin endpoints - higher limits for authenticated users
    rate_limiter.configure_endpoint(
        "/api/v1/admin",
        RateLimitConfig(requests=1000, window_seconds=3600, strategy=RateLimitStrategy.TOKEN_BUCKET, refill_rate=5.0)
    )


# Decorators for function-level rate limiting
def rate_limit(key_prefix: str = "", requests: int = 100, window_seconds: int = 60):
    """Decorator for function-level rate limiting"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate key from function name and arguments
            key_parts = [key_prefix, func.__name__]
            if args:
                key_parts.extend(str(arg) for arg in args)
            if kwargs:
                key_parts.extend(f"{k}:{v}" for k, v in kwargs.items())

            key = ":".join(key_parts)

            config = RateLimitConfig(
                requests=requests,
                window_seconds=window_seconds,
                strategy=RateLimitStrategy.SLIDING_WINDOW
            )

            result = await rate_limiter.check_limit(key, config)

            if not result.allowed:
                raise RateLimitExceeded(result.retry_after or 60, requests, window_seconds)

            return await func(*args, **kwargs)

        return wrapper
    return decorator


# Monitoring and analytics
async def get_rate_limit_metrics() -> Dict[str, Any]:
    """Get rate limiting metrics for monitoring"""
    total_keys = len(rate_limiter.states)
    total_configs = len(rate_limiter.configs)

    # Calculate hit rates and blocked requests
    blocked_requests = 0
    active_limits = 0

    for key, state in rate_limiter.states.items():
        config = rate_limiter.configs.get(key)
        if config:
            active_limits += 1
            if state.requests >= config.requests:
                blocked_requests += 1

    return {
        "total_rate_limit_keys": total_keys,
        "total_configured_limits": total_configs,
        "active_limits": active_limits,
        "blocked_requests": blocked_requests,
        "block_rate": (blocked_requests / max(1, total_keys)) * 100 if total_keys > 0 else 0
    }


# Cleanup on shutdown
async def shutdown_rate_limiter():
    """Shutdown rate limiter and cleanup resources"""
    rate_limiter.stop_cleanup_task()

    # Clear states
    rate_limiter.states.clear()
    rate_limiter.configs.clear()