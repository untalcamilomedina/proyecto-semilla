"""
Vibecoding Configuration Wizard

An intelligent configuration wizard for MCP (Model Context Protocol) connections
that auto-detects environments, validates configurations, and provides recovery.
"""

__version__ = "1.0.0"
__author__ = "Vibecoding Team"
__email__ = "dev@vibecoding.com"
__description__ = "Intelligent MCP Configuration Wizard"

from .environment_detector import EnvironmentDetector, SystemEnvironment, EnvironmentAnalyzer
from .config_validator import ConfigurationValidator, ConfigurationGenerator
from .cli_interface import WizardInterface
from .error_handler import ErrorHandler, get_error_handler

__all__ = [
    "EnvironmentDetector",
    "SystemEnvironment", 
    "EnvironmentAnalyzer",
    "ConfigurationValidator",
    "ConfigurationGenerator", 
    "WizardInterface",
    "ErrorHandler",
    "get_error_handler"
]