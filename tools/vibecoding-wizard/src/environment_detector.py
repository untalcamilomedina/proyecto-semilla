"""
Environment Detection System for Vibecoding Configuration Wizard

Automatically detects OS, Python environment, existing MCP installations,
and system configurations to provide intelligent setup recommendations.
"""

import os
import sys
import json
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class OSType(Enum):
    """Supported operating systems"""
    MACOS = "macos"
    WINDOWS = "windows"
    LINUX = "linux"
    UNKNOWN = "unknown"


class LLMClient(Enum):
    """Supported LLM clients"""
    CLAUDE_DESKTOP = "claude_desktop"
    CURSOR = "cursor"
    VS_CODE = "vscode"
    CUSTOM = "custom"


@dataclass
class PythonEnvironment:
    """Python environment information"""
    version: str
    executable: str
    is_virtual_env: bool
    virtual_env_path: Optional[str]
    has_pip: bool
    pip_version: Optional[str]


@dataclass
class MCPInstallation:
    """MCP installation information"""
    is_installed: bool
    version: Optional[str]
    installation_path: Optional[str]
    config_path: Optional[str]
    servers: List[Dict[str, Any]]


@dataclass
class LLMClientInfo:
    """LLM client information"""
    client_type: LLMClient
    is_installed: bool
    installation_path: Optional[str]
    config_path: Optional[str]
    version: Optional[str]


@dataclass
class SystemEnvironment:
    """Complete system environment information"""
    os_type: OSType
    os_version: str
    architecture: str
    python_env: PythonEnvironment
    mcp_installation: MCPInstallation
    llm_clients: List[LLMClientInfo]
    project_root: Optional[str]
    mcp_server_status: Dict[str, Any]


