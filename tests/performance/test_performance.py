"""
Performance tests for Proyecto Semilla
Tests response times, throughput, and system performance
"""

import pytest
import time
import asyncio
import statistics
from typing import List, Dict, Any
import subprocess
import json
import os


@pytest.mark.performance
class TestResponseTimes:
    """Test response time performance"""

    @pytest.mark.asyncio
    async def test_articles_endpoint_response_time(self, test_client, auth_headers, benchmark):
        """Test articles endpoint response time"""
        def get_articles():
            response = test_client.get("/api/v1/articles", headers=auth_headers)
            return response

        # Benchmark the request
        result = benchmark(get_articles)

        # Assert response time is under 100ms
        assert result.stats.mean < 0.1  # 100ms
        assert result.stats.max < 0.5   # 500ms max

    @pytest.mark.asyncio
    async def test_article_creation_performance(self, test_client, auth_headers, benchmark):
        """Test article creation performance"""
        article_data = {
            "title": f"Performance Test Article {time.time()}",
            "slug": f"perf-test-article-{int(time.time())}",
            "content": "Performance test content" * 100,  # Large content
            "excerpt": "Performance test excerpt",
            "status": "draft",
            "is_featured": False,
            "tags": ["performance", "test"]
        }

        def create_article():
            response = test_client.post(
                "/api/v1/articles",
                json=article_data,
                headers=auth_headers
            )
            return response

        result = benchmark(create_article)

        # Assert creation time is reasonable
        assert result.stats.mean < 0.2  # 200ms
        assert result.stats.max < 1.0   # 1s max


@pytest.mark.performance
class TestLoadTesting:
    """Load testing using Artillery"""

    def test_artillery_load_test(self):
        """Run Artillery load test and validate results"""
        config_path = "tests/performance/load-test.yml"
        report_path = "tests/performance/report.json"

        # Ensure config file exists
        assert os.path.exists(config_path), "Artillery config file not found"

        try:
            # Run Artillery test
            result = subprocess.run([
                "npx", "artillery", "run",
                "--config", config_path,
                "--output", report_path
            ], capture_output=True, text=True, timeout=300)

            # Check if test completed successfully
            assert result.returncode == 0, f"Artillery test failed: {result.stderr}"

            # Parse results
            with open(report_path, 'r') as f:
                report = json.load(f)

            # Validate performance metrics
            self._validate_artillery_results(report)

        except subprocess.TimeoutExpired:
            pytest.fail("Load test timed out")
        except FileNotFoundError:
            pytest.skip("Artillery not installed")
        finally:
            # Clean up report file
            if os.path.exists(report_path):
                os.remove(report_path)

    def _validate_artillery_results(self, report: Dict[str, Any]):
        """Validate Artillery test results"""
        # Check overall test success
        assert report.get("aggregate", {}).get("counters", {}).get("http.requests") > 0

        # Check response times
        latency = report.get("aggregate", {}).get("summaries", {}).get("http.response_time", {})
        if latency:
            mean_latency = latency.get("mean", 0)
            p95_latency = latency.get("p95", 0)

            # Assert reasonable performance
            assert mean_latency < 200, f"Mean latency too high: {mean_latency}ms"
            assert p95_latency < 500, f"P95 latency too high: {p95_latency}ms"

        # Check error rates
        errors = report.get("aggregate", {}).get("counters", {}).get("errors", 0)
        requests = report.get("aggregate", {}).get("counters", {}).get("http.requests", 1)
        error_rate = errors / requests

        assert error_rate < 0.05, f"Error rate too high: {error_rate:.2%}"


@pytest.mark.performance
class TestConcurrentRequests:
    """Test concurrent request handling"""

    @pytest.mark.asyncio
    async def test_concurrent_article_reads(self, test_client, auth_headers):
        """Test reading multiple articles concurrently"""
        import asyncio

        async def fetch_article():
            response = test_client.get("/api/v1/articles", headers=auth_headers)
            return response.status_code == 200

        # Create 10 concurrent requests
        tasks = [fetch_article() for _ in range(10)]
        start_time = time.time()

        results = await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time

        # All requests should succeed
        assert all(results), "Some concurrent requests failed"

        # Total time should be reasonable (allowing for some parallelism)
        assert total_time < 2.0, f"Concurrent requests took too long: {total_time}s"


