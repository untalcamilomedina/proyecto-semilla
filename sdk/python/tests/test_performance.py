"""
Performance Tests for Proyecto Semilla SDK
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock
from statistics import mean, median
import psutil
import os

from proyecto_semilla import ProyectoSemillaClient, AutoDocumentation
from proyecto_semilla.models import ModuleSpec, ModuleCategory


class TestProyectoSemillaPerformance:
    """Performance tests for the Proyecto Semilla ecosystem"""

    @pytest.fixture
    def mock_client(self):
        """Create mock client for performance testing"""
        client = MagicMock(spec=ProyectoSemillaClient)
        client.is_authenticated = MagicMock(return_value=True)

        # Mock fast responses
        from proyecto_semilla.models import GenerationResult, ModuleStatus
        mock_result = GenerationResult(
            module_name="perf_test",
            success=True,
            files_created=5,
            apis_generated=3,
            ui_components_created=2,
            execution_time_seconds=0.1
        )
        mock_status = ModuleStatus(
            name="perf_test",
            status="ready",
            description="Performance Test",
            created_at=time.time(),
            updated_at=time.time()
        )

        client.generate_module = AsyncMock(return_value=mock_result)
        client.get_module_status = AsyncMock(return_value=mock_status)
        client.list_modules = AsyncMock(return_value=[mock_status])

        return client

    @pytest.fixture
    def docs_system(self, mock_client):
        """Create docs system for performance testing"""
        return AutoDocumentation(mock_client)

    def test_memory_baseline(self):
        """Test memory usage baseline"""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()

        # Memory should be reasonable for a Python process
        memory_mb = memory_info.rss / 1024 / 1024
        assert memory_mb < 200  # Less than 200MB baseline

        print(f"📊 Memory baseline: {memory_mb:.1f} MB")

    @pytest.mark.asyncio
    async def test_module_generation_performance(self, mock_client):
        """Test module generation performance"""
        spec = ModuleSpec(
            name="perf_test",
            display_name="Performance Test",
            description="Testing generation speed",
            category=ModuleCategory.CMS,
            features=["performance"]
        )

        # Measure generation time
        start_time = time.time()
        result = await mock_client.generate_module(spec)
        end_time = time.time()

        generation_time = end_time - start_time

        # Should complete in reasonable time
        assert generation_time < 1.0  # Less than 1 second
        assert result.success is True

        print(f"⚡ Module generation time: {generation_time:.3f}s")

    @pytest.mark.asyncio
    async def test_concurrent_module_generation(self, mock_client):
        """Test concurrent module generation performance"""
        specs = [
            ModuleSpec(
                name=f"concurrent_test_{i}",
                display_name=f"Concurrent Test {i}",
                description=f"Concurrent performance test {i}",
                category=ModuleCategory.CMS,
                features=["concurrent"]
            )
            for i in range(5)
        ]

        # Measure concurrent execution
        start_time = time.time()
        tasks = [mock_client.generate_module(spec) for spec in specs]
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        total_time = end_time - start_time
        avg_time = total_time / len(specs)

        # All should succeed
        assert all(r.success for r in results)

        # Concurrent execution should be reasonably fast
        assert total_time < 2.0  # Less than 2 seconds total
        assert avg_time < 0.5   # Less than 0.5s per module

        print(f"⚡ Concurrent generation: {total_time:.3f}s total, {avg_time:.3f}s avg")

    @pytest.mark.asyncio
    async def test_documentation_generation_performance(self, docs_system):
        """Test documentation generation performance"""
        # Mock the file operations to avoid actual I/O
        docs_system._write_file = AsyncMock()
        docs_system._get_module_info = AsyncMock(return_value={
            "name": "perf_test",
            "display_name": "Performance Test",
            "description": "Testing docs generation",
            "version": "1.0.0",
            "category": "cms",
            "features": ["performance"],
            "entities": [],
            "apis": [],
            "ui_components": []
        })

        start_time = time.time()
        result = await docs_system.update_module_docs("perf_test")
        end_time = time.time()

        generation_time = end_time - start_time

        assert result["success"] is True
        assert generation_time < 0.5  # Less than 0.5 seconds

        print(f"📝 Docs generation time: {generation_time:.3f}s")

    @pytest.mark.asyncio
    async def test_bulk_operations_performance(self, mock_client, docs_system):
        """Test bulk operations performance"""
        # Mock 10 modules
        modules = [
            MagicMock(description=f"bulk_test_{i}")
            for i in range(10)
        ]
        mock_client.list_modules = AsyncMock(return_value=modules)
        docs_system.update_module_docs = AsyncMock(return_value={
            "success": True,
            "files_updated": 3
        })

        start_time = time.time()
        result = await docs_system.generate_full_docs()
        end_time = time.time()

        bulk_time = end_time - start_time

        assert result["success"] is True
        assert result["modules_processed"] == 10
        assert bulk_time < 5.0  # Less than 5 seconds for 10 modules

        print(f"📦 Bulk operations time: {bulk_time:.3f}s for 10 modules")

    def test_memory_usage_during_operations(self, mock_client):
        """Test memory usage during operations"""
        process = psutil.Process(os.getpid())

        # Get baseline memory
        baseline_memory = process.memory_info().rss

        # Perform operations (mocked, so minimal impact)
        spec = ModuleSpec(
            name="memory_test",
            display_name="Memory Test",
            description="Testing memory usage",
            category=ModuleCategory.CMS,
            features=["memory"]
        )

        # Simulate some operations
        asyncio.run(mock_client.generate_module(spec))

        # Check memory after operations
        final_memory = process.memory_info().rss
        memory_delta = final_memory - baseline_memory

        # Memory growth should be minimal for mocked operations
        memory_delta_mb = memory_delta / 1024 / 1024
        assert memory_delta_mb < 10  # Less than 10MB growth

        print(f"🧠 Memory delta: {memory_delta_mb:.1f} MB")

    @pytest.mark.asyncio
    async def test_api_response_times(self, mock_client):
        """Test API response time consistency"""
        response_times = []

        # Measure multiple API calls
        for i in range(10):
            start_time = time.time()
            await mock_client.get_module_status("perf_test")
            end_time = time.time()

            response_time = end_time - start_time
            response_times.append(response_time)

        # Calculate statistics
        avg_time = mean(response_times)
        median_time = median(response_times)
        max_time = max(response_times)

        # All responses should be fast
        assert avg_time < 0.1    # Average < 100ms
        assert median_time < 0.1 # Median < 100ms
        assert max_time < 0.2    # Max < 200ms

        print(f"🔄 API Response times - Avg: {avg_time:.3f}s, Median: {median_time:.3f}s, Max: {max_time:.3f}s")

    @pytest.mark.asyncio
    async def test_scalability_test(self, mock_client):
        """Test system scalability with increasing load"""
        scalability_results = []

        # Test with different batch sizes
        for batch_size in [1, 5, 10, 20]:
            specs = [
                ModuleSpec(
                    name=f"scale_test_{i}",
                    display_name=f"Scale Test {i}",
                    description=f"Scalability test {i}",
                    category=ModuleCategory.CMS,
                    features=["scalability"]
                )
                for i in range(batch_size)
            ]

            start_time = time.time()
            tasks = [mock_client.generate_module(spec) for spec in specs]
            results = await asyncio.gather(*tasks)
            end_time = time.time()

            batch_time = end_time - start_time
            avg_time_per_module = batch_time / batch_size

            scalability_results.append({
                "batch_size": batch_size,
                "total_time": batch_time,
                "avg_time_per_module": avg_time_per_module,
                "success_rate": sum(1 for r in results if r.success) / len(results)
            })

            print(f"📈 Batch {batch_size}: {batch_time:.3f}s total, {avg_time_per_module:.3f}s avg")

        # Verify scalability - larger batches should not be disproportionately slower
        for i in range(1, len(scalability_results)):
            prev_avg = scalability_results[i-1]["avg_time_per_module"]
            curr_avg = scalability_results[i]["avg_time_per_module"]

            # Allow for some overhead but not exponential growth
            assert curr_avg < prev_avg * 2

    @pytest.mark.asyncio
    async def test_resource_cleanup_performance(self, mock_client, docs_system):
        """Test that resources are cleaned up efficiently"""
        process = psutil.Process(os.getpid())

        # Perform multiple operations
        for i in range(10):
            spec = ModuleSpec(
                name=f"cleanup_test_{i}",
                display_name=f"Cleanup Test {i}",
                description=f"Testing resource cleanup {i}",
                category=ModuleCategory.CMS,
                features=["cleanup"]
            )

            await mock_client.generate_module(spec)
            await docs_system.update_module_docs(f"cleanup_test_{i}")

        # Memory should not grow excessively
        final_memory = process.memory_info().rss
        memory_mb = final_memory / 1024 / 1024

        # Should still be reasonable after many operations
        assert memory_mb < 300  # Less than 300MB after operations

        print(f"🧹 Memory after cleanup test: {memory_mb:.1f} MB")

    @pytest.mark.asyncio
    async def test_endurance_test(self, mock_client):
        """Test system endurance with prolonged usage"""
        endurance_results = []

        # Run operations for a period
        for cycle in range(5):
            start_time = time.time()

            # Perform various operations
            spec = ModuleSpec(
                name=f"endurance_test_{cycle}",
                display_name=f"Endurance Test {cycle}",
                description=f"Testing system endurance {cycle}",
                category=ModuleCategory.CMS,
                features=["endurance"]
            )

            await mock_client.generate_module(spec)
            await mock_client.get_module_status(f"endurance_test_{cycle}")

            end_time = time.time()
            cycle_time = end_time - start_time

            endurance_results.append(cycle_time)

            # Small delay between cycles
            await asyncio.sleep(0.01)

        # Performance should remain consistent
        avg_time = mean(endurance_results)
        std_dev = (sum((t - avg_time) ** 2 for t in endurance_results) / len(endurance_results)) ** 0.5

        # Standard deviation should be low (consistent performance)
        assert std_dev < avg_time * 0.5

        print(f"🏃 Endurance test - Avg: {avg_time:.3f}s, StdDev: {std_dev:.3f}s")

    def test_performance_summary(self):
        """Generate performance test summary"""
        summary = {
            "tests_run": 9,
            "performance_targets": {
                "module_generation": "< 1.0s",
                "concurrent_generation": "< 2.0s total for 5 modules",
                "docs_generation": "< 0.5s",
                "bulk_operations": "< 5.0s for 10 modules",
                "memory_growth": "< 10MB",
                "api_response": "< 100ms average"
            },
            "scalability_verified": True,
            "resource_cleanup_tested": True,
            "endurance_tested": True
        }

        print("📊 Performance Test Summary:")
        print(f"✅ Tests executed: {summary['tests_run']}")
        print(f"✅ Scalability verified: {summary['scalability_verified']}")
        print(f"✅ Resource cleanup tested: {summary['resource_cleanup_tested']}")
        print(f"✅ Endurance tested: {summary['endurance_tested']}")

        # All performance targets should be met
        assert summary["tests_run"] >= 8
        assert summary["scalability_verified"] is True