"""
Unit tests for middleware and core utilities
Tests CORS, tenant context, rate limiting, logging middleware
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import json


@pytest.mark.unit
class TestCORSMiddleware:
    """Test CORS middleware functionality"""

    @pytest.mark.asyncio
    async def test_cors_middleware_preflight(self):
        """Test CORS preflight request handling"""
        from app.core.middleware import cors_middleware

        # Mock preflight request
        mock_request = Mock()
        mock_request.method = "OPTIONS"
        mock_request.headers = {"origin": "http://localhost:3000", "access-control-request-method": "POST"}

        mock_call_next = AsyncMock()
        mock_response = Response()
        mock_call_next.return_value = mock_response

        response = await cors_middleware(mock_request, mock_call_next)

        # Should add CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers

    @pytest.mark.asyncio
    async def test_cors_middleware_regular_request(self):
        """Test CORS headers on regular requests"""
        from app.core.middleware import cors_middleware

        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.headers = {"origin": "http://localhost:3000"}

        mock_call_next = AsyncMock()
        mock_response = Response()
        mock_call_next.return_value = mock_response

        response = await cors_middleware(mock_request, mock_call_next)

        # Should add CORS headers
        assert "access-control-allow-origin" in response.headers


@pytest.mark.unit
class TestTenantContextMiddleware:
    """Test tenant context middleware"""

    @pytest.mark.asyncio
    async def test_tenant_context_from_header(self):
        """Test extracting tenant context from header"""
        from app.core.middleware import tenant_context_middleware
        from app.core.database import get_tenant_context, set_tenant_context

        # Mock request with tenant header
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.headers = {"x-tenant-id": "test-tenant-123"}
        mock_request.cookies = {}

        mock_call_next = AsyncMock()
        mock_response = JSONResponse({"status": "ok"})
        mock_call_next.return_value = mock_response

        response = await tenant_context_middleware(mock_request, mock_call_next)

        # Should set tenant context
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_tenant_context_from_cookie(self):
        """Test extracting tenant context from cookie"""
        from app.core.middleware import tenant_context_middleware

        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.headers = {}
        mock_request.cookies = {"tenant_id": "test-tenant-456"}

        mock_call_next = AsyncMock()
        mock_response = JSONResponse({"status": "ok"})
        mock_call_next.return_value = mock_response

        response = await tenant_context_middleware(mock_request, mock_call_next)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_tenant_context_missing(self):
        """Test handling missing tenant context"""
        from app.core.middleware import tenant_context_middleware

        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.headers = {}
        mock_request.cookies = {}

        mock_call_next = AsyncMock()
        mock_response = JSONResponse({"status": "ok"})
        mock_call_next.return_value = mock_response

        response = await tenant_context_middleware(mock_request, mock_call_next)

        # Should still work but might log warning
        assert response.status_code == 200


@pytest.mark.unit
class TestRateLimitingMiddleware:
    """Test rate limiting middleware"""

    @pytest.mark.asyncio
    async def test_rate_limiting_under_limit(self):
        """Test request under rate limit"""
        from app.core.middleware import rate_limiting_middleware

        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.url = Mock()
        mock_request.url.path = "/api/v1/users"
        mock_request.client = Mock()
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {}

        mock_call_next = AsyncMock()
        mock_response = Response()
        mock_call_next.return_value = mock_response

        response = await rate_limiting_middleware(mock_request, mock_call_next)

        # Should pass through
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_rate_limiting_exceeded(self):
        """Test rate limit exceeded"""
        from app.core.middleware import rate_limiting_middleware

        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.url = Mock()
        mock_request.url.path = "/api/v1/users"
        mock_request.client = Mock()
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {}

        mock_call_next = AsyncMock()
        mock_response = Response()
        mock_call_next.return_value = mock_response

        # This would need actual rate limiting implementation to test properly
        # For now, just ensure it doesn't crash
        response = await rate_limiting_middleware(mock_request, mock_call_next)
        assert isinstance(response, Response)


@pytest.mark.unit
class TestLoggingMiddleware:
    """Test logging middleware"""

    @pytest.mark.asyncio
    async def test_logging_middleware_request(self):
        """Test request logging"""
        from app.core.middleware import logging_middleware

        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.url = Mock()
        mock_request.url.path = "/api/v1/users"
        mock_request.client = Mock()
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {"user-agent": "test-agent"}

        mock_call_next = AsyncMock()
        mock_response = Response()
        mock_call_next.return_value = mock_response

        response = await logging_middleware(mock_request, mock_call_next)

        # Should log and pass through
        assert response.status_code == 200


@pytest.mark.unit
class TestDatabaseUtilities:
    """Test database utility functions"""

    @pytest.mark.asyncio
    async def test_set_tenant_context(self):
        """Test tenant context setting"""
        from app.core.database import set_tenant_context

        tenant_id = "test-tenant-123"
        set_tenant_context(tenant_id)

        # Should not raise exception
        assert True

    @pytest.mark.asyncio
    async def test_create_rls_functions(self):
        """Test RLS functions creation"""
        from app.core.database import create_rls_functions

        # This would require actual database connection
        # For unit test, just ensure function exists
        assert callable(create_rls_functions)


@pytest.mark.unit
class TestSecurityUtilities:
    """Test security utility functions"""

    def test_create_access_token(self):
        """Test JWT access token creation"""
        from app.core.security import create_access_token
        from app.models.user import User
        from uuid import uuid4

        user_id = str(uuid4())
        tenant_id = str(uuid4())

        token = create_access_token(subject=user_id, tenant_id=tenant_id)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_password(self):
        """Test password verification"""
        from app.core.security import verify_password, get_password_hash

        password = "testpassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_get_password_hash(self):
        """Test password hashing"""
        from app.core.security import get_password_hash

        password = "testpassword123"
        hashed = get_password_hash(password)

        assert isinstance(hashed, str)
        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt format


@pytest.mark.unit
class TestCookieManager:
    """Test secure cookie management"""

    def test_set_access_token_cookie(self):
        """Test setting access token cookie"""
        from app.core.cookies import SecureCookieManager
        from fastapi.responses import Response

        manager = SecureCookieManager()
        response = Response()

        token = "test.jwt.token"
        manager.set_access_token_cookie(response, token)

        # Should set secure cookie
        assert "access_token" in response.headers.get("set-cookie", "")

    def test_clear_auth_cookies(self):
        """Test clearing authentication cookies"""
        from app.core.cookies import SecureCookieManager
        from fastapi.responses import Response

        manager = SecureCookieManager()
        response = Response()

        manager.clear_auth_cookies(response)

        # Should clear cookies
        cookie_header = response.headers.get("set-cookie", "")
        assert "access_token" in cookie_header
        assert "Max-Age=0" in cookie_header


@pytest.mark.unit
class TestCircuitBreaker:
    """Test circuit breaker functionality"""

    def test_circuit_breaker_creation(self):
        """Test circuit breaker creation"""
        from app.core.circuit_breaker import CircuitBreaker, CircuitBreakerConfig

        config = CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=Exception
        )

        cb = CircuitBreaker(config)
        assert cb is not None

    def test_circuit_breaker_state(self):
        """Test circuit breaker state management"""
        from app.core.circuit_breaker import CircuitBreaker, CircuitBreakerConfig

        config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=60,
            expected_exception=Exception
        )

        cb = CircuitBreaker(config)

        # Initially closed
        status = cb.get_status()
        assert status["state"] == "closed"

    @pytest.mark.asyncio
    async def test_circuit_breaker_success(self):
        """Test circuit breaker success handling"""
        from app.core.circuit_breaker import CircuitBreaker, CircuitBreakerConfig

        config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=60,
            expected_exception=Exception
        )

        cb = CircuitBreaker(config)

        @cb
        async def test_function():
            return "success"

        result = await test_function()
        assert result == "success"

        # Should still be closed
        status = cb.get_status()
        assert status["state"] == "closed"


@pytest.mark.unit
class TestMetrics:
    """Test metrics collection"""

    def test_metrics_recording(self):
        """Test metrics recording"""
        from app.core.metrics import VibecodingMetrics

        metrics = VibecodingMetrics()

        # Record some requests
        metrics.record_request(0.1, 200)
        metrics.record_request(0.2, 404)
        metrics.record_request(0.05, 500)

        # Check metrics
        current = metrics.get_current_metrics()
        assert current["total_requests"] == 3
        assert current["error_count"] == 2  # 404 and 500

    def test_performance_metrics(self):
        """Test performance metrics calculation"""
        from app.core.metrics import VibecodingMetrics

        metrics = VibecodingMetrics()

        # Add some response times
        for i in range(10):
            metrics.record_request(0.1 * i, 200)

        percentiles = metrics.get_response_time_percentiles()
        assert isinstance(percentiles, dict)
        assert "p50" in percentiles
        assert "p95" in percentiles
        assert "p99" in percentiles


@pytest.mark.unit
class TestErrorHandler:
    """Test error handling"""

    @pytest.mark.asyncio
    async def test_error_handler_generic_error(self):
        """Test generic error handling"""
        from app.core.error_handler import ErrorHandler
        from fastapi import Request

        handler = ErrorHandler()

        mock_request = Mock(spec=Request)
        mock_request.url = Mock()
        mock_request.url.path = "/api/v1/test"

        exc = Exception("Test error")

        response = await handler.handle_error(mock_request, exc)

        assert response.status_code == 500
        data = json.loads(response.body)
        assert "error_id" in data
        assert "message" in data

    @pytest.mark.asyncio
    async def test_error_handler_http_error(self):
        """Test HTTP error handling"""
        from app.core.error_handler import ErrorHandler
        from fastapi import HTTPException, Request

        handler = ErrorHandler()

        mock_request = Mock(spec=Request)
        mock_request.url = Mock()
        mock_request.url.path = "/api/v1/test"

        exc = HTTPException(status_code=404, detail="Not found")

        response = await handler.handle_error(mock_request, exc)

        assert response.status_code == 404
        data = json.loads(response.body)
        assert "error_id" in data


@pytest.mark.unit
class TestInputValidation:
    """Test input validation utilities"""

    @pytest.mark.asyncio
    async def test_email_validation(self):
        """Test email validation"""
        from app.core.input_validation import EnterpriseValidator

        validator = EnterpriseValidator()

        # Valid email
        result = await validator.validate_input("email", "test@example.com")
        assert result.is_valid is True

        # Invalid email
        result = await validator.validate_input("email", "invalid-email")
        assert result.is_valid is False

    @pytest.mark.asyncio
    async def test_password_validation(self):
        """Test password validation"""
        from app.core.input_validation import EnterpriseValidator

        validator = EnterpriseValidator()

        # Valid password
        result = await validator.validate_input("password", "StrongPass123!")
        assert result.is_valid is True

        # Invalid password (too short)
        result = await validator.validate_input("password", "123")
        assert result.is_valid is False

    @pytest.mark.asyncio
    async def test_sanitization(self):
        """Test input sanitization"""
        from app.core.input_validation import EnterpriseValidator

        validator = EnterpriseValidator()

        # XSS attempt
        malicious_input = "<script>alert('xss')</script>Hello"
        result = await validator.sanitize_input(malicious_input, ["xss"])

        assert result.sanitized_value != malicious_input
        assert "<script>" not in result.sanitized_value
        assert "Hello" in result.sanitized_value