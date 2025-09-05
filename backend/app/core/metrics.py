"""
Vibecoding Metrics Collection System
Enterprise-grade monitoring and metrics for Proyecto Semilla
"""

import time
import psutil
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    response_time_p50: float = 0.0
    response_time_p95: float = 0.0
    response_time_p99: float = 0.0
    cache_hit_rate: float = 0.0
    memory_usage_mb: float = 0.0
    active_connections: int = 0
    error_rate_percentage: float = 0.0
    timestamp: float = 0.0


@dataclass
class SystemHealth:
    """System health status"""
    database_status: str = "unknown"
    cache_status: str = "unknown"
    external_services_status: str = "unknown"
    overall_status: str = "unknown"
    last_check: float = 0.0


class VibecodingMetrics:
    """
    Centralized metrics collection system for Proyecto Semilla
    Supports Prometheus-style metrics and custom monitoring
    """

    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
        self.cache_hits = 0
        self.cache_misses = 0

        # Historical data for trends
        self.performance_history = []
        self.max_history_size = 1000

        # Current metrics
        self.current_metrics = PerformanceMetrics()

    def record_request(self, response_time: float, status_code: int):
        """Record HTTP request metrics"""
        self.request_count += 1

        if status_code >= 400:
            self.error_count += 1

        # Keep response times for percentile calculations
        self.response_times.append(response_time)
        if len(self.response_times) > 1000:  # Keep last 1000 requests
            self.response_times.pop(0)

    def record_cache_hit(self):
        """Record cache hit"""
        self.cache_hits += 1

    def record_cache_miss(self):
        """Record cache miss"""
        self.cache_misses += 1

    def get_cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return (self.cache_hits / total) * 100

    def get_error_rate(self) -> float:
        """Calculate error rate percentage"""
        if self.request_count == 0:
            return 0.0
        return (self.error_count / self.request_count) * 100

    def get_response_time_percentiles(self) -> Dict[str, float]:
        """Calculate response time percentiles"""
        if not self.response_times:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}

        sorted_times = sorted(self.response_times)
        n = len(sorted_times)

        p50_index = int(n * 0.5)
        p95_index = int(n * 0.95)
        p99_index = int(n * 0.99)

        return {
            "p50": sorted_times[min(p50_index, n-1)],
            "p95": sorted_times[min(p95_index, n-1)],
            "p99": sorted_times[min(p99_index, n-1)]
        }

    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024

    def update_current_metrics(self):
        """Update current metrics snapshot"""
        percentiles = self.get_response_time_percentiles()

        self.current_metrics = PerformanceMetrics(
            response_time_p50=percentiles["p50"],
            response_time_p95=percentiles["p95"],
            response_time_p99=percentiles["p99"],
            cache_hit_rate=self.get_cache_hit_rate(),
            memory_usage_mb=self.get_memory_usage(),
            active_connections=getattr(self, 'active_connections', 0),
            error_rate_percentage=self.get_error_rate(),
            timestamp=time.time()
        )

        # Add to history
        self.performance_history.append(self.current_metrics)
        if len(self.performance_history) > self.max_history_size:
            self.performance_history.pop(0)

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics as dictionary"""
        self.update_current_metrics()
        return asdict(self.current_metrics)

    def get_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance trends for the last N hours"""
        cutoff_time = time.time() - (hours * 3600)

        recent_metrics = [
            m for m in self.performance_history
            if m.timestamp > cutoff_time
        ]

        if not recent_metrics:
            return {"error": "No data available for the specified time range"}

        # Calculate trends
        response_times = [m.response_time_p95 for m in recent_metrics]
        cache_rates = [m.cache_hit_rate for m in recent_metrics]
        error_rates = [m.error_rate_percentage for m in recent_metrics]

        return {
            "time_range_hours": hours,
            "data_points": len(recent_metrics),
            "response_time_trend": {
                "current": response_times[-1] if response_times else 0,
                "average": sum(response_times) / len(response_times) if response_times else 0,
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0
            },
            "cache_performance": {
                "current": cache_rates[-1] if cache_rates else 0,
                "average": sum(cache_rates) / len(cache_rates) if cache_rates else 0
            },
            "error_rate_trend": {
                "current": error_rates[-1] if error_rates else 0,
                "average": sum(error_rates) / len(error_rates) if error_rates else 0
            }
        }

    def get_prometheus_metrics(self) -> str:
        """Generate Prometheus-compatible metrics output"""
        self.update_current_metrics()

        metrics_output = f"""# HELP vibecoding_response_time_p95 Response time 95th percentile
# TYPE vibecoding_response_time_p95 gauge
vibecoding_response_time_p95 {self.current_metrics.response_time_p95}

# HELP vibecoding_cache_hit_rate Cache hit rate percentage
# TYPE vibecoding_cache_hit_rate gauge
vibecoding_cache_hit_rate {self.current_metrics.cache_hit_rate}

# HELP vibecoding_memory_usage_mb Memory usage in MB
# TYPE vibecoding_memory_usage_mb gauge
vibecoding_memory_usage_mb {self.current_metrics.memory_usage_mb}

# HELP vibecoding_error_rate_percentage Error rate percentage
# TYPE vibecoding_error_rate_percentage gauge
vibecoding_error_rate_percentage {self.current_metrics.error_rate_percentage}

# HELP vibecoding_active_connections Number of active connections
# TYPE vibecoding_active_connections gauge
vibecoding_active_connections {self.current_metrics.active_connections}

# HELP vibecoding_uptime_seconds System uptime in seconds
# TYPE vibecoding_uptime_seconds counter
vibecoding_uptime_seconds {time.time() - self.start_time}
"""

        return metrics_output


# Global metrics instance
metrics = VibecodingMetrics()


def get_metrics() -> VibecodingMetrics:
    """Dependency injection for metrics"""
    return metrics


@asynccontextmanager
async def metrics_context():
    """Context manager for metrics collection"""
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        # This would be called from middleware
        pass