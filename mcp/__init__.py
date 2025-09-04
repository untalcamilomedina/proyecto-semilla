"""
MCP (Model Context Protocol) integration for Proyecto Semilla
Permite que LLMs entiendan y extiendan automáticamente la plataforma
"""

__version__ = "0.1.0"
__author__ = "Proyecto Semilla Team"

from .server import ProyectoSemillaMCPServer

__all__ = ["ProyectoSemillaMCPServer"]