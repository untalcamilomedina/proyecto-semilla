"""
Unit tests for Circuit Breaker implementation
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.core.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitBreakerOpenException


class TestCircuitBreaker:
    """Test cases for Circuit Breaker functionality"""

    def test_circuit_breaker_creation(self):
        """Test circuit breaker creation with default config"""
        config = CircuitBreakerConfig(name="test_circuit")
        circuit_breaker = CircuitBreaker(config)

        assert circuit_breaker.config.name == "test_circuit"
        assert circuit_breaker.state.value == "closed"
        assert circuit_breaker.failure_count == 0
        assert circuit_breaker.success_count == 0

    def test_circuit_breaker_success_flow(self):
        """Test successful execution flow"""
        config = CircuitBreakerConfig(name="test_circuit")
        circuit_breaker = CircuitBreaker(config)

        @circuit_breaker
        def successful_function():
            return "success"

        result = successful_function()
        assert result == "success"
        assert circuit_breaker.state.value == "closed"
        assert circuit_breaker.failure_count == 0

    def test_circuit_breaker_failure_flow(self):
        """Test failure and recovery flow"""
        config = CircuitBreakerConfig(
            name="test_circuit",
            failure_threshold=2,
            recovery_timeout=1
        )
        circuit_breaker = CircuitBreaker(config)

        @circuit_breaker
        def failing_function():
            raise Exception("Test failure")

        # First failure
        with pytest.raises(Exception):
            failing_function()
        assert circuit_breaker.state.value == "closed"
        assert circuit_breaker.failure_count == 1

        # Second failure - should open circuit
        with pytest.raises(Exception):
            failing_function()
        assert circuit_breaker.state.value == "open"
        assert circuit_breaker.failure_count == 2

        # Third attempt - should fail fast
        with pytest.raises(CircuitBreakerOpenException):
            failing_function()
        assert circuit_breaker.state.value == "open"

    def test_circuit_breaker_recovery(self):
        """Test circuit breaker recovery after timeout"""
        config = CircuitBreakerConfig(
            name="test_circuit",
            failure_threshold=1,
            recovery_timeout=0.1  # Very short for testing
        )
        circuit_breaker = CircuitBreaker(config)

        @circuit_breaker
        def failing_function():
            raise Exception("Test failure")

        # Cause failure and open circuit
        with pytest.raises(Exception):
            failing_function()
        assert circuit_breaker.state.value == "open"

        # Wait for recovery timeout
        import time
        time.sleep(0.2)

        # Next call should attempt recovery (half-open)
        with pytest.raises(Exception):
            failing_function()
        # The circuit breaker should transition to half-open after the first attempt
        assert circuit_breaker.state.value == "half_open"

    def test_circuit_breaker_success_recovery(self):
        """Test successful recovery closes circuit"""
        config = CircuitBreakerConfig(
            name="test_circuit",
            failure_threshold=1,
            recovery_timeout=0.1,
            success_threshold=2
        )
        circuit_breaker = CircuitBreaker(config)

        call_count = 0

        @circuit_breaker
        def sometimes_failing_function():
            nonlocal call_count
            call_count += 1
            if call_count == 2:  # First call after failure
                raise Exception("First call after failure")
            return "success"

        # Cause initial failure
        with pytest.raises(Exception):
            sometimes_failing_function()
        assert circuit_breaker.state.value == "open"

        # Wait for recovery
        import time
        time.sleep(0.2)

        # First success in half-open state
        result = sometimes_failing_function()
        assert result == "success"
        assert circuit_breaker.state.value == "half_open"
        assert circuit_breaker.success_count == 1

        # Second success should close circuit
        result = sometimes_failing_function()
        assert result == "success"
        assert circuit_breaker.state.value == "closed"
        assert circuit_breaker.success_count == 2

    def test_circuit_breaker_timeout(self):
        """Test timeout handling"""
        config = CircuitBreakerConfig(
            name="test_circuit",
            timeout=0.1
        )
        circuit_breaker = CircuitBreaker(config)

        @circuit_breaker
        async def slow_function():
            await asyncio.sleep(0.2)  # Longer than timeout
            return "success"

        with pytest.raises(asyncio.TimeoutError):
            asyncio.run(slow_function())

        # Timeout should count as failure in our implementation
        assert circuit_breaker.failure_count == 1

    def test_circuit_breaker_metrics(self):
        """Test circuit breaker metrics collection"""
        config = CircuitBreakerConfig(name="test_circuit")
        circuit_breaker = CircuitBreaker(config)

        @circuit_breaker
        def successful_function():
            return "success"

        # Generate some activity
        for _ in range(3):
            successful_function()

        metrics = circuit_breaker.get_metrics()
        assert metrics.total_requests == 3
        assert metrics.total_successes == 3
        assert metrics.total_failures == 0
        assert metrics.uptime_percentage == 100.0

    def test_circuit_breaker_manual_control(self):
        """Test manual circuit breaker control"""
        config = CircuitBreakerConfig(name="test_circuit")
        circuit_breaker = CircuitBreaker(config)

        # Test manual open
        circuit_breaker.force_open()
        assert circuit_breaker.state.value == "open"

        # Test manual close
        circuit_breaker.force_close()
        assert circuit_breaker.state.value == "closed"

        # Test manual half-open
        circuit_breaker.force_half_open()
        assert circuit_breaker.state.value == "half_open"

    def test_async_circuit_breaker(self):
        """Test async function decoration"""
        config = CircuitBreakerConfig(name="async_test")
        circuit_breaker = CircuitBreaker(config)

        @circuit_breaker
        async def async_function():
            return "async success"

        result = asyncio.run(async_function())
        assert result == "async success"
        assert circuit_breaker.state.value == "closed"