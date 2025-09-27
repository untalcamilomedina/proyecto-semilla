"""
Advanced Rate Limiting Middleware with ML Integration
FastAPI middleware that uses ML-powered rate limiting
"""

import json
from datetime import datetime
from typing import Callable, Optional
import logging

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.rate_limiter import rate_limiter
from app.core.logging import get_logger

logger = get_logger(__name__)


class AdvancedRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Advanced rate limiting middleware with ML integration
    Replaces basic rate limiting with intelligent analysis
    """

    def __init__(self, app, exclude_paths: Optional[list] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/api/v1/health",
            "/api/v1/health/detailed",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/openapi.json",
            "/"
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request through advanced rate limiting
        """
        # Skip rate limiting for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Skip for auth endpoints that don't require tenant context
        if self._is_auth_endpoint(request.url.path):
            return await call_next(request)

        try:
            # Extract request data for analysis
            request_data = await self._extract_request_data(request)

            # Get tenant ID from request state (set by tenant middleware)
            tenant_id = getattr(request.state, 'tenant_id', None)

            # Check rate limit
            rate_limit_result = await rate_limiter.check_rate_limit(request_data, tenant_id)

            # Log rate limiting decision
            await self._log_rate_limit_decision(request, rate_limit_result)

            if not rate_limit_result['allowed']:
                # Request is blocked
                return await self._create_blocked_response(request, rate_limit_result)

            # Request is allowed, proceed
            response = await call_next(request)

            # Track successful request
            await self._track_successful_request(request, response, rate_limit_result)

            return response

        except Exception as e:
            logger.error(
                "Rate limiting middleware error",
                error=str(e),
                error_type=type(e).__name__,
                path=request.url.path,
                method=request.method,
                client_ip=self._get_client_ip(request)
            )
            # On error, allow request to proceed
            return await call_next(request)

    def _is_auth_endpoint(self, path: str) -> bool:
        """Check if path is an authentication endpoint that shouldn't be rate limited"""
        auth_paths = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/api/v1/auth/logout",
            "/api/v1/auth/logout-all",
            "/api/v1/auth/setup-status"
        ]
        return any(path.startswith(auth_path) for auth_path in auth_paths)

    async def _extract_request_data(self, request: Request) -> dict:
        """Extract relevant data from request for rate limiting analysis"""
        # Get request body (limited size for performance)
        body = b""
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if len(body) > 1024:  # Limit to 1KB for analysis
                    body = body[:1024]
            except:
                body = b""

        # Extract headers
        headers = dict(request.headers)
        # Remove sensitive headers
        sensitive_headers = ['authorization', 'cookie', 'x-api-key']
        for header in sensitive_headers:
            headers.pop(header, None)

        return {
            'method': request.method,
            'path': request.url.path,
            'query_string': str(request.url.query),
            'user_agent': request.headers.get('user-agent', ''),
            'accept': request.headers.get('accept', ''),
            'content_type': request.headers.get('content-type', ''),
            'content_length': len(body),
            'ip_address': self._get_client_ip(request),
            'user_id': getattr(request.state, 'user_id', None),
            'timestamp': datetime.utcnow(),
            'headers': headers,
            'body_size': len(body)
        }

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        # Check X-Forwarded-For header first (for proxies/load balancers)
        x_forwarded_for = request.headers.get('x-forwarded-for')
        if x_forwarded_for:
            # Take first IP if multiple
            return x_forwarded_for.split(',')[0].strip()

        # Check X-Real-IP header
        x_real_ip = request.headers.get('x-real-ip')
        if x_real_ip:
            return x_real_ip

        # Fall back to direct client
        if hasattr(request, 'client') and request.client:
            return request.client.host or 'unknown'

        return 'unknown'

    async def _log_rate_limit_decision(self, request: Request, result: dict):
        """Log rate limiting decision for monitoring"""
        log_data = {
            'allowed': result['allowed'],
            'reason': result.get('reason', 'unknown'),
            'ip_address': result.get('ip_address', 'unknown'),
            'path': request.url.path,
            'method': request.method,
            'user_agent': request.headers.get('user-agent', ''),
            'timestamp': datetime.utcnow().isoformat()
        }

        if not result['allowed']:
            # Log blocked requests with more detail
            log_data.update({
                'confidence': result.get('confidence'),
                'anomaly_score': result.get('anomaly_score'),
                'limit_type': result.get('limit_type'),
                'retry_after': result.get('retry_after')
            })
            logger.warning("Request blocked by rate limiter", **log_data)
        else:
            # Log allowed requests at info level (sampled)
            logger.info("Request allowed by rate limiter", **log_data)

    async def _create_blocked_response(self, request: Request, result: dict) -> JSONResponse:
        """Create response for blocked requests"""
        status_code = status.HTTP_429_TOO_MANY_REQUESTS
        retry_after = result.get('retry_after', 60)

        response_data = {
            'detail': 'Too many requests',
            'reason': result.get('reason', 'rate_limit_exceeded'),
            'retry_after': retry_after,
            'timestamp': datetime.utcnow().isoformat()
        }

        # Add additional information for API consumers
        if result.get('confidence'):
            response_data['confidence'] = result['confidence']

        if result.get('anomaly_score'):
            response_data['anomaly_score'] = result['anomaly_score']

        # Add headers
        headers = {
            'Retry-After': str(retry_after),
            'X-Rate-Limit-Reason': result.get('reason', 'unknown'),
            'X-Rate-Limit-Reset': str(int(datetime.utcnow().timestamp()) + retry_after)
        }

        return JSONResponse(
            status_code=status_code,
            content=response_data,
            headers=headers
        )

    async def _track_successful_request(self, request: Request, response: Response, result: dict):
        """Track successful requests for ML model training"""
        try:
            # Only track requests that were allowed and successful
            if response.status_code < 400:
                tracking_data = {
                    'method': request.method,
                    'path': request.url.path,
                    'status_code': response.status_code,
                    'response_time': getattr(response, 'response_time', None),
                    'ip_address': result.get('ip_address'),
                    'user_agent': request.headers.get('user-agent', ''),
                    'timestamp': datetime.utcnow().isoformat(),
                    'allowed': True,
                    'reason': result.get('reason', 'within_limits')
                }

                # Store for later ML training (this would be batched)
                await self._store_for_training(tracking_data)

        except Exception as e:
            logger.error(f"Error tracking successful request: {e}")

    async def _store_for_training(self, tracking_data: dict):
        """Store request data for ML model training"""
        # In production, this would store in a database or queue
        # For now, we'll use the rate limiter's tracking
        try:
            await rate_limiter._track_request(tracking_data, getattr(tracking_data, 'tenant_id', 'default'))
        except Exception as e:
            logger.error(f"Error storing for training: {e}")


