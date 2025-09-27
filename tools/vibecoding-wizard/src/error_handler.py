"""
Error Handling and Recovery System for Vibecoding Configuration Wizard

Provides comprehensive error handling, recovery strategies, and user-friendly
error messages for all components of the configuration wizard.
"""

import os
import sys
import json
import logging
import traceback
from typing import Dict, List, Optional, Any, Callable, Type, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import subprocess
import asyncio
from contextlib import asynccontextmanager, contextmanager


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better handling"""
    SYSTEM = "system"
    NETWORK = "network"
    PERMISSION = "permission"
    CONFIGURATION = "configuration"
    VALIDATION = "validation"
    USER_INPUT = "user_input"
    DEPENDENCY = "dependency"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Context information for errors"""
    operation: str
    component: str
    user_action: Optional[str] = None
    system_info: Optional[Dict[str, Any]] = None
    additional_data: Optional[Dict[str, Any]] = None


@dataclass
class RecoveryAction:
    """Represents a recovery action for an error"""
    name: str
    description: str
    action: Callable[[], Any]
    is_automatic: bool = False
    requires_confirmation: bool = True


@dataclass
class WizardError:
    """Comprehensive error information"""
    error_type: str
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    user_message: str
    context: Optional[ErrorContext] = None
    original_exception: Optional[Exception] = None
    recovery_actions: List[RecoveryAction] = None
    troubleshooting_steps: List[str] = None
    related_docs: List[str] = None


class ErrorRegistry:
    """Registry of known errors and their recovery strategies"""
    
    def __init__(self):
        self.known_errors = {}
        self._register_common_errors()
    
    def register_error(self, error_pattern: str, error_info: WizardError):
        """Register a known error pattern"""
        self.known_errors[error_pattern] = error_info
    
    def find_error(self, exception: Exception) -> Optional[WizardError]:
        """Find matching error pattern for an exception"""
        error_str = str(exception).lower()
        exception_type = type(exception).__name__
        
        # Try exact type match first
        if exception_type in self.known_errors:
            return self.known_errors[exception_type]
        
        # Try pattern matching
        for pattern, error_info in self.known_errors.items():
            if pattern in error_str or pattern in exception_type.lower():
                # Create a copy with the actual exception
                error_copy = WizardError(
                    error_type=error_info.error_type,
                    severity=error_info.severity,
                    category=error_info.category,
                    message=error_info.message,
                    user_message=error_info.user_message,
                    context=error_info.context,
                    original_exception=exception,
                    recovery_actions=error_info.recovery_actions,
                    troubleshooting_steps=error_info.troubleshooting_steps,
                    related_docs=error_info.related_docs
                )
                return error_copy
        
        return None
    
    def _register_common_errors(self):
        """Register common error patterns and their recovery strategies"""
        
        # Python/System Errors
        self.register_error("filenotfounderror", WizardError(
            error_type="FileNotFoundError",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SYSTEM,
            message="Required file not found",
            user_message="A required file could not be found. This might be due to an incorrect path or missing installation.",
            recovery_actions=[
                RecoveryAction("check_path", "Verify the file path exists", lambda: None),
                RecoveryAction("install_missing", "Install missing components", lambda: None)
            ],
            troubleshooting_steps=[
                "Check if the file path is correct",
                "Verify the file hasn't been moved or deleted",
                "Ensure you have the required permissions",
                "Try using an absolute path instead of relative"
            ]
        ))
        
        self.register_error("permissionerror", WizardError(
            error_type="PermissionError",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.PERMISSION,
            message="Permission denied",
            user_message="You don't have permission to access this file or directory.",
            recovery_actions=[
                RecoveryAction("fix_permissions", "Fix file permissions", lambda: None),
                RecoveryAction("run_as_admin", "Run as administrator", lambda: None)
            ],
            troubleshooting_steps=[
                "Check file and directory permissions",
                "Try running as administrator/sudo",
                "Ensure you own the files you're trying to modify",
                "Check if files are being used by another process"
            ]
        ))
        
        # Network Errors
        self.register_error("connectionerror", WizardError(
            error_type="ConnectionError",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.NETWORK,
            message="Network connection failed",
            user_message="Could not establish a network connection. Check your internet connection and server status.",
            recovery_actions=[
                RecoveryAction("retry_connection", "Retry connection", lambda: None),
                RecoveryAction("check_firewall", "Check firewall settings", lambda: None)
            ],
            troubleshooting_steps=[
                "Check your internet connection",
                "Verify the server is running",
                "Check firewall and proxy settings",
                "Try using a different port or URL"
            ]
        ))
        
        # Configuration Errors
        self.register_error("json.decoder.jsondecodeerror", WizardError(
            error_type="JSONDecodeError",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.CONFIGURATION,
            message="Invalid JSON configuration",
            user_message="The configuration file contains invalid JSON syntax.",
            recovery_actions=[
                RecoveryAction("fix_json", "Fix JSON syntax", lambda: None),
                RecoveryAction("recreate_config", "Recreate configuration", lambda: None)
            ],
            troubleshooting_steps=[
                "Check for missing commas, brackets, or quotes",
                "Validate JSON syntax using an online validator",
                "Look for trailing commas or extra characters",
                "Ensure proper escaping of special characters"
            ]
        ))
        
        # Python Environment Errors
        self.register_error("modulenotfounderror", WizardError(
            error_type="ModuleNotFoundError",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.DEPENDENCY,
            message="Required Python module not found",
            user_message="A required Python package is not installed.",
            recovery_actions=[
                RecoveryAction("install_package", "Install missing package", lambda: None),
                RecoveryAction("check_virtual_env", "Activate virtual environment", lambda: None)
            ],
            troubleshooting_steps=[
                "Install the missing package with pip",
                "Check if you're in the correct virtual environment",
                "Verify your Python path is correct",
                "Try upgrading pip and setuptools"
            ]
        ))
        
        # Timeout Errors
        self.register_error("timeouterror", WizardError(
            error_type="TimeoutError",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.NETWORK,
            message="Operation timed out",
            user_message="The operation took too long to complete.",
            recovery_actions=[
                RecoveryAction("increase_timeout", "Increase timeout", lambda: None),
                RecoveryAction("check_performance", "Check system performance", lambda: None)
            ],
            troubleshooting_steps=[
                "Check your network connection speed",
                "Verify the server is responding",
                "Try increasing the timeout value",
                "Check if system is under heavy load"
            ]
        ))


