"""
Unit tests for Configuration Validator System
"""

import os
import sys
import json
import tempfile
import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config_validator import (
    ConfigurationValidator, 
    ConfigurationGenerator,
    ValidationStatus, 
    ConfigType,
    ValidationResult,
    ServerConfig,
    ClientConfig
)
from environment_detector import SystemEnvironment, LLMClient, LLMClientInfo


class TestConfigurationValidator:
    """Test cases for ConfigurationValidator class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_environment = self.create_mock_environment()
        self.validator = ConfigurationValidator(self.mock_environment)
    
    def create_mock_environment(self):
        """Create a mock system environment"""
        mock_env = Mock(spec=SystemEnvironment)
        mock_env.llm_clients = [
            Mock(spec=LLMClientInfo,
                 client_type=LLMClient.CLAUDE_DESKTOP,
                 config_path='/path/to/claude_config.json')
        ]
        mock_env.mcp_server_status = {
            'server_path': '/path/to/server.py'
        }
        mock_env.project_root = '/path/to/project'
        mock_env.python_env = Mock()
        mock_env.python_env.executable = '/usr/bin/python3'
        
        return mock_env
    
    @pytest.mark.asyncio
    async def test_validate_all_configurations(self):
        """Test validation of all configurations"""
        with patch.object(self.validator, '_validate_client_config') as mock_validate:
            mock_config = Mock(spec=ClientConfig)
            mock_validate.return_value = mock_config
            
            configs = await self.validator.validate_all_configurations()
            
            assert len(configs) == 1
            assert mock_validate.call_count == 1
    
    @pytest.mark.asyncio
    async def test_validate_client_config_success(self):
        """Test successful client configuration validation"""
        mock_client = Mock()
        mock_client.client_type = LLMClient.CLAUDE_DESKTOP
        mock_client.config_path = '/path/to/config.json'
        
        with patch.object(self.validator, '_load_server_configs') as mock_load:
            with patch.object(self.validator, '_validate_server_config') as mock_validate_server:
                mock_server = Mock(spec=ServerConfig)
                mock_load.return_value = [mock_server]
                mock_validate_server.return_value = [
                    ValidationResult("test", ValidationStatus.VALID, "Valid")
                ]
                
                config = await self.validator._validate_client_config(mock_client)
                
                assert isinstance(config, ClientConfig)
                assert config.is_valid
                assert len(config.servers) == 1
    
    @pytest.mark.asyncio
    async def test_validate_client_config_error(self):
        """Test client configuration validation with error"""
        mock_client = Mock()
        mock_client.client_type = LLMClient.CLAUDE_DESKTOP
        mock_client.config_path = '/path/to/config.json'
        
        with patch.object(self.validator, '_load_server_configs') as mock_load:
            mock_load.side_effect = ValueError("Invalid config")
            
            config = await self.validator._validate_client_config(mock_client)
            
            assert isinstance(config, ClientConfig)
            assert not config.is_valid
            assert len(config.validation_results) > 0
            assert config.validation_results[0].status == ValidationStatus.ERROR
    
    @pytest.mark.asyncio
    async def test_load_server_configs_claude_desktop(self):
        """Test loading server configs for Claude Desktop"""
        config_data = {
            "mcpServers": {
                "test-server": {
                    "command": "python",
                    "args": ["server.py"],
                    "env": {"TEST_VAR": "value"},
                    "cwd": "/path/to/project"
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        try:
            servers = await self.validator._load_server_configs(config_path, ConfigType.CLAUDE_DESKTOP)
            
            assert len(servers) == 1
            server = servers[0]
            assert server.name == "test-server"
            assert server.command == "python"
            assert server.args == ["server.py"]
            assert server.env == {"TEST_VAR": "value"}
            assert server.working_directory == "/path/to/project"
        finally:
            os.unlink(config_path)
    
    @pytest.mark.asyncio
    async def test_load_server_configs_invalid_json(self):
        """Test loading server configs with invalid JSON"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"invalid": json}')  # Invalid JSON
            config_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Invalid configuration format"):
                await self.validator._load_server_configs(config_path, ConfigType.CLAUDE_DESKTOP)
        finally:
            os.unlink(config_path)
    
    @pytest.mark.asyncio
    async def test_validate_server_config(self):
        """Test validation of a single server configuration"""
        server = ServerConfig(
            name="test-server",
            command="python",
            args=["server.py"],
            env={},
            working_directory="/path/to/project"
        )
        
        with patch.object(self.validator, '_validate_command') as mock_cmd:
            with patch.object(self.validator, '_validate_arguments') as mock_args:
                with patch.object(self.validator, '_validate_environment_variables') as mock_env:
                    with patch.object(self.validator, '_validate_working_directory') as mock_workdir:
                        mock_cmd.return_value = ValidationResult("cmd", ValidationStatus.VALID, "Valid")
                        mock_args.return_value = ValidationResult("args", ValidationStatus.VALID, "Valid")
                        mock_env.return_value = ValidationResult("env", ValidationStatus.VALID, "Valid")
                        mock_workdir.return_value = ValidationResult("workdir", ValidationStatus.VALID, "Valid")
                        
                        results = await self.validator._validate_server_config(server)
                        
                        assert len(results) == 4
                        assert all(r.status == ValidationStatus.VALID for r in results)
    
    @pytest.mark.asyncio
    async def test_validate_command_python_success(self):
        """Test command validation for Python with success"""
        server = ServerConfig("test", "python", [], {})
        
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b"Python 3.9.0", b""))
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process):
            with patch('asyncio.wait_for', return_value=(b"Python 3.9.0", b"")):
                result = await self.validator._validate_command(server)
                
                assert result.status == ValidationStatus.VALID
                assert "Python" in result.message
    
    @pytest.mark.asyncio
    async def test_validate_command_python_error(self):
        """Test command validation for Python with error"""
        server = ServerConfig("test", "python", [], {})
        
        mock_process = Mock()
        mock_process.returncode = 1
        mock_process.communicate = AsyncMock(return_value=(b"", b"Command not found"))
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process):
            with patch('asyncio.wait_for', return_value=(b"", b"Command not found")):
                result = await self.validator._validate_command(server)
                
                assert result.status == ValidationStatus.ERROR
                assert "failed" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_validate_command_timeout(self):
        """Test command validation with timeout"""
        server = ServerConfig("test", "python", [], {})
        
        with patch('asyncio.create_subprocess_exec'):
            with patch('asyncio.wait_for', side_effect=asyncio.TimeoutError):
                result = await self.validator._validate_command(server)
                
                assert result.status == ValidationStatus.WARNING
                assert "timed out" in result.message.lower()
    
    def test_validate_arguments_script_exists(self):
        """Test argument validation when script file exists"""
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
            script_path = f.name
        
        try:
            server = ServerConfig("test", "python", [script_path], {})
            result = self.validator._validate_arguments(server)
            
            assert result.status == ValidationStatus.VALID
            assert "exists" in result.message.lower()
        finally:
            os.unlink(script_path)
    
    def test_validate_arguments_script_missing(self):
        """Test argument validation when script file is missing"""
        server = ServerConfig("test", "python", ["/nonexistent/script.py"], {})
        result = self.validator._validate_arguments(server)
        
        assert result.status == ValidationStatus.ERROR
        assert "not found" in result.message.lower()
    
    def test_validate_environment_variables_valid(self):
        """Test environment variable validation with valid variables"""
        server = ServerConfig("test", "python", [], {"PYTHONPATH": "/valid/path"})
        
        with patch('os.path.exists', return_value=True):
            result = self.validator._validate_environment_variables(server)
            
            assert result.status == ValidationStatus.VALID
    
    def test_validate_environment_variables_missing_path(self):
        """Test environment variable validation with missing path"""
        server = ServerConfig("test", "python", [], {"PYTHONPATH": "/missing/path"})
        
        with patch('os.path.exists', return_value=False):
            result = self.validator._validate_environment_variables(server)
            
            assert result.status == ValidationStatus.WARNING
            assert "does not exist" in result.message.lower()
    
    def test_validate_working_directory_exists(self):
        """Test working directory validation when directory exists"""
        with tempfile.TemporaryDirectory() as temp_dir:
            server = ServerConfig("test", "python", [], {}, working_directory=temp_dir)
            result = self.validator._validate_working_directory(server)
            
            assert result.status == ValidationStatus.VALID
            assert "exists" in result.message.lower()
    
    def test_validate_working_directory_missing(self):
        """Test working directory validation when directory is missing"""
        server = ServerConfig("test", "python", [], {}, working_directory="/nonexistent/dir")
        result = self.validator._validate_working_directory(server)
        
        assert result.status == ValidationStatus.ERROR
        assert "not found" in result.message.lower()
    
    def test_appears_to_be_http_server(self):
        """Test detection of HTTP server configurations"""
        server1 = ServerConfig("test", "python", ["server.py"], {})
        server2 = ServerConfig("test", "uvicorn", ["app:main"], {})
        server3 = ServerConfig("test", "python", ["script.py"], {})
        
        assert self.validator._appears_to_be_http_server(server1)
        assert self.validator._appears_to_be_http_server(server2)
        assert not self.validator._appears_to_be_http_server(server3)
    
    @pytest.mark.asyncio
    async def test_test_server_connectivity_success(self):
        """Test server connectivity check with success"""
        server = ServerConfig("test", "python", ["server.py", "--port=7777"], {})
        
        mock_response = Mock()
        mock_response.status = 200
        
        mock_session = Mock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            result = await self.validator._test_server_connectivity(server)
            
            assert result.status == ValidationStatus.VALID
            assert "responding" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_test_server_connectivity_timeout(self):
        """Test server connectivity check with timeout"""
        server = ServerConfig("test", "python", ["server.py"], {})
        
        with patch('aiohttp.ClientSession') as mock_session_cls:
            mock_session_cls.side_effect = asyncio.TimeoutError
            
            result = await self.validator._test_server_connectivity(server)
            
            assert result.status == ValidationStatus.WARNING
            assert "timed out" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_generate_config_recommendation(self):
        """Test configuration recommendation generation"""
        recommendation = await self.validator.generate_config_recommendation(
            ConfigType.CLAUDE_DESKTOP,
            "/path/to/server.py"
        )
        
        assert "mcpServers" in recommendation
        assert "proyecto-semilla" in recommendation["mcpServers"]
        
        server_config = recommendation["mcpServers"]["proyecto-semilla"]
        assert server_config["command"] == "/usr/bin/python3"
        assert "/path/to/server.py" in server_config["args"]
    
    def test_validate_config_syntax_valid(self):
        """Test configuration syntax validation with valid JSON"""
        config = {"mcpServers": {"test": {"command": "python"}}}
        
        result = self.validator.validate_config_syntax(config)
        
        assert result.status == ValidationStatus.VALID
        assert result.details["config"] == config
    
    def test_validate_config_syntax_invalid_json(self):
        """Test configuration syntax validation with invalid JSON string"""
        config = '{"invalid": json}'
        
        result = self.validator.validate_config_syntax(config)
        
        assert result.status == ValidationStatus.ERROR
        assert "JSON syntax" in result.message
    
    def test_get_common_issues_fixes(self):
        """Test getting common issues and their fixes"""
        issues_fixes = self.validator.get_common_issues_fixes()
        
        assert "python_not_found" in issues_fixes
        assert "script_not_found" in issues_fixes
        assert "permission_denied" in issues_fixes
        
        for issue, fix_info in issues_fixes.items():
            assert "issue" in fix_info
            assert "fix" in fix_info
            assert "example" in fix_info


