"""
Proyecto Semilla Python SDK
SDK oficial para interactuar con Proyecto Semilla desde LLMs y aplicaciones
"""

__version__ = "0.1.0"
__author__ = "Proyecto Semilla Team"

from .client import ProyectoSemillaClient
from .models import Tenant, User, ModuleSpec

__all__ = ["ProyectoSemillaClient", "Tenant", "User", "ModuleSpec"]