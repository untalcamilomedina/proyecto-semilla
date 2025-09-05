"""
Tests for Proyecto Semilla SDK Client
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
import httpx
from datetime import datetime

from proyecto_semilla import ProyectoSemillaClient
from proyecto_semilla.models import User, Tenant, ModuleSpec, ModuleCategory
from proyecto_semilla.exceptions import AuthenticationError, APIError


class TestProyectoSemillaClient:
    """Test Proyecto Semilla client functionality"""

    @pytest.fixture
    def client(self):
        """Create test client instance"""
        return ProyectoSemillaClient(base_url="http://test.example.com")

    @pytest.fixture
    def mock_response(self):
        """Create mock HTTP response"""
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"success": True, "data": {}}
        response.elapsed.total_seconds.return_value = 1.0
        return response

    def test_client_initialization(self, client):
        """Test client initializes correctly"""
        assert client.base_url == "http://test.example.com"
        assert client.timeout == 30.0
        assert client.auto_refresh is True
        assert client.auth is not None
        assert client.client is not None

    def test_health_check_success(self, client, mock_response):
        """Test successful health check"""
        # Mock the HTTP client
        client.client.get = AsyncMock(return_value=mock_response)
        mock_response.json.return_value = {"status": "healthy", "version": "0.1.0"}

        async def run_test():
            result = await client.health_check()
            assert result["status"] == "healthy"
            assert result["version"] == "0.1.0"
            assert "response_time" in result

        asyncio.run(run_test())

    def test_health_check_failure(self, client):
        """Test health check failure"""
        # Mock connection error
        client.client.get = AsyncMock(side_effect=httpx.ConnectError("Connection failed"))

        async def run_test():
            result = await client.health_check()
            assert result["status"] == "unhealthy"
            assert "error" in result

        asyncio.run(run_test())

    def test_is_authenticated_no_token(self, client):
        """Test authentication check without token"""
        assert client.is_authenticated() is False

    def test_get_current_user_no_auth(self, client):
        """Test get current user without authentication"""
        assert client.get_current_user() is None

    def test_get_current_tenant_no_auth(self, client):
        """Test get current tenant without authentication"""
        assert client.get_current_tenant() is None

    def test_models_import(self):
        """Test that all models can be imported"""
        from proyecto_semilla.models import (
            Tenant, User, ModuleSpec, APIResponse,
            ModuleStatus, GenerationResult
        )

        # Test model creation
        user = User(
            id="test-id",
            tenant_id="tenant-1",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"

        tenant = Tenant(
            id="tenant-1",
            name="Test Tenant",
            slug="test-tenant",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert tenant.slug == "test-tenant"

    def test_exceptions_import(self):
        """Test that all exceptions can be imported"""
        from proyecto_semilla.exceptions import (
            ProyectoSemillaError, AuthenticationError,
            APIError, ValidationError
        )

        # Test exception creation
        error = AuthenticationError("Test auth error")
        assert error.status_code == 401
        assert "Test auth error" in error.message

        api_error = APIError("Test API error", 500)
        assert api_error.status_code == 500

    @pytest.mark.asyncio
    async def test_context_manager(self, client):
        """Test async context manager"""
        async with client:
            assert client.client is not None

        # Client should be closed after context
        # Note: In real scenario, client.aclose() would be called

    def test_module_spec_creation(self):
        """Test ModuleSpec model creation and validation"""
        spec = ModuleSpec(
            name="test_module",
            display_name="Test Module",
            description="A test module for validation",
            category=ModuleCategory.CMS,
            features=["CRUD operations", "User management"],
            entities=[
                {
                    "name": "TestEntity",
                    "fields": [
                        {
                            "name": "title",
                            "type": "string",
                            "required": True
                        }
                    ]
                }
            ]
        )

        assert spec.name == "test_module"
        assert spec.category == ModuleCategory.CMS
        assert len(spec.features) == 2
        assert len(spec.entities) == 1

    def test_module_spec_validation(self):
        """Test ModuleSpec validation"""
        # Test unique features
        with pytest.raises(ValueError):
            ModuleSpec(
                name="test",
                display_name="Test",
                description="Test",
                category=ModuleCategory.CMS,
                features=["test", "test"]  # Duplicate features
            )

        # Test unique tags
        with pytest.raises(ValueError):
            ModuleSpec(
                name="test",
                display_name="Test",
                description="Test",
                category=ModuleCategory.CMS,
                features=["test"],
                tags=["tag1", "tag1"]  # Duplicate tags
            )

    def test_user_model_validation(self):
        """Test User model validation"""
        # Valid user
        user = User(
            id="user-1",
            tenant_id="tenant-1",
            email="test@example.com"
        )
        assert user.email == "test@example.com"

        # Invalid email
        with pytest.raises(ValueError):
            User(
                id="user-1",
                tenant_id="tenant-1",
                email="invalid-email"
            )

    def test_tenant_model_validation(self):
        """Test Tenant model validation"""
        # Valid tenant
        tenant = Tenant(
            id="tenant-1",
            name="Test Tenant",
            slug="test-tenant",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert tenant.slug == "test-tenant"

        # Invalid slug
        with pytest.raises(ValueError):
            Tenant(
                id="tenant-1",
                name="Test Tenant",
                slug="Test Tenant",  # Invalid characters
                created_at=datetime.now(),
                updated_at=datetime.now()
            )