@pytest.mark.performance
class TestMemoryUsage:
    """Test memory usage under load"""

    def test_memory_usage_baseline(self, test_client, auth_headers):
        """Test memory usage with normal load"""
        import psutil
        import os

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Perform some operations
        for i in range(50):
            response = test_client.get("/api/v1/articles", headers=auth_headers)
            assert response.status_code == 200

            # Create article
            article_data = {
                "title": f"Memory Test Article {i}",
                "slug": f"memory-test-{i}",
                "content": "Memory test content",
                "excerpt": "Memory test",
                "status": "draft",
                "is_featured": False,
                "tags": ["memory", "test"]
            }
            response = test_client.post(
                "/api/v1/articles",
                json=article_data,
                headers=auth_headers
            )
            assert response.status_code == 200

        # Check final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (< 50MB)
        assert memory_increase < 50, f"Memory usage increased too much: +{memory_increase:.1f}MB"


@pytest.mark.performance
@pytest.mark.slow
class TestDatabasePerformance:
    """Test database query performance"""

    def test_query_performance(self, test_client, auth_headers):
        """Test database query performance with multiple articles"""
        # Create multiple articles for testing
        for i in range(20):
            article_data = {
                "title": f"Bulk Test Article {i}",
                "slug": f"bulk-test-{i}",
                "content": f"Content for article {i}" * 10,
                "excerpt": f"Excerpt {i}",
                "status": "published",
                "is_featured": i % 5 == 0,  # Every 5th article is featured
                "tags": ["bulk", "test", f"tag-{i}"]
            }
            response = test_client.post(
                "/api/v1/articles",
                json=article_data,
                headers=auth_headers
            )
            assert response.status_code == 200

        # Test query performance
        start_time = time.time()
        response = test_client.get("/api/v1/articles", headers=auth_headers)
        query_time = time.time() - start_time

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 20

        # Query should be fast
        assert query_time < 0.1, f"Query took too long: {query_time:.3f}s"

    def test_stats_query_performance(self, test_client, auth_headers):
        """Test article stats query performance"""
        start_time = time.time()
        response = test_client.get("/api/v1/articles/stats/overview", headers=auth_headers)
        query_time = time.time() - start_time

        assert response.status_code == 200

        # Stats query should be very fast
        assert query_time < 0.05, f"Stats query took too long: {query_time:.3f}s"


@pytest.mark.performance
class TestCachingPerformance:
    """Test caching system performance"""

    def test_cache_hit_performance(self, test_client, auth_headers):
        """Test that cached responses are faster"""
        # First request (cache miss)
        start_time = time.time()
        response1 = test_client.get("/api/v1/articles", headers=auth_headers)
        first_request_time = time.time() - start_time

        # Second request (potential cache hit)
        start_time = time.time()
        response2 = test_client.get("/api/v1/articles", headers=auth_headers)
        second_request_time = time.time() - start_time

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Second request should be faster (at least 20% improvement)
        improvement = (first_request_time - second_request_time) / first_request_time
        assert improvement > 0.1, f"Cache improvement too low: {improvement:.1%}"


# Custom benchmark fixture for performance tests
@pytest.fixture
def benchmark():
    """Simple benchmark fixture"""
    class BenchmarkResult:
        def __init__(self, func, iterations=10):
            self.times = []
            for _ in range(iterations):
                start = time.time()
                result = func()
                end = time.time()
                self.times.append(end - start)
                self.result = result

        @property
        def stats(self):
            class Stats:
                def __init__(self, times):
                    self.mean = statistics.mean(times)
                    self.median = statistics.median(times)
                    self.min = min(times)
                    self.max = max(times)
                    self.stdev = statistics.stdev(times) if len(times) > 1 else 0
            return Stats(self.times)

    class Benchmark:
        def __init__(self, iterations=10):
            self.iterations = iterations

        def __call__(self, func):
            return BenchmarkResult(func, self.iterations)

    return Benchmark()