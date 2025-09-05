"""
Circuit Breaker Pattern Implementation for Proyecto Semilla
Enterprise-grade fault tolerance and cascade failure prevention
"""

from enum import Enum
from typing import Callable, Any, Optional, Dict
import asyncio
import time
import logging
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, failing fast
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5      # Failures before opening
    recovery_timeout: int = 60      # Seconds to wait before trying again
    expected_exception: tuple = (Exception,)  # Exceptions to catch
    success_threshold: int = 3      # Successes needed to close circuit
    timeout: float = 10.0           # Request timeout
    name: str = "default"           # Circuit breaker name for monitoring


@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker monitoring"""
    state: str
    failure_count: int
    success_count: int
    last_failure_time: Optional[float]
    total_requests: int
    total_failures: int
    total_successes: int
    uptime_percentage: float


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    def __init__(self, circuit_name: str):
        self.circuit_name = circuit_name
        super().__init__(f"Circuit breaker '{circuit_name}' is OPEN")


class CircuitBreaker:
    """
    Circuit Breaker pattern implementation for fault tolerance
    """

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.logger = logging.getLogger(f"{__name__}.{config.name}")

        # Metrics tracking
        self.total_requests = 0
        self.total_failures = 0
        self.total_successes = 0
        self.created_at = time.time()

    def __call__(self, func: Callable) -> Callable:
        """Decorator to apply circuit breaker to a function"""
        async def async_wrapper(*args, **kwargs) -> Any:
            return await self._execute_async(func, *args, **kwargs)

        def sync_wrapper(*args, **kwargs) -> Any:
            return self._execute_sync(func, *args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    async def _execute_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function with circuit breaker protection"""
        self.total_requests += 1

        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                self.logger.info(f"Circuit breaker '{self.config.name}' transitioning to HALF_OPEN")
            else:
                self.logger.warning(f"Circuit breaker '{self.config.name}' is OPEN - failing fast")
                raise CircuitBreakerOpenException(self.config.name)

        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.config.timeout
            )

            self._on_success()
            return result

        except self.config.expected_exception as e:
            self._on_failure()
            raise e
        except asyncio.TimeoutError:
            self.logger.warning(f"Request timeout for circuit breaker '{self.config.name}'")
            self._on_failure()
            raise TimeoutError(f"Request timed out after {self.config.timeout}s")

    def _execute_sync(self, func: Callable, *args, **kwargs) -> Any:
        """Execute sync function with circuit breaker protection"""
        self.total_requests += 1

        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                self.logger.info(f"Circuit breaker '{self.config.name}' transitioning to HALF_OPEN")
            else:
                self.logger.warning(f"Circuit breaker '{self.config.name}' is OPEN - failing fast")
                raise CircuitBreakerOpenException(self.config.name)

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """Handle successful execution"""
        self.total_successes += 1

        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._reset()
        else:
            self.success_count = 0

    def _on_failure(self):
        """Handle failed execution"""
        self.total_failures += 1
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            self.logger.error(f"Circuit breaker '{self.config.name}' OPEN after {self.failure_count} failures")

    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit"""
        if self.last_failure_time is None:
            return False

        return (time.time() - self.last_failure_time) >= self.config.recovery_timeout

    def _reset(self):
        """Reset circuit breaker to closed state"""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.logger.info(f"Circuit breaker '{self.config.name}' reset to CLOSED")

    def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status"""
        uptime = time.time() - self.created_at
        uptime_percentage = (self.total_successes / max(self.total_requests, 1)) * 100

        return {
            "name": self.config.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "total_requests": self.total_requests,
            "total_failures": self.total_failures,
            "total_successes": self.total_successes,
            "uptime_percentage": round(uptime_percentage, 2),
            "config": asdict(self.config)
        }

    def get_metrics(self) -> CircuitBreakerMetrics:
        """Get circuit breaker metrics"""
        uptime_percentage = (self.total_successes / max(self.total_requests, 1)) * 100

        return CircuitBreakerMetrics(
            state=self.state.value,
            failure_count=self.failure_count,
            success_count=self.success_count,
            last_failure_time=self.last_failure_time,
            total_requests=self.total_requests,
            total_failures=self.total_failures,
            total_successes=self.total_successes,
            uptime_percentage=round(uptime_percentage, 2)
        )

    def force_open(self):
        """Force circuit breaker to open state (for testing)"""
        self.state = CircuitBreakerState.OPEN
        self.logger.warning(f"Circuit breaker '{self.config.name}' forcibly opened")

    def force_close(self):
        """Force circuit breaker to closed state (for testing)"""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.logger.info(f"Circuit breaker '{self.config.name}' forcibly closed")

    def force_half_open(self):
        """Force circuit breaker to half-open state (for testing)"""
        self.state = CircuitBreakerState.HALF_OPEN
        self.logger.info(f"Circuit breaker '{self.config.name}' forcibly half-opened")


# Global circuit breaker registry
_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str) -> Optional[CircuitBreaker]:
    """Get circuit breaker by name"""
    return _circuit_breakers.get(name)


def register_circuit_breaker(name: str, circuit_breaker: CircuitBreaker):
    """Register circuit breaker globally"""
    _circuit_breakers[name] = circuit_breaker


def get_all_circuit_breakers() -> Dict[str, CircuitBreaker]:
    """Get all registered circuit breakers"""
    return _circuit_breakers.copy()


def create_circuit_breaker(config: CircuitBreakerConfig) -> CircuitBreaker:
    """Create and register a new circuit breaker"""
    circuit_breaker = CircuitBreaker(config)
    register_circuit_breaker(config.name, circuit_breaker)
    return circuit_breaker


@asynccontextmanager
async def circuit_breaker_context(name: str):
    """Context manager for circuit breaker monitoring"""
    circuit_breaker = get_circuit_breaker(name)
    if circuit_breaker:
        start_time = time.time()
        try:
            yield circuit_breaker
        finally:
            duration = time.time() - start_time
            # Log execution time for monitoring
            pass
    else:
        yield None