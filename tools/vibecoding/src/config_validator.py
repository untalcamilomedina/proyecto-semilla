"""
Configuration Validator for Vibecoding Configuration Wizard

Validates MCP server configurations, tests connections, and provides
intelligent configuration recommendations with error recovery.
"""

import os
import json
import asyncio
import aiohttp
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse

from environment_detector import SystemEnvironment, LLMClient


class ValidationStatus(Enum):
    """Validation result status"""
    VALID = "valid"
    WARNING = "warning"
    ERROR = "error"
    NOT_TESTED = "not_tested"


class ConfigType(Enum):
    """Configuration types"""
    CLAUDE_DESKTOP = "claude_desktop"
    VS_CODE = "vscode"
    CURSOR = "cursor"
    CUSTOM = "custom"


@dataclass
class ValidationResult:
    """Single validation check result"""
    check_name: str
    status: ValidationStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    fix_suggestion: Optional[str] = None


@dataclass
class ServerConfig:
    """MCP server configuration"""
    name: str
    command: str
    args: List[str]
    env: Dict[str, str]
    working_directory: Optional[str] = None


@dataclass
class ClientConfig:
    """LLM client configuration"""
    config_type: ConfigType
    config_path: str
    servers: List[ServerConfig]
    is_valid: bool = False
    validation_results: List[ValidationResult] = None


