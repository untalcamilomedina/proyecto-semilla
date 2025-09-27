"""
Tests for MCP Module Management System
"""

import pytest
import json
from uuid import uuid4
from unittest.mock import Mock, patch, AsyncMock

from app.services.module_service import ModuleService
from app.modules.manager import ModuleManager
from app.modules.loader import ModuleLoader
from app.modules.registry import ModuleRegistry
from app.models.module import Module, ModuleConfiguration


class TestModuleService:
    """Test ModuleService functionality"""

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return AsyncMock()

    @pytest.fixture
    def module_service(self):
        """ModuleService instance"""
        return ModuleService()

    @pytest.mark.asyncio
    async def test_get_modules(self, module_service, mock_db):
        """Test getting modules for a tenant"""
        tenant_id = uuid4()
        mock_modules = [
            Module(
                id=uuid4(),
                tenant_id=tenant_id,
                name="test-module",
                display_name="Test Module",
                version="1.0.0",
                status="active"
            )
        ]

        mock_db.execute.return_value.scalars.return_value.all.return_value = mock_modules

        result = await module_service.get_modules(str(tenant_id), mock_db)

        assert len(result) == 1
        assert result[0].name == "test-module"
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_install_module(self, module_service, mock_db):
        """Test module installation"""
        tenant_id = uuid4()
        module_name = "test-module"
        version = "1.0.0"

        # Mock registry lookup
        with patch.object(module_service, 'get_module_from_registry', new_callable=AsyncMock) as mock_registry:
            mock_registry.return_value = Mock(
                display_name="Test Module",
                description="A test module",
                author="Test Author",
                config_schema={},
                default_config={},
                dependencies=[],
                min_core_version="1.0.0",
                max_core_version="2.0.0"
            )

            # Mock validation
            with patch.object(module_service, 'validate_version_compatibility', return_value=True):
                # Mock module creation
                mock_module = Module(
                    id=uuid4(),
                    tenant_id=tenant_id,
                    name=module_name,
                    display_name="Test Module",
                    version=version,
                    status="inactive"
                )
                mock_db.add.return_value = None
                mock_db.flush = AsyncMock()
                mock_db.commit = AsyncMock()

                result = await module_service.install_module(str(tenant_id), module_name, version, {}, mock_db)

                assert result["success"] is True
                assert result["module"].name == module_name
                mock_db.add.assert_called()
                mock_db.commit.assert_called()


class TestModuleManager:
    """Test ModuleManager functionality"""

    @pytest.fixture
    def module_manager(self):
        """ModuleManager instance"""
        return ModuleManager()

    @pytest.mark.asyncio
    async def test_install_module(self, module_manager):
        """Test module installation through manager"""
        tenant_id = uuid4()
        module_name = "test-module"
        version = "1.0.0"

        with patch.object(module_manager.loader, 'download_module', return_value=True) as mock_download:
            with patch.object(module_manager.loader, 'validate_module_structure', return_value=True) as mock_validate:
                with patch.object(ModuleService, 'install_module', new_callable=AsyncMock) as mock_install:
                    mock_install.return_value = Module(
                        id=uuid4(),
                        tenant_id=tenant_id,
                        name=module_name,
                        display_name="Test Module",
                        version=version,
                        status="inactive"
                    )

                    result = await module_manager.install_module(tenant_id, module_name, version)

                    assert result["success"] is True
                    assert result["message"] is not None
                    mock_download.assert_called_once()
                    mock_validate.assert_called_once()
                    mock_install.assert_called_once()


class TestModuleLoader:
    """Test ModuleLoader functionality"""

    @pytest.fixture
    def module_loader(self):
        """ModuleLoader instance"""
        return ModuleLoader()

    def test_validate_module_structure_valid(self, module_loader, tmp_path):
        """Test validation of valid module structure"""
        # Create valid module structure
        module_path = tmp_path / "test_module"
        module_path.mkdir()

        # Create required files
        (module_path / "__init__.py").write_text("# Module init")
        (module_path / "module.json").write_text(json.dumps({
            "name": "test-module",
            "version": "1.0.0",
            "description": "Test module",
            "main": "__init__.py"
        }))

        # Create required directories
        (module_path / "handlers").mkdir()
        (module_path / "schemas").mkdir()

        result = module_loader.validate_module_structure(module_path)
        assert result is True

    def test_validate_module_structure_invalid(self, module_loader, tmp_path):
        """Test validation of invalid module structure"""
        # Create invalid module structure (missing module.json)
        module_path = tmp_path / "test_module"
        module_path.mkdir()

        (module_path / "__init__.py").write_text("# Module init")
        # Missing module.json

        result = module_loader.validate_module_structure(module_path)
        assert result is False


