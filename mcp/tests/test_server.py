"""
Tests for Proyecto Semilla MCP Server
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from mcp.server import ProyectoSemillaMCPServer


class TestProyectoSemillaMCPServer:
    """Test Proyecto Semilla MCP Server functionality"""

    @pytest.fixture
    def server(self):
        """Create test server instance"""
        return ProyectoSemillaMCPServer(
            instance_url="http://test.example.com",
            api_key="test-key"
        )

    def test_server_initialization(self, server):
        """Test server initializes correctly"""
        assert server.instance_url == "http://test.example.com"
        assert server.api_key == "test-key"
        assert server.auto_auth is True
        assert server.client is None
        assert server.authenticated is False

    def test_server_without_api_key(self):
        """Test server initialization without API key"""
        server = ProyectoSemillaMCPServer(instance_url="http://test.example.com")
        assert server.api_key is None
        assert server.auto_auth is True

    @pytest.mark.asyncio
    async def test_ensure_client_initialization(self, server):
        """Test client initialization"""
        # Mock the ProyectoSemillaClient
        with patch('mcp.server.ProyectoSemillaClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client.health_check = AsyncMock(return_value={
                'status': 'healthy',
                'version': '0.1.0'
            })
            mock_client_class.return_value = mock_client

            # Call _ensure_client
            client = await server._ensure_client()

            # Verify client was created and health check was called
            mock_client_class.assert_called_once_with(
                base_url="http://test.example.com",
                api_key="test-key",
                auto_refresh=True
            )
            mock_client.health_check.assert_called_once()
            assert server.authenticated is True

    @pytest.mark.asyncio
    async def test_ensure_client_health_check_failure(self, server):
        """Test client initialization with health check failure"""
        with patch('mcp.server.ProyectoSemillaClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client.health_check = AsyncMock(return_value={
                'status': 'unhealthy',
                'error': 'Connection failed'
            })
            mock_client_class.return_value = mock_client

            # Call _ensure_client and expect exception
            with pytest.raises(Exception):  # APIError
                await server._ensure_client()

            assert server.authenticated is False

    def test_tools_registration(self, server):
        """Test that tools are registered correctly"""
        # The server should have registered tools during initialization
        # We can't easily test the exact tools without mocking the MCP framework
        # But we can verify the server was initialized
        assert server is not None
        assert hasattr(server, '_ProyectoSemillaMCPServer__tools')
        assert hasattr(server, '_ProyectoSemillaMCPServer__resources')

    def test_resources_registration(self, server):
        """Test that resources are registered correctly"""
        # Similar to tools, we verify the server has the necessary attributes
        assert server is not None
        assert hasattr(server, '_ProyectoSemillaMCPServer__resources')

    @pytest.mark.asyncio
    async def test_generate_module_tool_mock(self, server):
        """Test generate_module tool with mocked client"""
        with patch('mcp.server.ProyectoSemillaClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client.generate_module = AsyncMock(return_value=MagicMock(
                module_name="test_module",
                files_created=5,
                apis_generated=3,
                ui_components_created=2,
                execution_time_seconds=2.5
            ))
            mock_client_class.return_value = mock_client

            # Mock the _ensure_client method
            server._ensure_client = AsyncMock(return_value=mock_client)

            # Call the tool (this would normally be done through MCP protocol)
            # For testing, we'll simulate the tool call
            result = await server._ProyectoSemillaMCPServer__tools['generate_module'].func(
                name="test_module",
                description="Test module",
                category="cms",
                features=["CRUD operations"]
            )

            # Verify the result
            assert "✅ Module 'test_module' generated successfully!" in result
            assert "Files Created: 5" in result
            assert "APIs Generated: 3" in result
            assert "UI Components: 2" in result

    def test_server_configuration(self, server):
        """Test server configuration parameters"""
        assert server.instance_url == "http://test.example.com"
        assert server.api_key == "test-key"
        assert server.auto_auth is True

    def test_server_name(self, server):
        """Test server name configuration"""
        assert server.name == "proyecto-semilla-mcp"

    @pytest.mark.asyncio
    async def test_multiple_client_calls(self, server):
        """Test multiple calls to _ensure_client reuse the same client"""
        with patch('mcp.server.ProyectoSemillaClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client.health_check = AsyncMock(return_value={
                'status': 'healthy',
                'version': '0.1.0'
            })
            mock_client_class.return_value = mock_client

            # First call
            client1 = await server._ensure_client()
            # Second call should reuse the same client
            client2 = await server._ensure_client()

            # Should be the same client instance
            assert client1 is client2
            # Should only create client once
            assert mock_client_class.call_count == 1