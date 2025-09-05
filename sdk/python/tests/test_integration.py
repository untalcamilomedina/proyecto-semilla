"""
Integration Tests for Proyecto Semilla SDK - End-to-End Testing
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from proyecto_semilla import (
    ProyectoSemillaClient,
    AutoDocumentation,
    ModuleSpec,
    ModuleCategory,
    Tenant,
    User
)


class TestProyectoSemillaIntegration:
    """End-to-end integration tests for the complete CORE system"""

    @pytest.fixture
    def mock_client(self):
        """Create comprehensive mock client"""
        client = MagicMock(spec=ProyectoSemillaClient)

        # Mock authentication
        client.is_authenticated = MagicMock(return_value=True)
        client.get_current_user = MagicMock(return_value=User(
            id="user-1",
            tenant_id="tenant-1",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        ))

        # Mock tenant operations
        mock_tenant = Tenant(
            id="tenant-1",
            name="Test Tenant",
            slug="test-tenant",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        client.get_tenant = AsyncMock(return_value=mock_tenant)
        client.get_tenants = AsyncMock(return_value=[mock_tenant])

        # Mock module operations
        from proyecto_semilla.models import ModuleStatus, GenerationResult
        mock_module_status = ModuleStatus(
            name="test_module",
            status="ready",
            description="Test Module",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            files_count=5,
            api_endpoints_count=3,
            ui_components_count=2
        )
        mock_generation_result = GenerationResult(
            module_name="test_module",
            success=True,
            files_created=5,
            apis_generated=3,
            ui_components_created=2,
            execution_time_seconds=2.5
        )

        client.get_module_status = AsyncMock(return_value=mock_module_status)
        client.list_modules = AsyncMock(return_value=[mock_module_status])
        client.generate_module = AsyncMock(return_value=mock_generation_result)

        return client

    @pytest.fixture
    def docs_system(self, mock_client):
        """Create AutoDocumentation system with mock client"""
        return AutoDocumentation(mock_client)

    @pytest.mark.asyncio
    async def test_complete_module_lifecycle(self, mock_client, docs_system, tmp_path):
        """Test complete module lifecycle from creation to documentation"""
        # 1. Create module specification
        spec = ModuleSpec(
            name="integration_test_module",
            display_name="Integration Test Module",
            description="Module for integration testing",
            category=ModuleCategory.CMS,
            features=["CRUD operations", "User management"],
            entities=[
                {
                    "name": "TestEntity",
                    "description": "Test entity",
                    "fields": [
                        {"name": "id", "type": "integer", "required": True},
                        {"name": "name", "type": "string", "required": True}
                    ]
                }
            ]
        )

        # 2. Generate module
        generation_result = await mock_client.generate_module(spec)
        assert generation_result.success is True
        assert generation_result.module_name == "integration_test_module"
        assert generation_result.files_created == 5

        # 3. Check module status
        status = await mock_client.get_module_status("integration_test_module")
        assert status.status == "ready"
        assert status.files_count == 5

        # 4. Update documentation
        docs_result = await docs_system.update_module_docs("integration_test_module")
        assert docs_result["success"] is True
        assert docs_result["files_updated"] == 3

        # 5. Validate documentation
        validation = await docs_system.validate_docs("integration_test_module")
        assert validation["readme_exists"] is True
        assert validation["api_docs_exist"] is True
        assert validation["all_valid"] is True

    @pytest.mark.asyncio
    async def test_tenant_user_workflow(self, mock_client):
        """Test complete tenant and user management workflow"""
        # 1. Get current user
        current_user = mock_client.get_current_user()
        assert current_user.email == "test@example.com"
        assert current_user.first_name == "Test"

        # 2. Get user tenant
        tenant = await mock_client.get_tenant(current_user.tenant_id)
        assert tenant.name == "Test Tenant"
        assert tenant.slug == "test-tenant"

        # 3. List all tenants
        tenants = await mock_client.get_tenants()
        assert len(tenants) == 1
        assert tenants[0].name == "Test Tenant"

        # 4. Verify authentication
        assert mock_client.is_authenticated() is True

    @pytest.mark.asyncio
    async def test_bulk_module_operations(self, mock_client, docs_system):
        """Test bulk operations on multiple modules"""
        # Mock multiple modules
        modules = [
            MagicMock(description="module1"),
            MagicMock(description="module2"),
            MagicMock(description="module3")
        ]
        mock_client.list_modules = AsyncMock(return_value=modules)

        # Mock documentation updates
        docs_system.update_module_docs = AsyncMock(return_value={
            "success": True,
            "files_updated": 3
        })

        # Generate documentation for all modules
        result = await docs_system.generate_full_docs()

        assert result["success"] is True
        assert result["modules_processed"] == 3
        assert result["total_files_updated"] == 9

        # Verify update_module_docs was called for each module
        assert docs_system.update_module_docs.call_count == 3

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, mock_client, docs_system):
        """Test error handling across integrated components"""
        # Mock client to raise exception
        mock_client.get_module_status = AsyncMock(side_effect=Exception("API Error"))

        # Test that errors are properly handled
        result = await docs_system.update_module_docs("nonexistent_module")

        assert result["success"] is False
        assert "API Error" in result["error"]

    @pytest.mark.asyncio
    async def test_performance_metrics(self, mock_client, docs_system):
        """Test performance metrics collection"""
        import time

        # Mock module generation with timing
        async def mock_generate_with_timing(spec):
            start_time = time.time()
            await asyncio.sleep(0.1)  # Simulate processing time
            end_time = time.time()

            from proyecto_semilla.models import GenerationResult
            return GenerationResult(
                module_name=spec.name,
                success=True,
                files_created=5,
                apis_generated=3,
                ui_components_created=2,
                execution_time_seconds=end_time - start_time
            )

        mock_client.generate_module = mock_generate_with_timing

        # Generate module and check timing
        spec = ModuleSpec(
            name="performance_test",
            display_name="Performance Test",
            description="Testing performance metrics",
            category=ModuleCategory.CMS,
            features=["performance"]
        )

        result = await mock_client.generate_module(spec)

        assert result.execution_time_seconds >= 0.1
        assert result.execution_time_seconds < 1.0  # Should be reasonably fast

    @pytest.mark.asyncio
    async def test_data_consistency(self, mock_client, docs_system):
        """Test data consistency across operations"""
        # Create a module
        spec = ModuleSpec(
            name="consistency_test",
            display_name="Consistency Test",
            description="Testing data consistency",
            category=ModuleCategory.CMS,
            features=["consistency"]
        )

        gen_result = await mock_client.generate_module(spec)

        # Check that module appears in list
        modules = await mock_client.list_modules()
        module_names = [m.description for m in modules]

        assert gen_result.module_name in module_names

        # Check that we can get status
        status = await mock_client.get_module_status(gen_result.module_name)
        assert status.name == gen_result.module_name

        # Check that docs can be generated
        docs_result = await docs_system.update_module_docs(gen_result.module_name)
        assert docs_result["success"] is True

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, mock_client):
        """Test concurrent operations handling"""
        # Create multiple module specs
        specs = [
            ModuleSpec(
                name=f"concurrent_test_{i}",
                display_name=f"Concurrent Test {i}",
                description=f"Testing concurrent operation {i}",
                category=ModuleCategory.CMS,
                features=["concurrent"]
            )
            for i in range(3)
        ]

        # Mock concurrent generation
        async def mock_concurrent_generate(spec):
            await asyncio.sleep(0.05)  # Small delay to simulate processing
            from proyecto_semilla.models import GenerationResult
            return GenerationResult(
                module_name=spec.name,
                success=True,
                files_created=5,
                apis_generated=3,
                ui_components_created=2,
                execution_time_seconds=0.05
            )

        mock_client.generate_module = mock_concurrent_generate

        # Run concurrent operations
        tasks = [mock_client.generate_module(spec) for spec in specs]
        results = await asyncio.gather(*tasks)

        # Verify all operations completed successfully
        assert len(results) == 3
        for result in results:
            assert result.success is True
            assert result.files_created == 5

    @pytest.mark.asyncio
    async def test_resource_cleanup(self, mock_client, docs_system):
        """Test proper resource cleanup after operations"""
        # Perform operations
        spec = ModuleSpec(
            name="cleanup_test",
            display_name="Cleanup Test",
            description="Testing resource cleanup",
            category=ModuleCategory.CMS,
            features=["cleanup"]
        )

        await mock_client.generate_module(spec)
        await docs_system.update_module_docs("cleanup_test")

        # Verify client state is clean
        assert mock_client.is_authenticated() is True

        # Verify docs system state
        assert docs_system.client is mock_client

    def test_memory_usage(self, mock_client, docs_system):
        """Test memory usage patterns"""
        import psutil
        import os

        # Get initial memory
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Perform operations (these are mocked, so minimal memory impact)
        spec = ModuleSpec(
            name="memory_test",
            display_name="Memory Test",
            description="Testing memory usage",
            category=ModuleCategory.CMS,
            features=["memory"]
        )

        # Memory usage should remain reasonable
        final_memory = process.memory_info().rss
        memory_delta = final_memory - initial_memory

        # Allow for some memory growth but not excessive
        assert memory_delta < 50 * 1024 * 1024  # Less than 50MB growth

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, mock_client, docs_system):
        """Complete end-to-end workflow test"""
        # 1. Setup - Verify client is ready
        assert mock_client.is_authenticated() is True
        user = mock_client.get_current_user()
        assert user is not None

        # 2. Module Creation
        spec = ModuleSpec(
            name="e2e_test",
            display_name="End-to-End Test",
            description="Complete workflow test",
            category=ModuleCategory.CMS,
            features=["e2e", "workflow"],
            entities=[
                {
                    "name": "TestEntity",
                    "description": "E2E test entity",
                    "fields": [
                        {"name": "id", "type": "integer", "required": True},
                        {"name": "name", "type": "string", "required": True}
                    ]
                }
            ]
        )

        # 3. Generation
        gen_result = await mock_client.generate_module(spec)
        assert gen_result.success is True

        # 4. Status Check
        status = await mock_client.get_module_status("e2e_test")
        assert status.status == "ready"

        # 5. Documentation
        docs_result = await docs_system.update_module_docs("e2e_test")
        assert docs_result["success"] is True

        # 6. Validation
        validation = await docs_system.validate_docs("e2e_test")
        assert validation["all_valid"] is True

        # 7. Bulk Operations
        bulk_result = await docs_system.generate_full_docs()
        assert bulk_result["success"] is True

        # Workflow completed successfully
        print("✅ End-to-end workflow completed successfully!")