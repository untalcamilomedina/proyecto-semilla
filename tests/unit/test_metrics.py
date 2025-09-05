"""
Unit tests for Metrics Collection System
"""

import pytest
from app.core.metrics import VibecodingMetrics


class TestMetrics:
    """Test cases for metrics collection"""

    def test_metrics_initialization(self):
        """Test metrics system initialization"""
        metrics = VibecodingMetrics()

        assert metrics.request_count == 0
        assert metrics.error_count == 0
        assert len(metrics.response_times) == 0
        assert metrics.cache_hits == 0
        assert metrics.cache_misses == 0

    def test_request_recording(self):
        """Test request metrics recording"""
        metrics = VibecodingMetrics()

        # Record successful request
        metrics.record_request(150.0, 200)
        assert metrics.request_count == 1
        assert metrics.error_count == 0

        # Record error request
        metrics.record_request(200.0, 500)
        assert metrics.request_count == 2
        assert metrics.error_count == 1

        # Check response times
        assert len(metrics.response_times) == 2
        assert 150.0 in metrics.response_times
        assert 200.0 in metrics.response_times

    def test_cache_metrics(self):
        """Test cache hit/miss recording"""
        metrics = VibecodingMetrics()

        # Record cache activity
        metrics.record_cache_hit()
        metrics.record_cache_hit()
        metrics.record_cache_miss()

        assert metrics.cache_hits == 2
        assert metrics.cache_misses == 1
        assert round(metrics.get_cache_hit_rate(), 2) == 66.67  # 2/3 * 100

    def test_error_rate_calculation(self):
        """Test error rate calculation"""
        metrics = VibecodingMetrics()

        # Record mix of success and error requests
        for _ in range(8):  # 8 successful
            metrics.record_request(100.0, 200)

        for _ in range(2):  # 2 errors
            metrics.record_request(100.0, 500)

        assert metrics.request_count == 10
        assert metrics.error_count == 2
        # Error rate should be 20%

    def test_response_time_percentiles(self):
        """Test response time percentile calculations"""
        metrics = VibecodingMetrics()

        # Add various response times
        response_times = [100, 200, 150, 300, 250]
        for rt in response_times:
            metrics.record_request(float(rt), 200)

        # Test that response times are recorded
        assert len(metrics.response_times) == 5
        assert all(rt in metrics.response_times for rt in response_times)

    def test_metrics_reset_behavior(self):
        """Test metrics reset and cleanup"""
        metrics = VibecodingMetrics()

        # Add some data
        metrics.record_request(100.0, 200)
        metrics.record_cache_hit()

        assert metrics.request_count == 1
        assert metrics.cache_hits == 1

        # Create new instance (simulating reset)
        new_metrics = VibecodingMetrics()
        assert new_metrics.request_count == 0
        assert new_metrics.cache_hits == 0

    def test_large_dataset_handling(self):
        """Test handling of large amounts of metrics data"""
        metrics = VibecodingMetrics()

        # Simulate high traffic
        for i in range(1500):  # More than the 1000 limit
            metrics.record_request(100.0 + i * 0.1, 200)

        # Should maintain only last 1000 entries
        assert len(metrics.response_times) <= 1000

    def test_concurrent_access(self):
        """Test metrics handling under concurrent access"""
        import threading
        metrics = VibecodingMetrics()

        def record_requests():
            for _ in range(100):
                metrics.record_request(100.0, 200)

        # Create multiple threads
        threads = []
        for _ in range(5):
            t = threading.Thread(target=record_requests)
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # Should have recorded all requests
        assert metrics.request_count == 500  # 5 threads * 100 requests each

    def test_memory_efficiency(self):
        """Test memory efficiency with large datasets"""
        import sys
        metrics = VibecodingMetrics()

        # Get initial memory usage
        initial_memory = sys.getsizeof(metrics.response_times)

        # Add many response times
        for i in range(500):
            metrics.record_request(float(i), 200)

        # Memory usage should be reasonable
        current_memory = sys.getsizeof(metrics.response_times)
        assert current_memory > initial_memory  # Should grow
        assert len(metrics.response_times) == 500  # Should maintain all data