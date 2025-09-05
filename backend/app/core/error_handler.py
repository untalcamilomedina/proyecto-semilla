"""
Global Error Handler for Proyecto Semilla
Comprehensive error handling with fallback systems and graceful degradation
"""

from typing import Dict, Any, Optional
import logging
import traceback
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import time

logger = logging.getLogger(__name__)

class ErrorHandler:
    """
    Global error handler with fallback systems and graceful degradation
    """

    def __init__(self):
        self.fallback_responses = {
            "database_error": {
                "message": "Database temporarily unavailable",
                "fallback_data": {"status": "degraded"},
                "retry_after": 30
            },
            "cache_error": {
                "message": "Cache temporarily unavailable",
                "fallback_data": {"cached": False},
                "retry_after": 10
            },
            "external_api_error": {
                "message": "External service temporarily unavailable",
                "fallback_data": {"data": []},
                "retry_after": 60
            },
            "circuit_breaker_error": {
                "message": "Service temporarily overloaded",
                "fallback_data": {"status": "rate_limited"},
                "retry_after": 30
            }
        }

        # Error tracking
        self.error_counts: Dict[str, int] = {}
        self.last_errors: Dict[str, float] = {}

    async def handle_error(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle errors with appropriate fallback responses"""

        # Log the error with full context
        error_id = f"{int(time.time())}_{hash(str(exc))}"
        logger.error(f"Error ID {error_id}: {exc}")
        logger.error(f"Request: {request.method} {request.url}")
        logger.error(traceback.format_exc())

        # Track error frequency
        error_type = type(exc).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        self.last_errors[error_type] = time.time()

        # Determine error type and provide fallback
        if isinstance(exc, ConnectionError):
            return await self._handle_connection_error(request, exc, error_id)
        elif isinstance(exc, TimeoutError):
            return await self._handle_timeout_error(request, exc, error_id)
        elif isinstance(exc, HTTPException):
            return await self._handle_http_error(request, exc, error_id)
        elif "database" in str(exc).lower() or "psycopg" in str(exc).lower():
            return await self._handle_database_error(request, exc, error_id)
        elif "cache" in str(exc).lower() or "redis" in str(exc).lower():
            return await self._handle_cache_error(request, exc, error_id)
        elif "circuit" in str(exc).lower():
            return await self._handle_circuit_breaker_error(request, exc, error_id)
        else:
            return await self._handle_generic_error(request, exc, error_id)

    async def _handle_connection_error(self, request: Request, exc: Exception, error_id: str) -> JSONResponse:
        """Handle connection errors with retry logic"""
        return JSONResponse(
            status_code=503,
            content={
                "error": "Service temporarily unavailable",
                "message": "Connection failed, please retry",
                "retry_after": 30,
                "error_id": error_id,
                "request_id": getattr(request.state, 'request_id', None)
            },
            headers={"Retry-After": "30"}
        )

    async def _handle_timeout_error(self, request: Request, exc: Exception, error_id: str) -> JSONResponse:
        """Handle timeout errors"""
        return JSONResponse(
            status_code=504,
            content={
                "error": "Gateway timeout",
                "message": "Request timed out, please try again",
                "retry_after": 10,
                "error_id": error_id,
                "request_id": getattr(request.state, 'request_id', None)
            },
            headers={"Retry-After": "10"}
        )

    async def _handle_http_error(self, request: Request, exc: HTTPException, error_id: str) -> JSONResponse:
        """Handle HTTP exceptions"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "error_id": error_id,
                "request_id": getattr(request.state, 'request_id', None)
            }
        )

    async def _handle_database_error(self, request: Request, exc: Exception, error_id: str) -> JSONResponse:
        """Handle database errors with fallback data"""
        fallback = self.fallback_responses["database_error"]

        # Try to provide cached or default data
        fallback_data = await self._get_fallback_data(request, "database")

        return JSONResponse(
            status_code=503,
            content={
                **fallback,
                "fallback_data": fallback_data,
                "error_id": error_id,
                "request_id": getattr(request.state, 'request_id', None)
            },
            headers={"Retry-After": str(fallback["retry_after"])}
        )

    async def _handle_cache_error(self, request: Request, exc: Exception, error_id: str) -> JSONResponse:
        """Handle cache errors"""
        fallback = self.fallback_responses["cache_error"]

        return JSONResponse(
            status_code=503,
            content={
                **fallback,
                "error_id": error_id,
                "request_id": getattr(request.state, 'request_id', None)
            },
            headers={"Retry-After": str(fallback["retry_after"])}
        )

    async def _handle_circuit_breaker_error(self, request: Request, exc: Exception, error_id: str) -> JSONResponse:
        """Handle circuit breaker errors"""
        fallback = self.fallback_responses["circuit_breaker_error"]

        return JSONResponse(
            status_code=503,
            content={
                **fallback,
                "error_id": error_id,
                "request_id": getattr(request.state, 'request_id', None)
            },
            headers={"Retry-After": str(fallback["retry_after"])}
        )

    async def _handle_generic_error(self, request: Request, exc: Exception, error_id: str) -> JSONResponse:
        """Handle generic errors"""
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "error_id": error_id,
                "request_id": getattr(request.state, 'request_id', None)
            }
        )

    async def _get_fallback_data(self, request: Request, error_type: str) -> Any:
        """Get fallback data for degraded operations"""
        try:
            # Try to get cached data or provide sensible defaults
            if "articles" in str(request.url):
                return await self._get_articles_fallback()
            elif "users" in str(request.url):
                return await self._get_users_fallback()
            elif "categories" in str(request.url):
                return await self._get_categories_fallback()
            else:
                return {"status": "degraded_mode"}
        except Exception as e:
            logger.error(f"Error getting fallback data: {e}")
            return {"status": "degraded_mode"}

    async def _get_articles_fallback(self) -> Dict[str, Any]:
        """Get fallback data for articles"""
        # In a real implementation, this would fetch from cache
        return {
            "articles": [
                {
                    "id": "fallback-1",
                    "title": "Service Temporarily Unavailable",
                    "content": "Please try again in a few moments.",
                    "status": "published",
                    "created_at": "2024-01-01T00:00:00Z"
                }
            ],
            "total": 1,
            "status": "degraded"
        }

    async def _get_users_fallback(self) -> Dict[str, Any]:
        """Get fallback data for users"""
        return {
            "users": [],
            "total": 0,
            "status": "degraded"
        }

    async def _get_categories_fallback(self) -> Dict[str, Any]:
        """Get fallback data for categories"""
        return {
            "categories": [
                {
                    "id": "fallback-1",
                    "name": "General",
                    "slug": "general",
                    "description": "General category"
                }
            ],
            "total": 1,
            "status": "degraded"
        }

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring"""
        return {
            "error_counts": self.error_counts.copy(),
            "last_errors": self.last_errors.copy(),
            "total_errors": sum(self.error_counts.values()),
            "most_common_error": max(self.error_counts.items(), key=lambda x: x[1]) if self.error_counts else None
        }

    def reset_error_counts(self):
        """Reset error counts (useful for testing)"""
        self.error_counts.clear()
        self.last_errors.clear()


# Global error handler instance
error_handler = ErrorHandler()

# FastAPI exception handlers
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    return await error_handler.handle_error(request, exc)

async def generic_exception_handler(request: Request, exc: Exception):
    """Handle generic exceptions"""
    return await error_handler.handle_error(request, exc)

async def circuit_breaker_exception_handler(request: Request, exc: Exception):
    """Handle circuit breaker exceptions"""
    from app.core.circuit_breaker import CircuitBreakerOpenException
    if isinstance(exc, CircuitBreakerOpenException):
        return await error_handler.handle_error(request, exc)
    else:
        return await generic_exception_handler(request, exc)