class ErrorHandler:
    """Main error handler with recovery capabilities"""
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.error_registry = ErrorRegistry()
        self.logger = self._setup_logger()
        self.recovery_enabled = True
        
    def _setup_logger(self) -> logging.Logger:
        """Set up error logging"""
        logger = logging.getLogger("vibecoding_wizard")
        logger.setLevel(logging.DEBUG if self.debug_mode else logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path.home() / ".vibecoding_wizard" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # File handler
        log_file = log_dir / "wizard_errors.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler for debug mode
        if self.debug_mode:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # Formatter for file
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    @contextmanager
    def handle_errors(self, 
                     operation: str, 
                     component: str = "wizard",
                     user_action: Optional[str] = None,
                     suppress_errors: bool = False):
        """Context manager for comprehensive error handling"""
        context = ErrorContext(
            operation=operation,
            component=component,
            user_action=user_action,
            system_info=self._get_system_info()
        )
        
        try:
            yield
        except Exception as e:
            self.logger.error(f"Error in {operation}: {str(e)}", exc_info=True)
            
            if not suppress_errors:
                self._handle_exception(e, context)
            else:
                # Still log but don't show to user
                pass
    
    @asynccontextmanager
    async def handle_async_errors(self,
                                 operation: str,
                                 component: str = "wizard",
                                 user_action: Optional[str] = None):
        """Async context manager for error handling"""
        context = ErrorContext(
            operation=operation,
            component=component,
            user_action=user_action,
            system_info=self._get_system_info()
        )
        
        try:
            yield
        except Exception as e:
            self.logger.error(f"Async error in {operation}: {str(e)}", exc_info=True)
            self._handle_exception(e, context)
    
    def _handle_exception(self, exception: Exception, context: ErrorContext):
        """Handle a specific exception with recovery"""
        # Find known error pattern
        wizard_error = self.error_registry.find_error(exception)
        
        if not wizard_error:
            # Create generic error
            wizard_error = WizardError(
                error_type=type(exception).__name__,
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.UNKNOWN,
                message=str(exception),
                user_message=f"An unexpected error occurred: {str(exception)}",
                original_exception=exception,
                troubleshooting_steps=[
                    "Try running the operation again",
                    "Check system requirements",
                    "Enable debug mode for more information"
                ]
            )
        
        wizard_error.context = context
        
        # Display error to user
        self._display_error(wizard_error)
        
        # Attempt recovery if enabled
        if self.recovery_enabled and wizard_error.recovery_actions:
            self._attempt_recovery(wizard_error)
        
        # Re-raise if critical
        if wizard_error.severity == ErrorSeverity.CRITICAL:
            raise exception
    
    def _display_error(self, error: WizardError):
        """Display user-friendly error message"""
        from .cli_interface import print_error, print_warning, print_info, Colors, colorize, Icons
        
        # Error message
        if error.severity == ErrorSeverity.CRITICAL:
            print_error(f"{Icons.CROSS} CRITICAL ERROR: {error.user_message}")
        elif error.severity == ErrorSeverity.HIGH:
            print_error(f"{Icons.CROSS} ERROR: {error.user_message}")
        elif error.severity == ErrorSeverity.MEDIUM:
            print_warning(f"{Icons.WARNING} WARNING: {error.user_message}")
        else:
            print_info(f"{Icons.INFO} {error.user_message}")
        
        # Show context if available
        if error.context and error.context.operation:
            print(f"  Operation: {error.context.operation}")
        
        # Show troubleshooting steps
        if error.troubleshooting_steps:
            print(f"\n{colorize('Troubleshooting Steps:', Colors.BRIGHT_BLUE)}")
            for i, step in enumerate(error.troubleshooting_steps, 1):
                print(f"  {i}. {step}")
        
        # Show technical details in debug mode
        if self.debug_mode and error.original_exception:
            print(f"\n{colorize('Technical Details:', Colors.DIM)}")
            print(f"  Exception Type: {type(error.original_exception).__name__}")
            print(f"  Exception Message: {str(error.original_exception)}")
            if hasattr(error.original_exception, '__traceback__'):
                print("  Traceback:")
                tb_lines = traceback.format_tb(error.original_exception.__traceback__)
                for line in tb_lines[-3:]:  # Show last 3 frames
                    print(f"    {line.strip()}")
    
    def _attempt_recovery(self, error: WizardError):
        """Attempt to recover from error"""
        from .cli_interface import InteractivePrompts, print_info, Icons
        
        print_info(f"\n{Icons.WRENCH} Recovery options available:")
        
        # Show available recovery actions
        action_names = [action.name.replace('_', ' ').title() for action in error.recovery_actions]
        action_names.append("Skip recovery")
        
        choice = InteractivePrompts.select_option(
            "Choose a recovery action:",
            action_names,
            default=0
        )
        
        if choice < len(error.recovery_actions):
            action = error.recovery_actions[choice]
            
            if action.requires_confirmation:
                if not InteractivePrompts.yes_no(f"Execute: {action.description}?"):
                    return
            
            try:
                print_info(f"Executing: {action.description}...")
                result = action.action()
                
                if asyncio.iscoroutine(result):
                    asyncio.run(result)
                
                print_info("Recovery action completed successfully!")
                
            except Exception as recovery_error:
                print_error(f"Recovery action failed: {str(recovery_error)}")
                self.logger.error(f"Recovery failed: {str(recovery_error)}")
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for error context"""
        import platform
        
        return {
            "os": platform.system(),
            "os_version": platform.release(),
            "python_version": platform.python_version(),
            "architecture": platform.machine(),
            "cwd": os.getcwd(),
            "user": os.environ.get("USER", "unknown")
        }
    
    def create_recovery_action(self, 
                              name: str, 
                              description: str, 
                              action: Callable,
                              is_automatic: bool = False) -> RecoveryAction:
        """Create a custom recovery action"""
        return RecoveryAction(
            name=name,
            description=description,
            action=action,
            is_automatic=is_automatic,
            requires_confirmation=not is_automatic
        )
    
    def register_custom_error(self, 
                             error_pattern: str, 
                             error_info: WizardError):
        """Register a custom error pattern"""
        self.error_registry.register_error(error_pattern, error_info)


class CommonRecoveryActions:
    """Common recovery actions that can be reused"""
    
    @staticmethod
    def install_package(package_name: str) -> RecoveryAction:
        """Recovery action to install a Python package"""
        def install():
            subprocess.run([sys.executable, "-m", "pip", "install", package_name], 
                         check=True, capture_output=True, text=True)
        
        return RecoveryAction(
            name="install_package",
            description=f"Install {package_name} package",
            action=install
        )
    
    @staticmethod
    def create_directory(path: str) -> RecoveryAction:
        """Recovery action to create a missing directory"""
        def create():
            Path(path).mkdir(parents=True, exist_ok=True)
        
        return RecoveryAction(
            name="create_directory",
            description=f"Create directory {path}",
            action=create
        )
    
    @staticmethod
    def fix_permissions(file_path: str) -> RecoveryAction:
        """Recovery action to fix file permissions"""
        def fix():
            os.chmod(file_path, 0o755)
        
        return RecoveryAction(
            name="fix_permissions",
            description=f"Fix permissions for {file_path}",
            action=fix
        )
    
    @staticmethod
    def backup_and_recreate_file(file_path: str, content: str = "") -> RecoveryAction:
        """Recovery action to backup and recreate a file"""
        def recreate():
            if os.path.exists(file_path):
                import shutil
                shutil.copy2(file_path, f"{file_path}.backup")
            
            with open(file_path, 'w') as f:
                f.write(content)
        
        return RecoveryAction(
            name="recreate_file",
            description=f"Backup and recreate {file_path}",
            action=recreate
        )
    
    @staticmethod
    def restart_service(service_name: str) -> RecoveryAction:
        """Recovery action to restart a service"""
        def restart():
            # This would be platform-specific
            if sys.platform == "darwin":
                subprocess.run(["brew", "services", "restart", service_name], check=True)
            elif sys.platform.startswith("linux"):
                subprocess.run(["systemctl", "restart", service_name], check=True)
        
        return RecoveryAction(
            name="restart_service",
            description=f"Restart {service_name} service",
            action=restart
        )


class SafeExecutor:
    """Safe execution wrapper with error handling"""
    
    def __init__(self, error_handler: ErrorHandler):
        self.error_handler = error_handler
    
    def safe_execute(self, 
                    func: Callable, 
                    operation_name: str,
                    *args, 
                    default_return=None, 
                    **kwargs):
        """Safely execute a function with error handling"""
        with self.error_handler.handle_errors(operation_name, suppress_errors=True):
            return func(*args, **kwargs)
        
        return default_return
    
    async def safe_async_execute(self, 
                               func: Callable, 
                               operation_name: str,
                               *args, 
                               default_return=None, 
                               **kwargs):
        """Safely execute an async function with error handling"""
        try:
            async with self.error_handler.handle_async_errors(operation_name):
                return await func(*args, **kwargs)
        except Exception:
            return default_return


# Global error handler instance
_global_error_handler = None


def get_error_handler(debug_mode: bool = False) -> ErrorHandler:
    """Get global error handler instance"""
    global _global_error_handler
    
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler(debug_mode=debug_mode)
    
    return _global_error_handler


def handle_errors(*args, **kwargs):
    """Decorator for error handling"""
    def decorator(func):
        def wrapper(*f_args, **f_kwargs):
            handler = get_error_handler()
            operation_name = kwargs.get('operation', func.__name__)
            
            with handler.handle_errors(operation_name):
                return func(*f_args, **f_kwargs)
        
        return wrapper
    return decorator