class RateLimitManager:
    """
    Management interface for rate limiting system
    Provides methods to manage whitelists, blacklists, and configurations
    """

    @staticmethod
    def add_to_whitelist(ip_address: str) -> bool:
        """Add IP address to whitelist"""
        try:
            rate_limiter.add_to_whitelist(ip_address)
            return True
        except Exception as e:
            logger.error(f"Failed to add {ip_address} to whitelist: {e}")
            return False

    @staticmethod
    def add_to_blacklist(ip_address: str) -> bool:
        """Add IP address to blacklist"""
        try:
            rate_limiter.add_to_blacklist(ip_address)
            return True
        except Exception as e:
            logger.error(f"Failed to add {ip_address} to blacklist: {e}")
            return False

    @staticmethod
    def remove_from_whitelist(ip_address: str) -> bool:
        """Remove IP address from whitelist"""
        try:
            rate_limiter.remove_from_whitelist(ip_address)
            return True
        except Exception as e:
            logger.error(f"Failed to remove {ip_address} from whitelist: {e}")
            return False

    @staticmethod
    def remove_from_blacklist(ip_address: str) -> bool:
        """Remove IP address from blacklist"""
        try:
            rate_limiter.remove_from_blacklist(ip_address)
            return True
        except Exception as e:
            logger.error(f"Failed to remove {ip_address} from blacklist: {e}")
            return False

    @staticmethod
    def update_tenant_config(tenant_id: str, config: dict) -> bool:
        """Update rate limiting configuration for tenant"""
        try:
            rate_limiter.update_tenant_config(tenant_id, config)
            return True
        except Exception as e:
            logger.error(f"Failed to update config for tenant {tenant_id}: {e}")
            return False

    @staticmethod
    def get_stats() -> dict:
        """Get rate limiting statistics"""
        try:
            return rate_limiter.get_stats()
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}

    @staticmethod
    async def cleanup_expired_data():
        """Clean up expired rate limiting data"""
        try:
            await rate_limiter.cleanup_expired_data()
        except Exception as e:
            logger.error(f"Failed to cleanup data: {e}")


# Convenience functions for easy access
def add_ip_to_whitelist(ip_address: str) -> bool:
    """Add IP to whitelist"""
    return RateLimitManager.add_to_whitelist(ip_address)


def add_ip_to_blacklist(ip_address: str) -> bool:
    """Add IP to blacklist"""
    return RateLimitManager.add_to_blacklist(ip_address)


def get_rate_limit_stats() -> dict:
    """Get rate limiting statistics"""
    return RateLimitManager.get_stats()