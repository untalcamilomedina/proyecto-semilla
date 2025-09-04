"""
Middleware for Proyecto Semilla
Tenant context, authentication, and security middleware
"""

from typing import Callable
import redis
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from jose import jwt, JWTError

from app.core.config import settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.user import User

logger = get_logger(__name__)

# Redis client for rate limiting (lazy initialization)
redis_client = None

def get_redis_client():
    """Get Redis client with lazy initialization"""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.from_url(settings.REDIS_URL)
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            redis_client = None
    return redis_client


async def tenant_context_middleware(request: Request, call_next):
    """
    Middleware to set tenant context for RLS
    Extracts tenant_id from JWT and sets it in database session
    """
    # Skip middleware for health checks and docs
    if request.url.path in ["/api/v1/health", "/api/v1/health/detailed", "/docs", "/redoc", "/openapi.json", "/api/v1/openapi.json"]:
        return await call_next(request)

    # Skip for auth endpoints that don't require tenant context
    if request.url.path.startswith("/api/v1/auth/login"):
        return await call_next(request)

    response = Response("Internal server error", status_code=500)

    try:
        # Extract token from Authorization header
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            # For endpoints that require auth but no token provided
            if request.url.path.startswith("/api/v1/") and not request.url.path.startswith("/api/v1/auth/login"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authorization header missing",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return await call_next(request)

        token = authorization.split(" ")[1]

        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )
            user_id = payload.get("sub")
            tenant_id = payload.get("tenant_id")

            if not user_id or not tenant_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Add tenant and user info to request state
            # The actual database verification will happen in the endpoint dependencies
            request.state.tenant_id = tenant_id
            request.state.user_id = user_id

        except JWTError as e:
            logger.warning(f"JWT validation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Continue with request
        response = await call_next(request)

    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        logger.error(
            "Middleware error",
            error=str(e),
            error_type=type(e).__name__,
            path=request.url.path,
            method=request.method
        )
        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )

    return response


async def rate_limiting_middleware(request: Request, call_next):
    """
    Redis-based rate limiting middleware
    """
    # Skip rate limiting for health checks
    if request.url.path in ["/health", "/api/v1/health", "/api/v1/health/detailed"]:
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"

    # Create rate limit key
    rate_limit_key = f"rate_limit:{client_ip}"

    # Get Redis client
    client = get_redis_client()
    if client is None:
        # If Redis is not available, skip rate limiting
        logger.debug("Redis not available, skipping rate limiting")
    else:
        try:
            # Use Redis pipeline for atomic operations
            pipe = client.pipeline()

            # Get current request count
            pipe.get(rate_limit_key)
            # Increment counter with expiration
            pipe.incr(rate_limit_key)
            pipe.expire(rate_limit_key, settings.RATE_LIMIT_WINDOW)

            # Execute pipeline
            results = pipe.execute()
            current_count = int(results[1])  # Result of INCR

            # Check if rate limit exceeded
            if current_count > settings.RATE_LIMIT_REQUESTS:
                logger.warning(
                    "Rate limit exceeded",
                    client_ip=client_ip,
                    path=request.url.path,
                    method=request.method,
                    current_count=current_count,
                    limit=settings.RATE_LIMIT_REQUESTS
                )

                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Too many requests",
                        "retry_after": settings.RATE_LIMIT_WINDOW
                    },
                    headers={"Retry-After": str(settings.RATE_LIMIT_WINDOW)}
                )

            # Log successful request
            logger.info(
                "Request processed",
                client_ip=client_ip,
                path=request.url.path,
                method=request.method,
                current_count=current_count,
                user_agent=request.headers.get("user-agent")
            )

        except redis.RedisError as e:
            # If Redis is down, allow request but log error
            logger.error(
                "Redis rate limiting error",
                error=str(e),
                client_ip=client_ip,
                path=request.url.path
            )

    # Continue with request
    response = await call_next(request)
    return response


async def logging_middleware(request: Request, call_next):
    """
    Structured logging middleware
    """
    import time

    start_time = time.time()

    # Log request
    logger.info(
        "Request started",
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "unknown")
    )

    try:
        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time
        logger.info(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time=f"{process_time:.3f}s"
        )

        return response

    except Exception as e:
        # Log error
        process_time = time.time() - start_time
        logger.error(
            "Request failed",
            method=request.method,
            path=request.url.path,
            error=str(e),
            error_type=type(e).__name__,
            process_time=f"{process_time:.3f}s"
        )
        raise