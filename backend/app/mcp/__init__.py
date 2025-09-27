"""
MCP (Model Context Protocol) module for Proyecto Semilla
Provides tools and resources for module management and system interaction
"""

from .server import ProyectoSemillaMCPServer
from .client import MCPClient
from .protocol import MCPProtocol

__all__ = ["ProyectoSemillaMCPServer", "MCPClient", "MCPProtocol"]