class TestConfigurationGenerator:
    """Test cases for ConfigurationGenerator class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        mock_validator = Mock(spec=ConfigurationValidator)
        mock_validator.environment = Mock()
        mock_validator.environment.python_env = Mock()
        mock_validator.environment.python_env.executable = "/usr/bin/python3"
        mock_validator.environment.project_root = "/path/to/project"
        mock_validator.environment.os_type = Mock()
        mock_validator.environment.os_type.value = "macos"
        
        self.generator = ConfigurationGenerator(mock_validator)
    
    @pytest.mark.asyncio
    async def test_create_claude_desktop_config_success(self):
        """Test successful Claude Desktop configuration creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "claude_desktop_config.json")
            
            with patch.object(self.generator.validator, 'generate_config_recommendation') as mock_gen:
                mock_gen.return_value = {"mcpServers": {"test": {"command": "python"}}}
                
                success, message = await self.generator.create_claude_desktop_config(config_path)
                
                assert success
                assert config_path in message
                assert os.path.exists(config_path)
                
                # Verify config content
                with open(config_path) as f:
                    config = json.load(f)
                    assert "mcpServers" in config
    
    @pytest.mark.asyncio
    async def test_create_claude_desktop_config_backup(self):
        """Test Claude Desktop configuration creation with backup"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "claude_desktop_config.json")
            backup_path = f"{config_path}.backup"
            
            # Create existing config
            existing_config = {"existing": "config"}
            with open(config_path, 'w') as f:
                json.dump(existing_config, f)
            
            with patch.object(self.generator.validator, 'generate_config_recommendation') as mock_gen:
                mock_gen.return_value = {"mcpServers": {"test": {"command": "python"}}}
                
                success, message = await self.generator.create_claude_desktop_config(config_path, backup_existing=True)
                
                assert success
                assert os.path.exists(backup_path)
                
                # Verify backup content
                with open(backup_path) as f:
                    backup_config = json.load(f)
                    assert backup_config == existing_config
    
    @pytest.mark.asyncio
    async def test_create_claude_desktop_config_error(self):
        """Test Claude Desktop configuration creation with error"""
        config_path = "/invalid/path/config.json"
        
        success, message = await self.generator.create_claude_desktop_config(config_path)
        
        assert not success
        assert "Failed to create" in message
    
    def test_get_default_claude_config_path_macos(self):
        """Test getting default Claude config path on macOS"""
        self.generator.environment.os_type.value = "macos"
        
        path = self.generator._get_default_claude_config_path()
        
        assert path is not None
        assert "Library/Application Support/Claude" in path
    
    def test_get_default_claude_config_path_windows(self):
        """Test getting default Claude config path on Windows"""
        self.generator.environment.os_type.value = "windows"
        
        path = self.generator._get_default_claude_config_path()
        
        assert path is not None
        assert "AppData/Roaming/Claude" in path
    
    def test_get_default_claude_config_path_linux(self):
        """Test getting default Claude config path on Linux"""
        self.generator.environment.os_type.value = "linux"
        
        path = self.generator._get_default_claude_config_path()
        
        assert path is not None
        assert ".config/Claude" in path
    
    def test_get_default_claude_config_path_unknown(self):
        """Test getting default Claude config path on unknown OS"""
        self.generator.environment.os_type.value = "unknown"
        
        path = self.generator._get_default_claude_config_path()
        
        assert path is None


if __name__ == '__main__':
    pytest.main([__file__])