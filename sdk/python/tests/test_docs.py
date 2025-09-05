"""
Tests for Proyecto Semilla SDK Auto-Documentation System
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
from datetime import datetime

from proyecto_semilla import AutoDocumentation, ProyectoSemillaClient
from proyecto_semilla.models import ModuleStatus


class TestAutoDocumentation:
    """Test Auto-Documentation system functionality"""

    @pytest.fixture
    def mock_client(self):
        """Create mock client"""
        client = MagicMock(spec=ProyectoSemillaClient)
        return client

    @pytest.fixture
    def docs_system(self, mock_client):
        """Create AutoDocumentation instance"""
        return AutoDocumentation(mock_client)

    @pytest.fixture
    def sample_module_info(self):
        """Sample module information"""
        return {
            "name": "test_module",
            "display_name": "Test Module",
            "description": "A test module",
            "version": "1.0.0",
            "category": "cms",
            "status": "ready",
            "files_count": 5,
            "api_endpoints_count": 3,
            "ui_components_count": 2,
            "generated_date": "2025-01-01T00:00:00",
            "updated_date": "2025-01-02T00:00:00",
            "features": ["CRUD operations", "User management"],
            "entities": [
                {
                    "name": "TestEntity",
                    "description": "Test entity",
                    "fields": [{"name": "id", "type": "integer"}]
                }
            ],
            "apis": [
                {
                    "method": "GET",
                    "path": "/api/test",
                    "description": "Get test data"
                }
            ],
            "ui_components": ["dashboard", "form"]
        }

    def test_initialization(self, docs_system):
        """Test AutoDocumentation initialization"""
        assert docs_system.client is not None
        assert docs_system.templates_path.name == "templates"
        assert docs_system.generated_path.name == "generated"
        assert docs_system.modules_path.name == "modules"

    @pytest.mark.asyncio
    async def test_get_module_info_success(self, docs_system, mock_client, sample_module_info):
        """Test successful module info retrieval"""
        # Mock the client methods
        mock_status = ModuleStatus(
            name="test_module",
            status="ready",
            description="Test Module",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            files_count=5,
            api_endpoints_count=3,
            ui_components_count=2
        )

        mock_client.get_module_status = AsyncMock(return_value=mock_status)
        docs_system._get_module_spec = AsyncMock(return_value=None)

        result = await docs_system._get_module_info("test_module")

        assert result is not None
        assert result["name"] == "test_module"
        assert result["status"] == "ready"
        assert result["files_count"] == 5

    @pytest.mark.asyncio
    async def test_get_module_info_not_found(self, docs_system, mock_client):
        """Test module info retrieval for non-existent module"""
        mock_client.get_module_status = AsyncMock(side_effect=Exception("Module not found"))

        result = await docs_system._get_module_info("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_generate_readme(self, docs_system, sample_module_info, tmp_path):
        """Test README generation"""
        # Create temporary template
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "module_readme.md"

        template_content = """# {display_name}

{description}

Version: {version}
Features: {features_list}
"""

        template_file.write_text(template_content)

        # Override templates path
        docs_system.templates_path = template_dir

        result = await docs_system._generate_readme(sample_module_info)

        assert sample_module_info["display_name"] in result
        assert sample_module_info["description"] in result
        assert sample_module_info["version"] in result
        assert "CRUD operations" in result

    @pytest.mark.asyncio
    async def test_generate_api_docs(self, docs_system, sample_module_info):
        """Test API documentation generation"""
        result = await docs_system._generate_api_docs(sample_module_info)

        assert sample_module_info["display_name"] in result
        assert sample_module_info["version"] in result
        assert "GET /api/test" in result
        assert "Get test data" in result

    @pytest.mark.asyncio
    async def test_update_module_docs_success(self, docs_system, mock_client, sample_module_info, tmp_path):
        """Test successful module docs update"""
        # Mock dependencies
        docs_system._get_module_info = AsyncMock(return_value=sample_module_info)
        docs_system._generate_readme = AsyncMock(return_value="# Test README")
        docs_system._generate_api_docs = AsyncMock(return_value="# Test API Docs")
        docs_system._update_main_index = AsyncMock()
        docs_system._write_file = AsyncMock()

        result = await docs_system.update_module_docs("test_module")

        assert result["success"] is True
        assert result["files_updated"] == 3
        assert result["readme_generated"] is True
        assert result["api_docs_generated"] is True
        assert result["index_updated"] is True

    @pytest.mark.asyncio
    async def test_update_module_docs_module_not_found(self, docs_system, mock_client):
        """Test module docs update for non-existent module"""
        docs_system._get_module_info = AsyncMock(return_value=None)

        result = await docs_system.update_module_docs("nonexistent")

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_generate_full_docs(self, docs_system, mock_client):
        """Test full documentation generation"""
        # Mock module list
        mock_modules = [
            MagicMock(description="module1"),
            MagicMock(description="module2")
        ]
        mock_client.list_modules = AsyncMock(return_value=mock_modules)

        # Mock update results
        docs_system.update_module_docs = AsyncMock(return_value={
            "success": True,
            "files_updated": 3
        })

        result = await docs_system.generate_full_docs()

        assert result["success"] is True
        assert result["modules_processed"] == 2
        assert result["total_files_updated"] == 6

    @pytest.mark.asyncio
    async def test_validate_docs_complete(self, docs_system, tmp_path):
        """Test documentation validation with all files present"""
        # Create temporary directories and files
        modules_dir = tmp_path / "modules" / "test_module"
        generated_dir = tmp_path / "generated"

        modules_dir.mkdir(parents=True)
        generated_dir.mkdir(parents=True)

        # Create files
        (modules_dir / "README.md").write_text("# Test README")
        (generated_dir / "test_module_api.md").write_text("# Test API")
        (generated_dir / "modules_index.md").write_text("## test_module")

        # Override paths
        docs_system.modules_path = tmp_path / "modules"
        docs_system.generated_path = generated_dir

        result = await docs_system.validate_docs("test_module")

        assert result["readme_exists"] is True
        assert result["api_docs_exist"] is True
        assert result["index_updated"] is True
        assert result["all_valid"] is True

    @pytest.mark.asyncio
    async def test_validate_docs_incomplete(self, docs_system, tmp_path):
        """Test documentation validation with missing files"""
        # Create minimal directory structure
        modules_dir = tmp_path / "modules" / "test_module"
        modules_dir.mkdir(parents=True)

        # Override paths
        docs_system.modules_path = tmp_path / "modules"
        docs_system.generated_path = tmp_path / "generated"

        result = await docs_system.validate_docs("test_module")

        assert result["readme_exists"] is False
        assert result["api_docs_exist"] is False
        assert result["index_updated"] is False
        assert result["all_valid"] is False

    def test_template_rendering(self, docs_system, sample_module_info):
        """Test template rendering functionality"""
        from jinja2 import Template

        template_str = "Module: {{ name }} - Version: {{ version }}"
        template = Template(template_str)

        result = template.render(**sample_module_info)

        assert "Module: test_module" in result
        assert "Version: 1.0.0" in result