class EnvironmentDetector:
    """
    Detects and analyzes the system environment for MCP configuration
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize environment detector
        
        Args:
            project_root: Optional path to project root (auto-detected if None)
        """
        self.project_root = project_root or self._detect_project_root()
        
    def detect_full_environment(self) -> SystemEnvironment:
        """
        Perform complete environment detection
        
        Returns:
            SystemEnvironment: Complete system environment information
        """
        return SystemEnvironment(
            os_type=self._detect_os(),
            os_version=self._get_os_version(),
            architecture=platform.machine(),
            python_env=self._detect_python_environment(),
            mcp_installation=self._detect_mcp_installation(),
            llm_clients=self._detect_llm_clients(),
            project_root=self.project_root,
            mcp_server_status=self._check_mcp_server_status()
        )
    
    def _detect_os(self) -> OSType:
        """Detect operating system"""
        system = platform.system().lower()
        
        if system == "darwin":
            return OSType.MACOS
        elif system == "windows":
            return OSType.WINDOWS
        elif system == "linux":
            return OSType.LINUX
        else:
            return OSType.UNKNOWN
    
    def _get_os_version(self) -> str:
        """Get detailed OS version"""
        try:
            return platform.platform()
        except Exception:
            return "Unknown"
    
    def _detect_python_environment(self) -> PythonEnvironment:
        """Detect Python environment details"""
        python_exe = sys.executable
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        # Check if in virtual environment
        is_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        venv_path = None
        if is_venv:
            venv_path = os.environ.get('VIRTUAL_ENV') or sys.prefix
        
        # Check pip availability
        has_pip = self._check_command_availability('pip')
        pip_version = None
        
        if has_pip:
            try:
                result = subprocess.run([python_exe, '-m', 'pip', '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    pip_version = result.stdout.strip().split()[1]
            except Exception:
                pass
        
        return PythonEnvironment(
            version=python_version,
            executable=python_exe,
            is_virtual_env=is_venv,
            virtual_env_path=venv_path,
            has_pip=has_pip,
            pip_version=pip_version
        )
    
    def _detect_mcp_installation(self) -> MCPInstallation:
        """Detect MCP installation and configuration"""
        # Check if MCP is installed via pip
        is_installed = False
        version = None
        installation_path = None
        
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'show', 'mcp'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                is_installed = True
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.startswith('Version:'):
                        version = line.split(':', 1)[1].strip()
                    elif line.startswith('Location:'):
                        installation_path = line.split(':', 1)[1].strip()
        except Exception:
            pass
        
        # Find MCP configuration files
        config_path = self._find_mcp_config()
        servers = self._parse_mcp_servers(config_path)
        
        return MCPInstallation(
            is_installed=is_installed,
            version=version,
            installation_path=installation_path,
            config_path=config_path,
            servers=servers
        )
    
    def _detect_llm_clients(self) -> List[LLMClientInfo]:
        """Detect installed LLM clients"""
        clients = []
        
        # Detect Claude Desktop
        claude_info = self._detect_claude_desktop()
        if claude_info:
            clients.append(claude_info)
        
        # Detect Cursor
        cursor_info = self._detect_cursor()
        if cursor_info:
            clients.append(cursor_info)
        
        # Detect VS Code
        vscode_info = self._detect_vscode()
        if vscode_info:
            clients.append(vscode_info)
        
        return clients
    
    def _detect_claude_desktop(self) -> Optional[LLMClientInfo]:
        """Detect Claude Desktop installation"""
        os_type = self._detect_os()
        
        if os_type == OSType.MACOS:
            app_path = "/Applications/Claude.app"
            config_path = os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
        elif os_type == OSType.WINDOWS:
            app_path = os.path.expanduser("~/AppData/Local/Programs/Claude/Claude.exe")
            config_path = os.path.expanduser("~/AppData/Roaming/Claude/claude_desktop_config.json")
        else:
            # Linux paths may vary
            app_path = None
            config_path = os.path.expanduser("~/.config/Claude/claude_desktop_config.json")
        
        is_installed = False
        version = None
        
        if app_path and os.path.exists(app_path):
            is_installed = True
            # Try to get version info
            try:
                # Version detection would be client-specific
                version = self._get_claude_desktop_version(app_path)
            except Exception:
                pass
        
        # Check if config exists even if app is not found
        if os.path.exists(config_path):
            is_installed = True
        
        if is_installed:
            return LLMClientInfo(
                client_type=LLMClient.CLAUDE_DESKTOP,
                is_installed=is_installed,
                installation_path=app_path if app_path and os.path.exists(app_path) else None,
                config_path=config_path if os.path.exists(config_path) else None,
                version=version
            )
        
        return None
    
    def _detect_cursor(self) -> Optional[LLMClientInfo]:
        """Detect Cursor installation"""
        # Cursor detection logic would go here
        # This is a placeholder for now
        return None
    
    def _detect_vscode(self) -> Optional[LLMClientInfo]:
        """Detect VS Code installation"""
        is_installed = self._check_command_availability('code')
        
        if is_installed:
            version = None
            try:
                result = subprocess.run(['code', '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
            except Exception:
                pass
            
            return LLMClientInfo(
                client_type=LLMClient.VS_CODE,
                is_installed=True,
                installation_path=None,  # VS Code path detection is complex
                config_path=None,  # VS Code MCP config varies by extension
                version=version
            )
        
        return None
    
    def _find_mcp_config(self) -> Optional[str]:
        """Find MCP configuration file"""
        possible_paths = [
            os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json"),  # macOS
            os.path.expanduser("~/AppData/Roaming/Claude/claude_desktop_config.json"),  # Windows
            os.path.expanduser("~/.config/Claude/claude_desktop_config.json"),  # Linux
            os.path.expanduser("~/.claude_desktop_config.json"),  # Alternative
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _parse_mcp_servers(self, config_path: Optional[str]) -> List[Dict[str, Any]]:
        """Parse MCP servers from configuration file"""
        if not config_path or not os.path.exists(config_path):
            return []
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            servers = config.get('mcpServers', {})
            return [
                {
                    'name': name,
                    'command': server.get('command'),
                    'args': server.get('args', []),
                    'env': server.get('env', {})
                }
                for name, server in servers.items()
            ]
        except Exception:
            return []
    
    def _check_mcp_server_status(self) -> Dict[str, Any]:
        """Check if the project's MCP server is running"""
        status = {
            'is_running': False,
            'url': 'http://localhost:7777',
            'server_path': None,
            'last_check': None
        }
        
        if self.project_root:
            server_path = os.path.join(self.project_root, 'mcp', 'server.py')
            if os.path.exists(server_path):
                status['server_path'] = server_path
        
        # Try to check if server is running
        try:
            import requests
            response = requests.get(status['url'] + '/health', timeout=5)
            if response.status_code == 200:
                status['is_running'] = True
                status['last_check'] = 'success'
        except Exception as e:
            status['last_check'] = str(e)
        
        return status
    
    def _detect_project_root(self) -> Optional[str]:
        """Auto-detect project root directory"""
        # Start from current working directory and look for project indicators
        current = Path.cwd()
        
        # Look for common project indicators
        indicators = [
            'mcp/server.py',
            'proyecto-semilla',
            'requirements.txt',
            'setup.py',
            'pyproject.toml',
            '.git'
        ]
        
        # Check current directory and parents
        for path in [current] + list(current.parents):
            for indicator in indicators:
                if (path / indicator).exists():
                    return str(path)
        
        return None
    
    def _check_command_availability(self, command: str) -> bool:
        """Check if a command is available in PATH"""
        try:
            subprocess.run([command, '--version'], 
                         capture_output=True, timeout=10)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _get_claude_desktop_version(self, app_path: str) -> Optional[str]:
        """Get Claude Desktop version (macOS specific)"""
        if not app_path.endswith('.app'):
            return None
        
        plist_path = os.path.join(app_path, 'Contents', 'Info.plist')
        if not os.path.exists(plist_path):
            return None
        
        try:
            import plistlib
            with open(plist_path, 'rb') as f:
                plist = plistlib.load(f)
            return plist.get('CFBundleShortVersionString')
        except Exception:
            return None


class EnvironmentAnalyzer:
    """
    Analyzes detected environment and provides recommendations
    """
    
    def __init__(self, environment: SystemEnvironment):
        self.environment = environment
    
    def analyze_compatibility(self) -> Dict[str, Any]:
        """
        Analyze environment compatibility and provide recommendations
        
        Returns:
            Dict containing analysis results and recommendations
        """
        analysis = {
            'compatibility_score': 0,
            'issues': [],
            'recommendations': [],
            'requirements_met': [],
            'missing_requirements': []
        }
        
        # Check Python version
        if self._check_python_compatibility():
            analysis['requirements_met'].append('Python version >= 3.8')
            analysis['compatibility_score'] += 20
        else:
            analysis['issues'].append('Python version too old (requires 3.8+)')
            analysis['recommendations'].append('Upgrade Python to 3.8 or newer')
        
        # Check pip availability
        if self.environment.python_env.has_pip:
            analysis['requirements_met'].append('pip package manager')
            analysis['compatibility_score'] += 10
        else:
            analysis['issues'].append('pip not available')
            analysis['recommendations'].append('Install pip package manager')
        
        # Check virtual environment
        if self.environment.python_env.is_virtual_env:
            analysis['requirements_met'].append('Virtual environment active')
            analysis['compatibility_score'] += 15
        else:
            analysis['recommendations'].append('Consider using a virtual environment for isolation')
        
        # Check MCP installation
        if self.environment.mcp_installation.is_installed:
            analysis['requirements_met'].append('MCP library installed')
            analysis['compatibility_score'] += 25
        else:
            analysis['missing_requirements'].append('MCP library')
            analysis['recommendations'].append('Install MCP library: pip install mcp')
        
        # Check LLM clients
        if self.environment.llm_clients:
            analysis['requirements_met'].append(f'{len(self.environment.llm_clients)} LLM client(s) detected')
            analysis['compatibility_score'] += 20
        else:
            analysis['issues'].append('No supported LLM clients detected')
            analysis['recommendations'].append('Install Claude Desktop or another supported LLM client')
        
        # Check project MCP server
        if self.environment.mcp_server_status.get('server_path'):
            analysis['requirements_met'].append('Project MCP server found')
            analysis['compatibility_score'] += 10
            
            if self.environment.mcp_server_status.get('is_running'):
                analysis['requirements_met'].append('MCP server is running')
            else:
                analysis['recommendations'].append('Start the MCP server for testing')
        
        return analysis
    
    def _check_python_compatibility(self) -> bool:
        """Check if Python version is compatible"""
        version_parts = self.environment.python_env.version.split('.')
        try:
            major = int(version_parts[0])
            minor = int(version_parts[1])
            return major > 3 or (major == 3 and minor >= 8)
        except (ValueError, IndexError):
            return False
    
    def get_setup_recommendations(self) -> List[Dict[str, str]]:
        """
        Get prioritized setup recommendations
        
        Returns:
            List of recommendations with priority and instructions
        """
        recommendations = []
        
        # High priority: Python and pip
        if not self._check_python_compatibility():
            recommendations.append({
                'priority': 'HIGH',
                'title': 'Upgrade Python',
                'description': 'Python 3.8+ is required for MCP functionality',
                'action': 'Install Python 3.8+ from python.org'
            })
        
        if not self.environment.python_env.has_pip:
            recommendations.append({
                'priority': 'HIGH',
                'title': 'Install pip',
                'description': 'pip is required to install Python packages',
                'action': 'Install pip: python -m ensurepip --upgrade'
            })
        
        # Medium priority: MCP library
        if not self.environment.mcp_installation.is_installed:
            recommendations.append({
                'priority': 'MEDIUM',
                'title': 'Install MCP library',
                'description': 'MCP library is required for server functionality',
                'action': 'Run: pip install mcp'
            })
        
        # Medium priority: LLM client
        if not self.environment.llm_clients:
            recommendations.append({
                'priority': 'MEDIUM',
                'title': 'Install LLM Client',
                'description': 'An LLM client is needed to use MCP servers',
                'action': 'Download Claude Desktop from claude.ai'
            })
        
        # Low priority: Virtual environment
        if not self.environment.python_env.is_virtual_env:
            recommendations.append({
                'priority': 'LOW',
                'title': 'Use Virtual Environment',
                'description': 'Virtual environments provide better isolation',
                'action': 'Create venv: python -m venv venv && source venv/bin/activate'
            })
        
        return recommendations