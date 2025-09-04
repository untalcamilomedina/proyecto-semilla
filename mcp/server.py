"""
Proyecto Semilla MCP Server
Permite que LLMs entiendan y extiendan automáticamente la plataforma
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPTool:
    """Representa una herramienta que LLMs pueden ejecutar"""

    def __init__(self, name: str, description: str, function: Callable, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters

    async def execute(self, **kwargs) -> Any:
        """Ejecutar la herramienta con los parámetros proporcionados"""
        try:
            if asyncio.iscoroutinefunction(self.function):
                return await self.function(**kwargs)
            else:
                return self.function(**kwargs)
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {e}")
            return {"error": str(e)}


class MCPResource:
    """Representa un recurso que LLMs pueden consultar"""

    def __init__(self, uri: str, name: str, description: str, content_function: Callable):
        self.uri = uri
        self.name = name
        self.description = description
        self.content_function = content_function

    async def get_content(self) -> str:
        """Obtener el contenido del recurso"""
        try:
            if asyncio.iscoroutinefunction(self.content_function):
                return await self.content_function()
            else:
                return self.content_function()
        except Exception as e:
            logger.error(f"Error getting content for resource {self.uri}: {e}")
            return f"Error: {str(e)}"


class ProyectoSemillaMCPServer:
    """
    MCP Server para Proyecto Semilla
    Permite que LLMs entiendan y extiendan automáticamente la plataforma
    """

    def __init__(self, api_url: str = "http://localhost:8000", api_key: str = None):
        self.api_url = api_url
        self.api_key = api_key
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self._register_core_tools()
        self._register_core_resources()

    def _register_core_tools(self):
        """Registrar herramientas básicas del sistema"""
        # Tool: Health Check
        self.register_tool(
            name="health_check",
            description="Verificar el estado de salud del sistema Proyecto Semilla",
            function=self._health_check,
            parameters={}
        )

        # Tool: Get System Info
        self.register_tool(
            name="get_system_info",
            description="Obtener información general del sistema",
            function=self._get_system_info,
            parameters={}
        )

        # Tool: Analyze Architecture
        self.register_tool(
            name="analyze_architecture",
            description="Analizar la arquitectura completa de Proyecto Semilla",
            function=self._analyze_architecture,
            parameters={}
        )

        # Tool: List Tenants
        self.register_tool(
            name="list_tenants",
            description="Listar todos los tenants disponibles",
            function=self._list_tenants,
            parameters={
                "limit": {"type": "integer", "description": "Número máximo de tenants a retornar", "default": 10}
            }
        )

        # Tool: Create Tenant
        self.register_tool(
            name="create_tenant",
            description="Crear un nuevo tenant en el sistema",
            function=self._create_tenant,
            parameters={
                "name": {"type": "string", "description": "Nombre del tenant", "required": True},
                "slug": {"type": "string", "description": "Slug único del tenant", "required": True},
                "description": {"type": "string", "description": "Descripción del tenant"}
            }
        )

        # ========================================
        # DOCUMENTATION TOOLS - AUTO-DOCUMENTATION
        # ========================================

        # Integrar herramientas de documentación
        try:
            from .tools.documentation_tools import register_documentation_tools
            register_documentation_tools(self)
        except ImportError as e:
            logger.warning(f"No se pudieron cargar herramientas de documentación: {e}")

    def _register_core_resources(self):
        """Registrar recursos básicos del sistema"""
        # Resource: Architecture Overview
        self.register_resource(
            uri="project://architecture",
            name="Architecture Overview",
            description="Vista general de la arquitectura de Proyecto Semilla",
            content_function=self._get_architecture_overview
        )

        # Resource: Database Schema
        self.register_resource(
            uri="project://database/schema",
            name="Database Schema",
            description="Esquema completo de la base de datos",
            content_function=self._get_database_schema
        )

        # Resource: API Endpoints
        self.register_resource(
            uri="project://api/endpoints",
            name="API Endpoints",
            description="Lista completa de endpoints disponibles",
            content_function=self._get_api_endpoints
        )

    def register_tool(self, name: str, description: str, function: Callable, parameters: Dict[str, Any]):
        """Registrar una nueva herramienta"""
        tool = MCPTool(name, description, function, parameters)
        self.tools[name] = tool
        logger.info(f"Registered MCP tool: {name}")

    def register_resource(self, uri: str, name: str, description: str, content_function: Callable):
        """Registrar un nuevo recurso"""
        resource = MCPResource(uri, name, description, content_function)
        self.resources[uri] = resource
        logger.info(f"Registered MCP resource: {uri}")

    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Ejecutar una herramienta por nombre"""
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not found"}

        tool = self.tools[tool_name]
        return await tool.execute(**kwargs)

    async def get_resource(self, uri: str) -> str:
        """Obtener el contenido de un recurso"""
        if uri not in self.resources:
            return f"Resource '{uri}' not found"

        resource = self.resources[uri]
        return await resource.get_content()

    def list_tools(self) -> List[Dict[str, Any]]:
        """Listar todas las herramientas disponibles"""
        return [
            {
                "name": name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for name, tool in self.tools.items()
        ]

    def list_resources(self) -> List[Dict[str, Any]]:
        """Listar todos los recursos disponibles"""
        return [
            {
                "uri": uri,
                "name": resource.name,
                "description": resource.description
            }
            for uri, resource in self.resources.items()
        ]

    # Core Tool Implementations
    async def _health_check(self) -> Dict[str, Any]:
        """Verificar estado del sistema"""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "0.1.0",
            "mcp_server": "operational"
        }

    async def _get_system_info(self) -> Dict[str, Any]:
        """Obtener información del sistema"""
        return {
            "name": "Proyecto Semilla",
            "version": "0.1.0",
            "description": "Primera plataforma SaaS Vibecoding-native",
            "architecture": "Multi-tenant FastAPI + PostgreSQL + Redis",
            "mcp_status": "active",
            "vibecoding_ready": True
        }

    async def _analyze_architecture(self) -> Dict[str, Any]:
        """Analizar arquitectura completa"""
        return {
            "overview": "Proyecto Semilla es una plataforma SaaS multi-tenant construida con FastAPI, PostgreSQL y Redis",
            "components": {
                "backend": "FastAPI con async SQLAlchemy",
                "database": "PostgreSQL con Row-Level Security",
                "cache": "Redis para sesiones y cache",
                "auth": "JWT con refresh tokens",
                "mcp": "Model Context Protocol para LLMs"
            },
            "patterns": [
                "Repository pattern para data access",
                "Dependency injection para servicios",
                "Middleware para cross-cutting concerns",
                "Async/await para I/O operations"
            ],
            "multi_tenant": {
                "strategy": "Database-level isolation con RLS",
                "context": "Tenant ID en JWT y request state",
                "data_isolation": "Políticas RLS automáticas"
            }
        }

    async def _list_tenants(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Listar tenants (mock implementation)"""
        # En una implementación real, esto consultaría la base de datos
        return [
            {
                "id": "demo-tenant-1",
                "name": "Demo Company",
                "slug": "demo-company",
                "description": "Tenant de demostración",
                "is_active": True
            }
        ]

    async def _create_tenant(self, name: str, slug: str, description: str = None) -> Dict[str, Any]:
        """Crear tenant (mock implementation)"""
        # En una implementación real, esto crearía el tenant en la base de datos
        return {
            "id": f"tenant-{slug}",
            "name": name,
            "slug": slug,
            "description": description,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }

    # Core Resource Implementations
    async def _get_architecture_overview(self) -> str:
        """Obtener overview de arquitectura"""
        return """
# Arquitectura de Proyecto Semilla

## Visión General
Proyecto Semilla es la primera plataforma SaaS diseñada nativamente para la era del Vibecoding.

## Componentes Principales
- **Backend**: FastAPI con Python 3.11+
- **Base de Datos**: PostgreSQL con Row-Level Security
- **Cache**: Redis para sesiones y datos temporales
- **Autenticación**: JWT con refresh tokens
- **MCP**: Model Context Protocol para integración con LLMs

## Patrones Arquitecturales
- **Multi-tenancy**: Aislamiento a nivel de base de datos
- **Repository Pattern**: Abstracción de acceso a datos
- **Dependency Injection**: Inyección de dependencias para testabilidad
- **Async/Await**: Operaciones I/O no bloqueantes

## Características Únicas
- **Vibecoding-Native**: Diseñado para desarrollo asistido por IA
- **Auto-Documentación**: Documentación que se mantiene automáticamente
- **Self-Improving**: El sistema aprende y mejora con el uso
        """

    async def _get_database_schema(self) -> str:
        """Obtener esquema de base de datos"""
        return """
# Esquema de Base de Datos - Proyecto Semilla

## Tablas Principales

### tenants
- id: UUID (PK)
- name: VARCHAR(100)
- slug: VARCHAR(50) UNIQUE
- description: TEXT
- parent_tenant_id: UUID (FK)
- settings: JSONB
- is_active: BOOLEAN
- created_at: TIMESTAMPTZ
- updated_at: TIMESTAMPTZ

### users
- id: UUID (PK)
- tenant_id: UUID (FK → tenants)
- email: VARCHAR(255) UNIQUE
- hashed_password: VARCHAR(255)
- first_name: VARCHAR(100)
- last_name: VARCHAR(100)
- full_name: VARCHAR(201)
- is_active: BOOLEAN
- is_verified: BOOLEAN
- preferences: JSONB
- last_login: TIMESTAMPTZ
- login_count: INTEGER
- created_at: TIMESTAMPTZ
- updated_at: TIMESTAMPTZ

### refresh_tokens
- id: UUID (PK)
- user_id: UUID (FK → users)
- tenant_id: UUID (FK → tenants)
- token: VARCHAR(500) UNIQUE
- is_revoked: BOOLEAN
- expires_at: TIMESTAMPTZ
- user_agent: VARCHAR(500)
- ip_address: VARCHAR(45)
- created_at: TIMESTAMPTZ
- revoked_at: TIMESTAMPTZ

## Políticas RLS (Row-Level Security)
- tenant_isolation_policy: Aísla datos por tenant_id
- user_tenant_isolation: Vincula usuarios a su tenant
        """

    async def _get_api_endpoints(self) -> str:
        """Obtener lista de endpoints"""
        return """
# API Endpoints - Proyecto Semilla v0.1.0

## Autenticación
- `POST /api/v1/auth/login` - Login con email/password
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout de dispositivo actual
- `POST /api/v1/auth/logout-all` - Logout de todos los dispositivos
- `GET /api/v1/auth/me` - Información del usuario actual

## Tenants
- `GET /api/v1/tenants/` - Listar tenants (con paginación)
- `POST /api/v1/tenants/` - Crear nuevo tenant
- `GET /api/v1/tenants/{id}` - Obtener tenant por ID
- `PUT /api/v1/tenants/{id}` - Actualizar tenant
- `DELETE /api/v1/tenants/{id}` - Eliminar tenant (soft delete)

## Health
- `GET /health` - Health check del sistema

## MCP (Model Context Protocol)
- `GET /mcp/tools` - Listar herramientas MCP disponibles
- `POST /mcp/tools/{name}/execute` - Ejecutar herramienta MCP
- `GET /mcp/resources` - Listar recursos MCP disponibles
- `GET /mcp/resources/{uri}` - Obtener contenido de recurso MCP
        """


# Función de utilidad para crear servidor MCP
def create_mcp_server(api_url: str = "http://localhost:8000", api_key: str = None) -> ProyectoSemillaMCPServer:
    """Crear instancia del servidor MCP"""
    return ProyectoSemillaMCPServer(api_url, api_key)


# Ejemplo de uso
if __name__ == "__main__":
    async def main():
        # Crear servidor MCP
        server = create_mcp_server()

        # Listar herramientas disponibles
        tools = server.list_tools()
        print(f"🛠️  Herramientas MCP disponibles: {len(tools)}")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")

        # Listar recursos disponibles
        resources = server.list_resources()
        print(f"📚 Recursos MCP disponibles: {len(resources)}")
        for resource in resources:
            print(f"  - {resource['uri']}: {resource['name']}")

        # Ejecutar health check
        health = await server.execute_tool("health_check")
        print(f"🏥 Health Check: {health}")

        # Obtener información del sistema
        info = await server.execute_tool("get_system_info")
        print(f"ℹ️  System Info: {info}")

    # Ejecutar ejemplo
    asyncio.run(main())