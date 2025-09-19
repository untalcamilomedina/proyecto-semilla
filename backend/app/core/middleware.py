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
from app.core.cookies import get_cookie_manager
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


async def cors_middleware(request: Request, call_next):
    """
    CORS middleware to handle preflight requests and add CORS headers to all responses
    """
    # Handle preflight OPTIONS requests
    if request.method == "OPTIONS":
        from app.core.config import settings
        cors_headers = {}

        if settings.BACKEND_CORS_ORIGINS:
            request_origin = request.headers.get("origin")
            allowed_origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]

            if request_origin and request_origin in allowed_origins:
                cors_origin = request_origin
            elif allowed_origins:
                cors_origin = allowed_origins[0]
            else:
                cors_origin = None

            if cors_origin:
                cors_headers.update({
                    "Access-Control-Allow-Origin": cors_origin,
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Authorization, Content-Type, X-Requested-With",
                    "Access-Control-Max-Age": "86400",  # 24 hours
                    "Vary": "Origin"
                })

        return Response(status_code=200, headers=cors_headers)

    # Continue with request
    response = await call_next(request)

    # Add CORS headers to all responses
    from app.core.config import settings
    if settings.BACKEND_CORS_ORIGINS:
        request_origin = request.headers.get("origin")
        allowed_origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]

        if request_origin and request_origin in allowed_origins:
            cors_origin = request_origin
        elif allowed_origins:
            cors_origin = allowed_origins[0]
        else:
            cors_origin = None

        if cors_origin:
            response.headers.update({
                "Access-Control-Allow-Origin": cors_origin,
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Authorization, Content-Type, X-Requested-With",
                "Vary": "Origin"
            })

    return response


async def tenant_context_middleware(request: Request, call_next):
    """
    Middleware to set tenant context for RLS
    Extracts tenant_id from JWT and sets it in database session
    """
    # Skip middleware for health checks, docs, and OPTIONS requests
    if request.method == "OPTIONS" or request.url.path in ["/api/v1/health", "/api/v1/health/detailed", "/docs", "/redoc", "/openapi.json", "/api/v1/openapi.json", "/", "/health"]:
        return await call_next(request)

    # Skip for auth endpoints that don't require tenant context
    if (request.url.path.startswith("/api/v1/auth/login") or
        request.url.path.startswith("/api/v1/auth/register") or
        request.url.path.startswith("/api/v1/auth/refresh") or
        request.url.path.startswith("/api/v1/auth/logout") or
        request.url.path.startswith("/api/v1/auth/logout-all") or
        request.url.path.startswith("/api/v1/auth/setup-status")):
        return await call_next(request)

    response = Response("Internal server error", status_code=500)

    try:
        # Extract token from Authorization header first
        token = None
        authorization = request.headers.get("Authorization")

        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
        else:
            # Fallback to cookie-based authentication
            cookie_manager = get_cookie_manager()
            token = cookie_manager.get_access_token_from_cookie(request)

        if not token:
            # For endpoints that require auth but no token provided
            # Skip auth check for endpoints in exceptions
            requires_auth = (
                request.url.path.startswith("/api/v1/") and
                not request.url.path.startswith("/api/v1/auth/login") and
                not request.url.path.startswith("/api/v1/auth/register") and
                not request.url.path.startswith("/api/v1/auth/refresh") and
                not request.url.path.startswith("/api/v1/auth/logout") and
                not request.url.path.startswith("/api/v1/auth/logout-all") and
                not request.url.path.startswith("/api/v1/auth/setup-status")
            )
            if requires_auth:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return await call_next(request)

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
        # Handle HTTP exceptions properly
        response = JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail},
            headers=e.headers
        )
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