class TestModuleRegistry:
    """Test ModuleRegistry functionality"""

    @pytest.fixture
    def registry(self, tmp_path):
        """ModuleRegistry instance with temporary path"""
        registry_file = tmp_path / "registry.json"
        return ModuleRegistry(registry_file)

    def test_register_module(self, registry):
        """Test module registration"""
        metadata = {
            "name": "test-module",
            "display_name": "Test Module",
            "description": "A test module",
            "author": "Test Author",
            "latest_version": "1.0.0",
            "total_downloads": 0,
            "is_official": False
        }

        result = registry.register_module("test-module", metadata)
        assert result is True

        # Verify registration
        stored = registry.get_module("test-module")
        assert stored is not None
        assert stored["name"] == "test-module"
        assert stored["display_name"] == "Test Module"

    def test_get_module(self, registry):
        """Test getting module metadata"""
        metadata = {
            "name": "test-module",
            "display_name": "Test Module",
            "latest_version": "1.0.0",
            "total_downloads": 0,
            "is_official": False
        }

        registry.register_module("test-module", metadata)
        result = registry.get_module("test-module")

        assert result is not None
        assert result["name"] == "test-module"

    def test_get_nonexistent_module(self, registry):
        """Test getting non-existent module"""
        result = registry.get_module("nonexistent")
        assert result is None

    def test_list_modules(self, registry):
        """Test listing modules"""
        # Register multiple modules
        modules_data = [
            {
                "name": "module-1",
                "display_name": "Module 1",
                "latest_version": "1.0.0",
                "total_downloads": 100,
                "is_official": True
            },
            {
                "name": "module-2",
                "display_name": "Module 2",
                "latest_version": "2.0.0",
                "total_downloads": 50,
                "is_official": False
            }
        ]

        for module_data in modules_data:
            registry.register_module(module_data["name"], module_data)

        # Test listing all
        result = registry.list_modules()
        assert len(result) == 2

        # Test listing with limit
        result = registry.list_modules(limit=1)
        assert len(result) == 1

    def test_search_modules(self, registry):
        """Test searching modules"""
        modules_data = [
            {
                "name": "analytics-module",
                "display_name": "Analytics Module",
                "description": "Provides analytics functionality",
                "latest_version": "1.0.0",
                "total_downloads": 100,
                "is_official": True
            },
            {
                "name": "payment-module",
                "display_name": "Payment Module",
                "description": "Handles payment processing",
                "latest_version": "2.0.0",
                "total_downloads": 50,
                "is_official": False
            }
        ]

        for module_data in modules_data:
            registry.register_module(module_data["name"], module_data)

        # Search for analytics
        result = registry.search_modules("analytics")
        assert len(result) == 1
        assert result[0]["name"] == "analytics-module"

        # Search for non-existent term
        result = registry.search_modules("nonexistent")
        assert len(result) == 0


class TestModuleModels:
    """Test module model functionality"""

    def test_module_creation(self):
        """Test creating a module instance"""
        tenant_id = uuid4()
        module = Module(
            tenant_id=tenant_id,
            name="test-module",
            display_name="Test Module",
            version="1.0.0",
            description="A test module",
            status="inactive",
            is_system=False
        )

        assert module.tenant_id == tenant_id
        assert module.name == "test-module"
        assert module.display_name == "Test Module"
        assert module.version == "1.0.0"
        assert module.status == "inactive"
        assert module.is_system is False

    def test_module_configuration_creation(self):
        """Test creating a module configuration instance"""
        module_id = uuid4()
        tenant_id = uuid4()

        config = ModuleConfiguration(
            module_id=module_id,
            tenant_id=tenant_id,
            config_data={"setting": "value"},
            is_active=True
        )

        assert config.module_id == module_id
        assert config.tenant_id == tenant_id
        assert config.config_data == {"setting": "value"}
        assert config.is_active is True


# Integration tests
class TestModuleIntegration:
    """Integration tests for module system"""

    @pytest.mark.asyncio
    async def test_full_module_lifecycle(self):
        """Test complete module lifecycle"""
        # This would be a comprehensive integration test
        # For now, just ensure the basic components can be imported
        from app.services.module_service import ModuleService
        from app.modules.manager import ModuleManager
        from app.modules.loader import ModuleLoader
        from app.modules.registry import ModuleRegistry

        # Verify all components can be instantiated
        service = ModuleService()
        manager = ModuleManager()
        loader = ModuleLoader()
        registry = ModuleRegistry()

        assert service is not None
        assert manager is not None
        assert loader is not None
        assert registry is not None

        # Test basic registry operations
        metadata = {
            "name": "integration-test-module",
            "display_name": "Integration Test Module",
            "latest_version": "1.0.0",
            "total_downloads": 0,
            "is_official": False
        }

        result = registry.register_module("integration-test-module", metadata)
        assert result is True

        retrieved = registry.get_module("integration-test-module")
        assert retrieved is not None
        assert retrieved["name"] == "integration-test-module"