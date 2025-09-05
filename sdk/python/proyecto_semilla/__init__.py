"""
Proyecto Semilla SDK - Vibecoding-Native Development Platform
"""

__version__ = "0.1.0"
__author__ = "Proyecto Semilla Team"
__description__ = "SDK for Vibecoding-native application development"

from .client import ProyectoSemillaClient
from .models import (
    Tenant,
    User,
    ModuleSpec,
    APIResponse,
    ModuleStatus,
    GenerationResult
)
from .exceptions import (
    ProyectoSemillaError,
    AuthenticationError,
    APIError,
    ValidationError
)

__all__ = [
    "ProyectoSemillaClient",
    "Tenant",
    "User",
    "ModuleSpec",
    "APIResponse",
    "ModuleStatus",
    "GenerationResult",
    "ProyectoSemillaError",
    "AuthenticationError",
    "APIError",
    "ValidationError"
]