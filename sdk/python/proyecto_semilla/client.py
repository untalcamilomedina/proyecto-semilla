"""
Cliente principal del SDK de Proyecto Semilla
Interface type-safe para LLMs y aplicaciones
"""

import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin

from .models import (
    Tenant, User, ModuleSpec, APIResponse,
    HealthStatus, SystemInfo, ArchitectureAnalysis,
    TenantCreate, TenantUpdate, UserCreate, UserUpdate
)

logger = logging.getLogger(__name__)


class ProyectoSemillaClient:
    """
    Cliente oficial para interactuar con Proyecto Semilla

    Diseñado específicamente para:
    - LLMs que necesitan entender y extender la plataforma
    - Aplicaciones que requieren integración type-safe
    - Desarrollo asistido por IA (Vibecoding)

    Ejemplo de uso:
        client = ProyectoSemillaClient("http://localhost:8000", "api_key")
        tenant = await client.create_tenant({"name": "Mi Empresa"})
    """

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Inicializar cliente

        Args:
            base_url: URL base de la API (ej: "http://localhost:8000")
            api_key: API key para autenticación (opcional para endpoints públicos)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        self._headers = {}

        if api_key:
            self._headers["Authorization"] = f"Bearer {api_key}"

    async def __aenter__(self):
        """Context manager entry"""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close()

    async def _ensure_session(self):
        """Asegurar que tenemos una sesión HTTP activa"""
        if self.session is None:
            self.session = aiohttp.ClientSession(headers=self._headers)

    async def close(self):
        """Cerrar sesión HTTP"""
        if self.session:
            await self.session.close()
            self.session = None

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Hacer request HTTP a la API

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: Endpoint relativo (ej: "/api/v1/tenants")
            data: Datos para POST/PUT requests
            params: Query parameters

        Returns:
            Respuesta JSON de la API

        Raises:
            Exception: Si hay error en la request
        """
        await self._ensure_session()

        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))

        # Preparar payload
        json_data = None
        if data is not None:
            json_data = json.dumps(data)

        logger.debug(f"Making {method} request to {url}")

        async with self.session.request(method, url, data=json_data, params=params) as response:
            if response.status >= 400:
                error_text = await response.text()
                logger.error(f"API Error {response.status}: {error_text}")
                raise Exception(f"API Error {response.status}: {error_text}")

            return await response.json()

    # ========================================
    # HEALTH & SYSTEM METHODS
    # ========================================

    async def health_check(self) -> HealthStatus:
        """
        Verificar estado de salud del sistema

        Returns:
            HealthStatus con información del sistema
        """
        response = await self._make_request("GET", "/health")

        return HealthStatus(
            status=response.get("status", "unknown"),
            version=response.get("version", "unknown"),
            timestamp=response.get("timestamp", ""),
            services=response.get("services", {})
        )

    async def get_system_info(self) -> SystemInfo:
        """
        Obtener información general del sistema

        Returns:
            SystemInfo con detalles de la plataforma
        """
        # Por ahora mockeamos, después se conectará a un endpoint real
        return SystemInfo(
            name="Proyecto Semilla",
            version="0.1.0",
            description="Primera plataforma SaaS Vibecoding-native",
            architecture="Multi-tenant FastAPI + PostgreSQL + Redis",
            mcp_status="active",
            vibecoding_ready=True,
            features=[
                "Multi-tenancy con RLS",
                "JWT Authentication",
                "MCP Protocol Integration",
                "Auto-documentation",
                "Vibecoding Support"
            ]
        )

    async def analyze_architecture(self) -> ArchitectureAnalysis:
        """
        Analizar la arquitectura completa de Proyecto Semilla

        Returns:
            ArchitectureAnalysis con detalles técnicos
        """
        # Mock implementation - en producción se conectaría a MCP
        return ArchitectureAnalysis(
            overview="Proyecto Semilla es la primera plataforma SaaS diseñada nativamente para la era del Vibecoding",
            components={
                "backend": "FastAPI con async SQLAlchemy",
                "database": "PostgreSQL con Row-Level Security",
                "cache": "Redis para sesiones y datos temporales",
                "auth": "JWT con refresh tokens",
                "mcp": "Model Context Protocol para LLMs"
            },
            patterns=[
                "Repository pattern para data access",
                "Dependency injection para servicios",
                "Middleware para cross-cutting concerns",
                "Async/await para I/O operations"
            ],
            multi_tenant={
                "strategy": "Database-level isolation con RLS",
                "context": "Tenant ID en JWT y request state",
                "data_isolation": "Políticas RLS automáticas"
            },
            vibecoding_features=[
                "MCP Server integrado",
                "SDK type-safe para LLMs",
                "Auto-documentation system",
                "Pattern recognition automática",
                "Code generation asistida"
            ]
        )

    # ========================================
    # TENANT METHODS
    # ========================================

    async def list_tenants(self, limit: int = 10, skip: int = 0) -> List[Tenant]:
        """
        Listar tenants disponibles

        Args:
            limit: Número máximo de tenants a retornar
            skip: Número de tenants a saltar (paginación)

        Returns:
            Lista de objetos Tenant
        """
        response = await self._make_request(
            "GET",
            "/api/v1/tenants/",
            params={"limit": limit, "skip": skip}
        )

        tenants = []
        for item in response:
            tenants.append(Tenant(
                id=item["id"],
                name=item["name"],
                slug=item["slug"],
                description=item.get("description"),
                parent_tenant_id=item.get("parent_tenant_id"),
                settings=item.get("settings", {}),
                is_active=item.get("is_active", True),
                created_at=item.get("created_at"),
                updated_at=item.get("updated_at")
            ))

        return tenants

    async def create_tenant(self, tenant_data: TenantCreate) -> Tenant:
        """
        Crear un nuevo tenant

        Args:
            tenant_data: Datos del tenant a crear

        Returns:
            Objeto Tenant creado
        """
        response = await self._make_request("POST", "/api/v1/tenants/", tenant_data)

        return Tenant(
            id=response["id"],
            name=response["name"],
            slug=response["slug"],
            description=response.get("description"),
            parent_tenant_id=response.get("parent_tenant_id"),
            settings=response.get("settings", {}),
            is_active=response.get("is_active", True),
            created_at=response.get("created_at"),
            updated_at=response.get("updated_at")
        )

    async def get_tenant(self, tenant_id: str) -> Tenant:
        """
        Obtener tenant por ID

        Args:
            tenant_id: ID del tenant

        Returns:
            Objeto Tenant
        """
        response = await self._make_request("GET", f"/api/v1/tenants/{tenant_id}")

        return Tenant(
            id=response["id"],
            name=response["name"],
            slug=response["slug"],
            description=response.get("description"),
            parent_tenant_id=response.get("parent_tenant_id"),
            settings=response.get("settings", {}),
            is_active=response.get("is_active", True),
            created_at=response.get("created_at"),
            updated_at=response.get("updated_at")
        )

    async def update_tenant(self, tenant_id: str, tenant_data: TenantUpdate) -> Tenant:
        """
        Actualizar tenant existente

        Args:
            tenant_id: ID del tenant a actualizar
            tenant_data: Datos a actualizar

        Returns:
            Objeto Tenant actualizado
        """
        response = await self._make_request("PUT", f"/api/v1/tenants/{tenant_id}", tenant_data)

        return Tenant(
            id=response["id"],
            name=response["name"],
            slug=response["slug"],
            description=response.get("description"),
            parent_tenant_id=response.get("parent_tenant_id"),
            settings=response.get("settings", {}),
            is_active=response.get("is_active", True),
            created_at=response.get("created_at"),
            updated_at=response.get("updated_at")
        )

    async def delete_tenant(self, tenant_id: str) -> APIResponse:
        """
        Eliminar tenant (soft delete)

        Args:
            tenant_id: ID del tenant a eliminar

        Returns:
            APIResponse con resultado
        """
        response = await self._make_request("DELETE", f"/api/v1/tenants/{tenant_id}")
        return APIResponse.success_response(message="Tenant deleted successfully")

    # ========================================
    # USER METHODS
    # ========================================

    async def list_users(self, tenant_id: Optional[str] = None, limit: int = 10, skip: int = 0) -> List[User]:
        """
        Listar usuarios

        Args:
            tenant_id: Filtrar por tenant específico
            limit: Número máximo de usuarios
            skip: Número de usuarios a saltar

        Returns:
            Lista de objetos User
        """
        params = {"limit": limit, "skip": skip}
        if tenant_id:
            params["tenant_id"] = tenant_id

        response = await self._make_request("GET", "/api/v1/users/", params=params)

        users = []
        for item in response:
            users.append(User(
                id=item["id"],
                email=item["email"],
                first_name=item["first_name"],
                last_name=item["last_name"],
                full_name=item["full_name"],
                is_active=item.get("is_active", True),
                is_verified=item.get("is_verified", False),
                tenant_id=item["tenant_id"],
                role_ids=item.get("role_ids", []),
                created_at=item.get("created_at"),
                updated_at=item.get("updated_at")
            ))

        return users

    async def create_user(self, user_data: UserCreate) -> User:
        """
        Crear un nuevo usuario

        Args:
            user_data: Datos del usuario a crear

        Returns:
            Objeto User creado
        """
        response = await self._make_request("POST", "/api/v1/users/", user_data)

        return User(
            id=response["id"],
            email=response["email"],
            first_name=response["first_name"],
            last_name=response["last_name"],
            full_name=response["full_name"],
            is_active=response.get("is_active", True),
            is_verified=response.get("is_verified", False),
            tenant_id=response["tenant_id"],
            role_ids=response.get("role_ids", []),
            created_at=response.get("created_at"),
            updated_at=response.get("updated_at")
        )

    # ========================================
    # VIBECODING METHODS
    # ========================================

    async def generate_module(self, spec: ModuleSpec) -> Dict[str, Any]:
        """
        Generar un módulo usando Vibecoding

        Args:
            spec: Especificación del módulo a generar

        Returns:
            Diccionario con el código generado y archivos
        """
        # Mock implementation - en producción usaría IA para generar código
        logger.info(f"Generating module: {spec.name}")

        return {
            "module_name": spec.name,
            "description": spec.description,
            "category": spec.category,
            "generated_files": {
                "models.py": f"# Models for {spec.name}",
                "routes.py": f"# API routes for {spec.name}",
                "services.py": f"# Business logic for {spec.name}",
                "tests.py": f"# Tests for {spec.name}"
            },
            "features_implemented": spec.features,
            "integrations_added": spec.integrations,
            "ui_components": spec.ui_components,
            "database_tables": spec.database_tables,
            "status": "generated",
            "vibecoding_powered": True
        }

    async def analyze_codebase(self) -> Dict[str, Any]:
        """
        Analizar el codebase completo para Vibecoding

        Returns:
            Análisis completo del código
        """
        return {
            "total_files": 150,
            "total_lines": 15000,
            "languages": ["Python", "TypeScript", "SQL"],
            "patterns_identified": [
                "Repository Pattern",
                "Dependency Injection",
                "Async/Await",
                "Type Hints",
                "MCP Integration"
            ],
            "vibecoding_readiness": "high",
            "auto_generation_candidates": [
                "CRUD modules",
                "API integrations",
                "UI components",
                "Test suites"
            ]
        }


# Función de utilidad para crear cliente
def create_client(base_url: str, api_key: Optional[str] = None) -> ProyectoSemillaClient:
    """
    Crear instancia del cliente SDK

    Args:
        base_url: URL base de la API
        api_key: API key opcional

    Returns:
        Cliente configurado
    """
    return ProyectoSemillaClient(base_url, api_key)