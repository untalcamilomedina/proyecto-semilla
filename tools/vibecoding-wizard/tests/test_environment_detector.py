"""
Unit tests for Environment Detection System
"""

import os
import sys
import json
import tempfile
import platform
import pytest
from unittest.mock import Mock, patch, mock_open, MagicMock
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from environment_detector import (
    EnvironmentDetector, 
    SystemEnvironment, 
    EnvironmentAnalyzer,
    OSType, 
    LLMClient, 
    PythonEnvironment,
    MCPInstallation,
    LLMClientInfo
)


class TestEnvironmentDetector:
    """Test cases for EnvironmentDetector class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.detector = EnvironmentDetector()
    
    def test_detect_os_macos(self):
        """Test macOS detection"""
        with patch('platform.system', return_value='Darwin'):
            assert self.detector._detect_os() == OSType.MACOS
    
    def test_detect_os_windows(self):
        """Test Windows detection"""
        with patch('platform.system', return_value='Windows'):
            assert self.detector._detect_os() == OSType.WINDOWS
    
    def test_detect_os_linux(self):
        """Test Linux detection"""
        with patch('platform.system', return_value='Linux'):
            assert self.detector._detect_os() == OSType.LINUX
    
    def test_detect_os_unknown(self):
        """Test unknown OS detection"""
        with patch('platform.system', return_value='FreeBSD'):
            assert self.detector._detect_os() == OSType.UNKNOWN
    
    def test_get_os_version(self):
        """Test OS version detection"""
        with patch('platform.platform', return_value='macOS-12.0-arm64'):
            version = self.detector._get_os_version()
            assert version == 'macOS-12.0-arm64'
    
    def test_detect_python_environment(self):
        """Test Python environment detection"""
        python_env = self.detector._detect_python_environment()
        
        assert isinstance(python_env, PythonEnvironment)
        assert python_env.version is not None
        assert python_env.executable is not None
        assert isinstance(python_env.is_virtual_env, bool)
        assert isinstance(python_env.has_pip, bool)
    
    @patch('subprocess.run')
    def test_detect_python_environment_with_pip(self, mock_run):
        """Test Python environment detection with pip"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "pip 21.0.0"
        
        python_env = self.detector._detect_python_environment()
        
        assert python_env.has_pip
        assert python_env.pip_version == "21.0.0"
    
    @patch('subprocess.run')
    def test_detect_mcp_installation_installed(self, mock_run):
        """Test MCP installation detection when installed"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Version: 1.0.0\nLocation: /path/to/mcp"
        
        mcp_install = self.detector._detect_mcp_installation()
        
        assert mcp_install.is_installed
        assert mcp_install.version == "1.0.0"
        assert mcp_install.installation_path == "/path/to/mcp"
    
    @patch('subprocess.run')
    def test_detect_mcp_installation_not_installed(self, mock_run):
        """Test MCP installation detection when not installed"""
        mock_run.return_value.returncode = 1
        
        mcp_install = self.detector._detect_mcp_installation()
        
        assert not mcp_install.is_installed
        assert mcp_install.version is None
        assert mcp_install.installation_path is None
    
    @patch('os.path.exists')
    def test_detect_claude_desktop_macos(self, mock_exists):
        """Test Claude Desktop detection on macOS"""
        with patch.object(self.detector, '_detect_os', return_value=OSType.MACOS):
            mock_exists.return_value = True
            
            client_info = self.detector._detect_claude_desktop()
            
            assert client_info is not None
            assert client_info.client_type == LLMClient.CLAUDE_DESKTOP
            assert client_info.is_installed
    
    @patch('os.path.exists')
    def test_detect_claude_desktop_not_installed(self, mock_exists):
        """Test Claude Desktop detection when not installed"""
        with patch.object(self.detector, '_detect_os', return_value=OSType.MACOS):
            mock_exists.return_value = False
            
            client_info = self.detector._detect_claude_desktop()
            
            assert client_info is None
    
    @patch('subprocess.run')
    def test_detect_vscode_installed(self, mock_run):
        """Test VS Code detection when installed"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "1.70.0"
        
        with patch.object(self.detector, '_check_command_availability', return_value=True):
            client_info = self.detector._detect_vscode()
            
            assert client_info is not None
            assert client_info.client_type == LLMClient.VS_CODE
            assert client_info.is_installed
            assert client_info.version == "1.70.0"
    
    def test_find_mcp_config_exists(self):
        """Test MCP config file detection when file exists"""
        with tempfile.NamedTemporaryFile(suffix='claude_desktop_config.json', delete=False) as f:
            config_path = f.name
            f.write(b'{"mcpServers": {}}')
        
        try:
            with patch('os.path.expanduser', return_value=config_path):
                found_path = self.detector._find_mcp_config()
                assert found_path == config_path
        finally:
            os.unlink(config_path)
    
    def test_find_mcp_config_not_exists(self):
        """Test MCP config file detection when no file exists"""
        with patch('os.path.exists', return_value=False):
            found_path = self.detector._find_mcp_config()
            assert found_path is None
    
    def test_parse_mcp_servers(self):
        """Test parsing MCP servers from config file"""
        config_data = {
            "mcpServers": {
                "test-server": {
                    "command": "python",
                    "args": ["server.py"],
                    "env": {"TEST_VAR": "value"}
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        try:
            servers = self.detector._parse_mcp_servers(config_path)
            
            assert len(servers) == 1
            assert servers[0]['name'] == 'test-server'
            assert servers[0]['command'] == 'python'
            assert servers[0]['args'] == ['server.py']
            assert servers[0]['env'] == {'TEST_VAR': 'value'}
        finally:
            os.unlink(config_path)
    
    @patch('requests.get')
    def test_check_mcp_server_status_running(self, mock_get):
        """Test MCP server status check when server is running"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        status = self.detector._check_mcp_server_status()
        
        assert status['is_running']
        assert status['last_check'] == 'success'
    
    @patch('requests.get')
    def test_check_mcp_server_status_not_running(self, mock_get):
        """Test MCP server status check when server is not running"""
        mock_get.side_effect = Exception("Connection refused")
        
        status = self.detector._check_mcp_server_status()
        
        assert not status['is_running']
        assert 'Connection refused' in status['last_check']
    
    def test_detect_project_root(self):
        """Test project root detection"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock project structure
            mcp_dir = os.path.join(temp_dir, 'mcp')
            os.makedirs(mcp_dir)
            server_path = os.path.join(mcp_dir, 'server.py')
            Path(server_path).touch()
            
            with patch('pathlib.Path.cwd', return_value=Path(temp_dir)):
                detector = EnvironmentDetector()
                root = detector._detect_project_root()
                
                assert root == temp_dir
    
    def test_check_command_availability(self):
        """Test command availability check"""
        # Test with a command that should exist (python)
        assert self.detector._check_command_availability('python')
        
        # Test with a command that shouldn't exist
        assert not self.detector._check_command_availability('nonexistent_command_12345')
    
    def test_detect_full_environment(self):
        """Test complete environment detection"""
        environment = self.detector.detect_full_environment()
        
        assert isinstance(environment, SystemEnvironment)
        assert isinstance(environment.os_type, OSType)
        assert environment.os_version is not None
        assert environment.architecture is not None
        assert isinstance(environment.python_env, PythonEnvironment)
        assert isinstance(environment.mcp_installation, MCPInstallation)
        assert isinstance(environment.llm_clients, list)
        assert isinstance(environment.mcp_server_status, dict)


class TestEnvironmentAnalyzer:
    """Test cases for EnvironmentAnalyzer class"""
    
    def create_mock_environment(self, **overrides):
        """Create a mock environment for testing"""
        defaults = {
            'os_type': OSType.MACOS,
            'os_version': 'macOS-12.0',
            'architecture': 'arm64',
            'python_env': PythonEnvironment(
                version='3.9.0',
                executable='/usr/bin/python3',
                is_virtual_env=True,
                virtual_env_path='/path/to/venv',
                has_pip=True,
                pip_version='21.0.0'
            ),
            'mcp_installation': MCPInstallation(
                is_installed=True,
                version='1.0.0',
                installation_path='/path/to/mcp',
                config_path=None,
                servers=[]
            ),
            'llm_clients': [
                LLMClientInfo(
                    client_type=LLMClient.CLAUDE_DESKTOP,
                    is_installed=True,
                    installation_path='/Applications/Claude.app',
                    config_path='/path/to/config.json',
                    version='1.0.0'
                )
            ],
            'project_root': '/path/to/project',
            'mcp_server_status': {
                'is_running': True,
                'server_path': '/path/to/server.py'
            }
        }
        
        defaults.update(overrides)
        return SystemEnvironment(**defaults)
    
    def test_analyze_compatibility_perfect_environment(self):
        """Test compatibility analysis with perfect environment"""
        environment = self.create_mock_environment()
        analyzer = EnvironmentAnalyzer(environment)
        
        analysis = analyzer.analyze_compatibility()
        
        assert analysis['compatibility_score'] == 100
        assert len(analysis['issues']) == 0
        assert len(analysis['requirements_met']) > 0
    
    def test_analyze_compatibility_old_python(self):
        """Test compatibility analysis with old Python version"""
        python_env = PythonEnvironment(
            version='3.7.0',
            executable='/usr/bin/python3',
            is_virtual_env=False,
            virtual_env_path=None,
            has_pip=True,
            pip_version='21.0.0'
        )
        
        environment = self.create_mock_environment(python_env=python_env)
        analyzer = EnvironmentAnalyzer(environment)
        
        analysis = analyzer.analyze_compatibility()
        
        assert analysis['compatibility_score'] < 100
        assert any('Python version too old' in issue for issue in analysis['issues'])
    
    def test_analyze_compatibility_no_pip(self):
        """Test compatibility analysis without pip"""
        python_env = PythonEnvironment(
            version='3.9.0',
            executable='/usr/bin/python3',
            is_virtual_env=False,
            virtual_env_path=None,
            has_pip=False,
            pip_version=None
        )
        
        environment = self.create_mock_environment(python_env=python_env)
        analyzer = EnvironmentAnalyzer(environment)
        
        analysis = analyzer.analyze_compatibility()
        
        assert analysis['compatibility_score'] < 100
        assert any('pip not available' in issue for issue in analysis['issues'])
    
    def test_analyze_compatibility_no_mcp(self):
        """Test compatibility analysis without MCP installed"""
        mcp_installation = MCPInstallation(
            is_installed=False,
            version=None,
            installation_path=None,
            config_path=None,
            servers=[]
        )
        
        environment = self.create_mock_environment(mcp_installation=mcp_installation)
        analyzer = EnvironmentAnalyzer(environment)
        
        analysis = analyzer.analyze_compatibility()
        
        assert analysis['compatibility_score'] < 100
        assert 'MCP library' in analysis['missing_requirements']
    
    def test_analyze_compatibility_no_llm_clients(self):
        """Test compatibility analysis without LLM clients"""
        environment = self.create_mock_environment(llm_clients=[])
        analyzer = EnvironmentAnalyzer(environment)
        
        analysis = analyzer.analyze_compatibility()
        
        assert analysis['compatibility_score'] < 100
        assert any('No supported LLM clients' in issue for issue in analysis['issues'])
    
    def test_check_python_compatibility_valid(self):
        """Test Python version compatibility check with valid version"""
        environment = self.create_mock_environment()
        analyzer = EnvironmentAnalyzer(environment)
        
        assert analyzer._check_python_compatibility()
    
    def test_check_python_compatibility_invalid(self):
        """Test Python version compatibility check with invalid version"""
        python_env = PythonEnvironment(
            version='3.7.0',
            executable='/usr/bin/python3',
            is_virtual_env=False,
            virtual_env_path=None,
            has_pip=True,
            pip_version='21.0.0'
        )
        
        environment = self.create_mock_environment(python_env=python_env)
        analyzer = EnvironmentAnalyzer(environment)
        
        assert not analyzer._check_python_compatibility()
    
    def test_get_setup_recommendations(self):
        """Test setup recommendations generation"""
        # Environment with some issues
        python_env = PythonEnvironment(
            version='3.7.0',  # Old version
            executable='/usr/bin/python3',
            is_virtual_env=False,  # No venv
            virtual_env_path=None,
            has_pip=False,  # No pip
            pip_version=None
        )
        
        environment = self.create_mock_environment(
            python_env=python_env,
            llm_clients=[]  # No LLM clients
        )
        analyzer = EnvironmentAnalyzer(environment)
        
        recommendations = analyzer.get_setup_recommendations()
        
        # Should have recommendations for multiple issues
        assert len(recommendations) > 0
        
        # Check for high priority recommendations
        high_priority = [r for r in recommendations if r['priority'] == 'HIGH']
        assert len(high_priority) > 0
        
        # Should recommend Python upgrade and pip installation
        rec_titles = [r['title'] for r in recommendations]
        assert any('Python' in title for title in rec_titles)
        assert any('pip' in title for title in rec_titles)


if __name__ == '__main__':
    pytest.main([__file__])