class ConfigurationValidator:
    """
    Validates MCP configurations and provides intelligent recommendations
    """
    
    def __init__(self, environment: SystemEnvironment):
        self.environment = environment
        self.timeout = 10  # Default timeout for network operations
    
    async def validate_all_configurations(self) -> List[ClientConfig]:
        """
        Validate all detected client configurations
        
        Returns:
            List of client configurations with validation results
        """
        configurations = []
        
        for client_info in self.environment.llm_clients:
            if client_info.config_path:
                config = await self._validate_client_config(client_info)
                configurations.append(config)
        
        return configurations
    
    async def _validate_client_config(self, client_info) -> ClientConfig:
        """Validate a specific client configuration"""
        config_type = self._map_client_to_config_type(client_info.client_type)
        
        # Load configuration
        servers = []
        validation_results = []
        
        try:
            servers = await self._load_server_configs(client_info.config_path, config_type)
            
            # Validate each server
            for server in servers:
                server_results = await self._validate_server_config(server)
                validation_results.extend(server_results)
            
        except Exception as e:
            validation_results.append(ValidationResult(
                check_name="config_loading",
                status=ValidationStatus.ERROR,
                message=f"Failed to load configuration: {str(e)}",
                fix_suggestion="Check configuration file format and permissions"
            ))
        
        # Overall validation status
        has_errors = any(r.status == ValidationStatus.ERROR for r in validation_results)
        is_valid = not has_errors
        
        return ClientConfig(
            config_type=config_type,
            config_path=client_info.config_path,
            servers=servers,
            is_valid=is_valid,
            validation_results=validation_results
        )
    
    async def _load_server_configs(self, config_path: str, config_type: ConfigType) -> List[ServerConfig]:
        """Load server configurations from file"""
        if not os.path.exists(config_path):
            return []
        
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            servers = []
            
            if config_type == ConfigType.CLAUDE_DESKTOP:
                mcp_servers = config_data.get('mcpServers', {})
                for name, server_config in mcp_servers.items():
                    servers.append(ServerConfig(
                        name=name,
                        command=server_config.get('command', ''),
                        args=server_config.get('args', []),
                        env=server_config.get('env', {}),
                        working_directory=server_config.get('cwd')
                    ))
            
            return servers
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            raise ValueError(f"Invalid configuration format: {str(e)}")
    
    async def _validate_server_config(self, server: ServerConfig) -> List[ValidationResult]:
        """Validate a single server configuration"""
        results = []
        
        # Validate command exists
        command_result = await self._validate_command(server)
        results.append(command_result)
        
        # Validate arguments
        args_result = self._validate_arguments(server)
        results.append(args_result)
        
        # Validate environment variables
        env_result = self._validate_environment_variables(server)
        results.append(env_result)
        
        # Validate working directory
        if server.working_directory:
            workdir_result = self._validate_working_directory(server)
            results.append(workdir_result)
        
        # Test server connectivity if it looks like an HTTP server
        if self._appears_to_be_http_server(server):
            connectivity_result = await self._test_server_connectivity(server)
            results.append(connectivity_result)
        
        return results
    
    async def _validate_command(self, server: ServerConfig) -> ValidationResult:
        """Validate server command is executable"""
        command = server.command
        
        # Handle Python commands specially
        if command == "python" or command.endswith("python"):
            try:
                result = await asyncio.create_subprocess_exec(
                    command, "--version",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await asyncio.wait_for(result.communicate(), timeout=self.timeout)
                
                if result.returncode == 0:
                    python_version = stdout.decode().strip()
                    return ValidationResult(
                        check_name="command_executable",
                        status=ValidationStatus.VALID,
                        message=f"Python command is executable ({python_version})",
                        details={"version": python_version}
                    )
                else:
                    return ValidationResult(
                        check_name="command_executable",
                        status=ValidationStatus.ERROR,
                        message=f"Python command failed: {stderr.decode().strip()}",
                        fix_suggestion="Check Python installation or use full path"
                    )
            except asyncio.TimeoutError:
                return ValidationResult(
                    check_name="command_executable",
                    status=ValidationStatus.WARNING,
                    message="Command validation timed out",
                    fix_suggestion="Command might be slow to respond"
                )
            except Exception as e:
                return ValidationResult(
                    check_name="command_executable",
                    status=ValidationStatus.ERROR,
                    message=f"Command not found or not executable: {str(e)}",
                    fix_suggestion="Install Python or provide full path to executable"
                )
        
        # Handle other commands
        if os.path.isabs(command):
            # Absolute path
            if os.path.exists(command) and os.access(command, os.X_OK):
                return ValidationResult(
                    check_name="command_executable",
                    status=ValidationStatus.VALID,
                    message="Command is executable"
                )
            else:
                return ValidationResult(
                    check_name="command_executable",
                    status=ValidationStatus.ERROR,
                    message="Command file not found or not executable",
                    fix_suggestion="Check file path and permissions"
                )
        else:
            # Command in PATH
            try:
                subprocess.run([command, "--help"], 
                             capture_output=True, timeout=5, check=False)
                return ValidationResult(
                    check_name="command_executable",
                    status=ValidationStatus.VALID,
                    message="Command found in PATH"
                )
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                return ValidationResult(
                    check_name="command_executable",
                    status=ValidationStatus.ERROR,
                    message="Command not found in PATH",
                    fix_suggestion="Install the required package or use full path"
                )
    
    def _validate_arguments(self, server: ServerConfig) -> ValidationResult:
        """Validate server arguments"""
        args = server.args
        
        # Check for required script file (common pattern)
        script_files = [arg for arg in args if arg.endswith('.py')]
        
        if script_files:
            script_path = script_files[0]
            
            # Make path relative to working directory if specified
            if server.working_directory and not os.path.isabs(script_path):
                full_path = os.path.join(server.working_directory, script_path)
            else:
                full_path = script_path
            
            if os.path.exists(full_path):
                return ValidationResult(
                    check_name="script_file",
                    status=ValidationStatus.VALID,
                    message=f"Script file exists: {script_path}",
                    details={"script_path": full_path}
                )
            else:
                return ValidationResult(
                    check_name="script_file",
                    status=ValidationStatus.ERROR,
                    message=f"Script file not found: {script_path}",
                    fix_suggestion="Check script path and working directory"
                )
        
        return ValidationResult(
            check_name="arguments",
            status=ValidationStatus.VALID,
            message="Arguments appear valid"
        )
    
    def _validate_environment_variables(self, server: ServerConfig) -> ValidationResult:
        """Validate environment variables"""
        env_vars = server.env
        issues = []
        
        for key, value in env_vars.items():
            # Check for missing environment variables that reference other env vars
            if value.startswith('$') and value[1:] not in os.environ:
                issues.append(f"Environment variable {value} is not set")
            
            # Check for file paths
            if 'PATH' in key.upper() or 'FILE' in key.upper():
                if not os.path.exists(value):
                    issues.append(f"Path {value} does not exist for {key}")
        
        if issues:
            return ValidationResult(
                check_name="environment_variables",
                status=ValidationStatus.WARNING,
                message=f"Environment issues: {'; '.join(issues)}",
                details={"issues": issues},
                fix_suggestion="Set missing environment variables or fix paths"
            )
        
        return ValidationResult(
            check_name="environment_variables",
            status=ValidationStatus.VALID,
            message="Environment variables appear valid"
        )
    
    def _validate_working_directory(self, server: ServerConfig) -> ValidationResult:
        """Validate working directory"""
        workdir = server.working_directory
        
        if os.path.exists(workdir) and os.path.isdir(workdir):
            return ValidationResult(
                check_name="working_directory",
                status=ValidationStatus.VALID,
                message=f"Working directory exists: {workdir}"
            )
        else:
            return ValidationResult(
                check_name="working_directory",
                status=ValidationStatus.ERROR,
                message=f"Working directory not found: {workdir}",
                fix_suggestion="Create directory or fix path"
            )
    
    def _appears_to_be_http_server(self, server: ServerConfig) -> bool:
        """Check if server configuration suggests it's an HTTP server"""
        # Look for indicators that this is an HTTP server
        indicators = [
            'server.py',
            'uvicorn',
            'gunicorn',
            'fastapi',
            'flask'
        ]
        
        all_args = ' '.join([server.command] + server.args).lower()
        return any(indicator in all_args for indicator in indicators)
    
    async def _test_server_connectivity(self, server: ServerConfig) -> ValidationResult:
        """Test connectivity to HTTP server"""
        # This is a simplified test - in practice, you'd need to start the server
        # or check if it's already running
        
        # Look for port or URL in arguments
        port = None
        for arg in server.args:
            if arg.isdigit() and 1000 <= int(arg) <= 65535:
                port = int(arg)
                break
            if arg.startswith('--port='):
                try:
                    port = int(arg.split('=')[1])
                except ValueError:
                    pass
        
        if not port:
            port = 7777  # Default for proyecto-semilla
        
        url = f"http://localhost:{port}/health"
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return ValidationResult(
                            check_name="server_connectivity",
                            status=ValidationStatus.VALID,
                            message=f"Server is responding at {url}",
                            details={"url": url, "status": response.status}
                        )
                    else:
                        return ValidationResult(
                            check_name="server_connectivity",
                            status=ValidationStatus.WARNING,
                            message=f"Server responded with status {response.status}",
                            details={"url": url, "status": response.status}
                        )
        except asyncio.TimeoutError:
            return ValidationResult(
                check_name="server_connectivity",
                status=ValidationStatus.WARNING,
                message=f"Connection to {url} timed out",
                fix_suggestion="Start the server or check if it's running on a different port"
            )
        except Exception as e:
            return ValidationResult(
                check_name="server_connectivity",
                status=ValidationStatus.WARNING,
                message=f"Could not connect to {url}: {str(e)}",
                fix_suggestion="Start the server or check configuration"
            )
    
    def _map_client_to_config_type(self, client_type: LLMClient) -> ConfigType:
        """Map LLM client type to configuration type"""
        mapping = {
            LLMClient.CLAUDE_DESKTOP: ConfigType.CLAUDE_DESKTOP,
            LLMClient.VS_CODE: ConfigType.VS_CODE,
            LLMClient.CURSOR: ConfigType.CURSOR,
        }
        return mapping.get(client_type, ConfigType.CUSTOM)
    
    async def generate_config_recommendation(self, 
                                           target_client: ConfigType,
                                           server_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate recommended configuration for a client
        
        Args:
            target_client: Target client type
            server_path: Optional path to MCP server script
            
        Returns:
            Dict containing recommended configuration
        """
        if not server_path and self.environment.mcp_server_status.get('server_path'):
            server_path = self.environment.mcp_server_status['server_path']
        
        if target_client == ConfigType.CLAUDE_DESKTOP:
            return await self._generate_claude_desktop_config(server_path)
        elif target_client == ConfigType.VS_CODE:
            return await self._generate_vscode_config(server_path)
        else:
            return await self._generate_generic_config(server_path)
    
    async def _generate_claude_desktop_config(self, server_path: Optional[str]) -> Dict[str, Any]:
        """Generate Claude Desktop configuration"""
        config = {
            "mcpServers": {}
        }
        
        if server_path:
            # Determine Python executable
            python_exe = self.environment.python_env.executable
            
            # Determine working directory
            server_dir = os.path.dirname(server_path)
            project_root = self.environment.project_root or server_dir
            
            config["mcpServers"]["proyecto-semilla"] = {
                "command": python_exe,
                "args": [server_path],
                "cwd": project_root,
                "env": {
                    "PYTHONPATH": project_root
                }
            }
            
            # Add environment variables if needed
            if os.path.exists(os.path.join(project_root, '.env')):
                config["mcpServers"]["proyecto-semilla"]["env"]["ENV_FILE"] = os.path.join(project_root, '.env')
        
        return config
    
    async def _generate_vscode_config(self, server_path: Optional[str]) -> Dict[str, Any]:
        """Generate VS Code configuration"""
        # VS Code MCP configuration varies by extension
        # This is a placeholder
        return {
            "mcp": {
                "servers": []
            }
        }
    
    async def _generate_generic_config(self, server_path: Optional[str]) -> Dict[str, Any]:
        """Generate generic MCP configuration"""
        return {
            "servers": []
        }
    
    def validate_config_syntax(self, config_data: Union[str, Dict]) -> ValidationResult:
        """Validate configuration syntax"""
        try:
            if isinstance(config_data, str):
                parsed = json.loads(config_data)
            else:
                parsed = config_data
                # Ensure it's JSON serializable
                json.dumps(parsed)
            
            return ValidationResult(
                check_name="config_syntax",
                status=ValidationStatus.VALID,
                message="Configuration syntax is valid",
                details={"config": parsed}
            )
            
        except json.JSONDecodeError as e:
            return ValidationResult(
                check_name="config_syntax",
                status=ValidationStatus.ERROR,
                message=f"Invalid JSON syntax: {str(e)}",
                fix_suggestion="Check JSON format - missing commas, brackets, or quotes"
            )
        except Exception as e:
            return ValidationResult(
                check_name="config_syntax",
                status=ValidationStatus.ERROR,
                message=f"Configuration error: {str(e)}",
                fix_suggestion="Check configuration structure"
            )
    
    def get_common_issues_fixes(self) -> Dict[str, Dict[str, str]]:
        """Get common configuration issues and their fixes"""
        return {
            "python_not_found": {
                "issue": "Python command not found",
                "fix": "Use full path to Python executable or install Python",
                "example": f'"{self.environment.python_env.executable}"'
            },
            "script_not_found": {
                "issue": "MCP server script not found",
                "fix": "Check script path relative to working directory",
                "example": "Use absolute path or correct relative path"
            },
            "permission_denied": {
                "issue": "Permission denied accessing files",
                "fix": "Check file permissions and ownership",
                "example": "chmod +x script.py"
            },
            "port_in_use": {
                "issue": "Server port already in use",
                "fix": "Stop existing server or use different port",
                "example": "Use --port argument to specify different port"
            },
            "missing_dependencies": {
                "issue": "Required Python packages not installed",
                "fix": "Install required packages",
                "example": "pip install -r requirements.txt"
            }
        }


class ConfigurationGenerator:
    """
    Generates new configurations based on environment and requirements
    """
    
    def __init__(self, validator: ConfigurationValidator):
        self.validator = validator
        self.environment = validator.environment
    
    async def create_claude_desktop_config(self, 
                                         config_path: Optional[str] = None,
                                         backup_existing: bool = True) -> Tuple[bool, str]:
        """
        Create or update Claude Desktop configuration
        
        Args:
            config_path: Path to configuration file (auto-detected if None)
            backup_existing: Whether to backup existing configuration
            
        Returns:
            Tuple of (success, message)
        """
        # Determine config path
        if not config_path:
            config_path = self._get_default_claude_config_path()
        
        if not config_path:
            return False, "Could not determine Claude Desktop configuration path"
        
        try:
            # Backup existing config if requested
            if backup_existing and os.path.exists(config_path):
                backup_path = f"{config_path}.backup"
                import shutil
                shutil.copy2(config_path, backup_path)
            
            # Generate recommended configuration
            recommended_config = await self.validator.generate_config_recommendation(
                ConfigType.CLAUDE_DESKTOP
            )
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # Write configuration
            with open(config_path, 'w') as f:
                json.dump(recommended_config, f, indent=2)
            
            return True, f"Configuration created at {config_path}"
            
        except Exception as e:
            return False, f"Failed to create configuration: {str(e)}"
    
    def _get_default_claude_config_path(self) -> Optional[str]:
        """Get default Claude Desktop configuration path"""
        if self.environment.os_type.value == "macos":
            return os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
        elif self.environment.os_type.value == "windows":
            return os.path.expanduser("~/AppData/Roaming/Claude/claude_desktop_config.json")
        elif self.environment.os_type.value == "linux":
            return os.path.expanduser("~/.config/Claude/claude_desktop_config.json")
        return None