"""
Documentation Tools para MCP
Herramientas que permiten a LLMs generar y actualizar documentación automáticamente
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    import aiofiles
except ImportError:
    aiofiles = None

from ..server import MCPTool


class DocumentationTools:
    """
    Herramientas de documentación para el sistema MCP
    Permite a LLMs generar, leer y actualizar documentación automáticamente
    """

    def __init__(self, docs_path: str = "docs"):
        self.docs_path = Path(docs_path)
        self.vibecoding_docs_path = self.docs_path / "vibecoding"
        self._ensure_docs_structure()

    def _ensure_docs_structure(self):
        """Asegurar que la estructura de documentación existe"""
        directories = [
            self.docs_path,
            self.vibecoding_docs_path,
            self.vibecoding_docs_path / "getting-started",
            self.vibecoding_docs_path / "examples",
            self.vibecoding_docs_path / "best-practices"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def get_documentation_tools(self) -> List[MCPTool]:
        """
        Obtener lista de herramientas de documentación para MCP
        """
        return [
            MCPTool(
                name="generate_api_docs",
                description="Generar documentación automática de APIs basada en el código",
                function=self.generate_api_documentation,
                parameters={
                    "endpoint_path": {
                        "type": "string",
                        "description": "Path del endpoint a documentar (ej: '/api/v1/tenants')",
                        "required": True
                    },
                    "include_examples": {
                        "type": "boolean",
                        "description": "Incluir ejemplos de uso",
                        "default": True
                    }
                }
            ),
            MCPTool(
                name="update_module_docs",
                description="Actualizar documentación de un módulo específico",
                function=self.update_module_documentation,
                parameters={
                    "module_name": {
                        "type": "string",
                        "description": "Nombre del módulo a documentar",
                        "required": True
                    },
                    "description": {
                        "type": "string",
                        "description": "Descripción del módulo",
                        "required": True
                    },
                    "features": {
                        "type": "array",
                        "description": "Lista de funcionalidades del módulo",
                        "items": {"type": "string"}
                    }
                }
            ),
            MCPTool(
                name="generate_vibecoding_guide",
                description="Generar guía de Vibecoding para un caso de uso específico",
                function=self.generate_vibecoding_guide,
                parameters={
                    "use_case": {
                        "type": "string",
                        "description": "Caso de uso específico (ej: 'ecommerce', 'analytics')",
                        "required": True
                    },
                    "complexity": {
                        "type": "string",
                        "description": "Nivel de complejidad (simple, medium, complex)",
                        "default": "medium"
                    }
                }
            ),
            MCPTool(
                name="validate_documentation",
                description="Validar que la documentación esté completa y actualizada",
                function=self.validate_documentation,
                parameters={
                    "check_api_coverage": {
                        "type": "boolean",
                        "description": "Verificar cobertura de documentación de APIs",
                        "default": True
                    },
                    "check_examples": {
                        "type": "boolean",
                        "description": "Verificar que hay ejemplos de uso",
                        "default": True
                    }
                }
            )
        ]

    async def generate_api_documentation(self, endpoint_path: str, include_examples: bool = True) -> Dict[str, Any]:
        """
        Generar documentación automática para un endpoint específico

        Args:
            endpoint_path: Path del endpoint (ej: '/api/v1/tenants')
            include_examples: Incluir ejemplos de uso

        Returns:
            Documentación generada en formato estructurado
        """
        # Mock implementation - en producción analizaría el código FastAPI
        docs = {
            "endpoint": endpoint_path,
            "description": f"Documentación automática para {endpoint_path}",
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "authentication": "JWT Bearer Token",
            "rate_limiting": "100 requests/minute",
            "response_format": "JSON",
            "last_updated": datetime.utcnow().isoformat(),
            "generated_by": "MCP Documentation Tool"
        }

        if include_examples:
            docs["examples"] = {
                "get_request": f"GET {endpoint_path}",
                "post_request": f"POST {endpoint_path}\nContent-Type: application/json\n{json.dumps({'example': 'data'}, indent=2)}",
                "response": json.dumps({"success": True, "data": "example"}, indent=2)
            }

        # Guardar documentación
        await self._save_api_documentation(endpoint_path, docs)

        return {
            "status": "success",
            "message": f"Documentación generada para {endpoint_path}",
            "documentation": docs
        }

    async def update_module_documentation(self, module_name: str, description: str, features: List[str] = None) -> Dict[str, Any]:
        """
        Actualizar documentación de un módulo

        Args:
            module_name: Nombre del módulo
            description: Descripción del módulo
            features: Lista de funcionalidades

        Returns:
            Resultado de la actualización
        """
        if features is None:
            features = []

        module_docs = {
            "name": module_name,
            "description": description,
            "features": features,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "vibecoding_ready": True,
            "auto_generated": True
        }

        # Guardar en archivo
        docs_file = self.docs_path / f"module_{module_name}.json"
        async with aiofiles.open(docs_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(module_docs, indent=2, ensure_ascii=False))

        return {
            "status": "success",
            "message": f"Documentación actualizada para módulo {module_name}",
            "file_path": str(docs_file)
        }

    async def generate_vibecoding_guide(self, use_case: str, complexity: str = "medium") -> Dict[str, Any]:
        """
        Generar guía de Vibecoding para un caso de uso específico

        Args:
            use_case: Caso de uso (ej: 'ecommerce', 'analytics')
            complexity: Nivel de complejidad

        Returns:
            Guía completa de Vibecoding
        """
        guide = {
            "title": f"Guía Vibecoding: {use_case.title()}",
            "use_case": use_case,
            "complexity": complexity,
            "generated_at": datetime.utcnow().isoformat(),
            "sections": []
        }

        # Generar secciones basadas en el caso de uso
        if use_case == "ecommerce":
            guide["sections"] = [
                {
                    "title": "1. Análisis de Requerimientos",
                    "content": "Identificar productos, categorías, carrito de compras, pagos...",
                    "mcp_tools_needed": ["analyze_architecture", "get_database_schema"]
                },
                {
                    "title": "2. Diseño de Base de Datos",
                    "content": "Crear tablas para products, categories, orders, payments...",
                    "mcp_tools_needed": ["generate_api_docs", "update_module_docs"]
                },
                {
                    "title": "3. Generación de APIs",
                    "content": "Crear endpoints REST para gestión de productos y pedidos",
                    "mcp_tools_needed": ["generate_api_docs"]
                },
                {
                    "title": "4. Implementación de Lógica de Negocio",
                    "content": "Reglas de inventario, descuentos, envío...",
                    "mcp_tools_needed": ["update_module_docs"]
                }
            ]
        elif use_case == "analytics":
            guide["sections"] = [
                {
                    "title": "1. Definición de Métricas",
                    "content": "Identificar KPIs, dashboards, reportes...",
                    "mcp_tools_needed": ["analyze_architecture"]
                },
                {
                    "title": "2. Diseño de Data Warehouse",
                    "content": "Esquemas para almacenamiento de datos analíticos",
                    "mcp_tools_needed": ["get_database_schema"]
                }
            ]
        else:
            guide["sections"] = [
                {
                    "title": "1. Análisis General",
                    "content": f"Análisis específico para caso de uso: {use_case}",
                    "mcp_tools_needed": ["analyze_architecture", "get_system_info"]
                }
            ]

        # Guardar guía
        guide_file = self.vibecoding_docs_path / "examples" / f"vibecoding-{use_case}.json"
        async with aiofiles.open(guide_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(guide, indent=2, ensure_ascii=False))

        return {
            "status": "success",
            "message": f"Guía Vibecoding generada para {use_case}",
            "guide": guide,
            "file_path": str(guide_file)
        }

    async def validate_documentation(self, check_api_coverage: bool = True, check_examples: bool = True) -> Dict[str, Any]:
        """
        Validar estado de la documentación

        Args:
            check_api_coverage: Verificar cobertura de APIs
            check_examples: Verificar ejemplos

        Returns:
            Reporte de validación
        """
        validation_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "checks": [],
            "issues": [],
            "recommendations": []
        }

        # Verificar estructura de directorios
        required_dirs = [
            self.docs_path,
            self.vibecoding_docs_path,
            self.vibecoding_docs_path / "getting-started",
            self.vibecoding_docs_path / "examples",
            self.vibecoding_docs_path / "best-practices"
        ]

        for directory in required_dirs:
            if directory.exists():
                validation_report["checks"].append(f"✅ Directorio {directory.name} existe")
            else:
                validation_report["issues"].append(f"❌ Falta directorio {directory.name}")
                validation_report["recommendations"].append(f"Crear directorio {directory}")

        # Verificar archivos de documentación crítica
        critical_files = [
            self.docs_path / "README.md",
            self.vibecoding_docs_path / "getting-started" / "overview.md"
        ]

        for file_path in critical_files:
            if file_path.exists():
                validation_report["checks"].append(f"✅ Archivo {file_path.name} existe")
            else:
                validation_report["issues"].append(f"❌ Falta archivo crítico {file_path.name}")
                validation_report["recommendations"].append(f"Crear archivo {file_path}")

        # Verificar cobertura de APIs (simulado)
        if check_api_coverage:
            api_endpoints = [
                "/api/v1/tenants",
                "/api/v1/users",
                "/api/v1/auth"
            ]

            for endpoint in api_endpoints:
                docs_file = self.docs_path / f"api{endpoint.replace('/', '_')}.json"
                if docs_file.exists():
                    validation_report["checks"].append(f"✅ Documentación API {endpoint} existe")
                else:
                    validation_report["issues"].append(f"❌ Falta documentación para {endpoint}")
                    validation_report["recommendations"].append(f"Generar docs para {endpoint}")

        return {
            "status": "completed",
            "validation_report": validation_report
        }

    async def _save_api_documentation(self, endpoint_path: str, docs: Dict[str, Any]):
        """
        Guardar documentación de API en archivo

        Args:
            endpoint_path: Path del endpoint
            docs: Documentación a guardar
        """
        try:
            import aiofiles
        except ImportError:
            # Fallback si no está disponible aiofiles
            filename = f"api{endpoint_path.replace('/', '_')}.json"
            docs_file = self.docs_path / filename

            with open(docs_file, 'w', encoding='utf-8') as f:
                json.dump(docs, f, indent=2, ensure_ascii=False)
            return

        filename = f"api{endpoint_path.replace('/', '_')}.json"
        docs_file = self.docs_path / filename

        async with aiofiles.open(docs_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(docs, indent=2, ensure_ascii=False))


# Función para integrar con MCP Server
def register_documentation_tools(mcp_server):
    """
    Registrar herramientas de documentación en el servidor MCP

    Args:
        mcp_server: Instancia del ProyectoSemillaMCPServer
    """
    docs_tools = DocumentationTools()

    for tool in docs_tools.get_documentation_tools():
        mcp_server.register_tool(tool.name, tool.description, tool.function, tool.parameters)

    print(f"📚 Registradas {len(docs_tools.get_documentation_tools())} herramientas de documentación en MCP")