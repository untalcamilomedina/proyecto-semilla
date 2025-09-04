"""
Modelos de datos para el SDK de Proyecto Semilla
Definiciones type-safe para interactuar con la plataforma
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class Tenant:
    """Modelo que representa un Tenant en Proyecto Semilla"""
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    parent_tenant_id: Optional[str] = None
    settings: Dict[str, Any] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.settings is None:
            self.settings = {}


@dataclass
class User:
    """Modelo que representa un Usuario en Proyecto Semilla"""
    id: str
    email: str
    first_name: str
    last_name: str
    full_name: str
    is_active: bool = True
    is_verified: bool = False
    tenant_id: str = None
    role_ids: List[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.role_ids is None:
            self.role_ids = []


@dataclass
class ModuleSpec:
    """Especificación para generar un módulo usando Vibecoding"""
    name: str
    description: str
    category: str  # 'ecommerce', 'analytics', 'communication', etc.
    features: List[str]  # Lista de funcionalidades requeridas
    integrations: List[str] = None  # APIs externas a integrar
    ui_components: List[str] = None  # Componentes UI necesarios
    database_tables: List[Dict[str, Any]] = None  # Esquemas de BD requeridos

    def __post_init__(self):
        if self.integrations is None:
            self.integrations = []
        if self.ui_components is None:
            self.ui_components = []
        if self.database_tables is None:
            self.database_tables = []


@dataclass
class APIResponse:
    """Respuesta genérica de la API"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    message: Optional[str] = None

    @classmethod
    def success_response(cls, data: Any = None, message: str = None) -> 'APIResponse':
        return cls(success=True, data=data, message=message)

    @classmethod
    def error_response(cls, error: str, message: str = None) -> 'APIResponse':
        return cls(success=False, error=error, message=message)


@dataclass
class HealthStatus:
    """Estado de salud del sistema"""
    status: str  # 'healthy', 'degraded', 'unhealthy'
    version: str
    timestamp: datetime
    services: Dict[str, str] = None  # Estado de cada servicio

    def __post_init__(self):
        if self.services is None:
            self.services = {}

    def is_healthy(self) -> bool:
        return self.status == 'healthy'


@dataclass
class SystemInfo:
    """Información general del sistema"""
    name: str
    version: str
    description: str
    architecture: str
    mcp_status: str
    vibecoding_ready: bool
    features: List[str] = None

    def __post_init__(self):
        if self.features is None:
            self.features = []


@dataclass
class ArchitectureAnalysis:
    """Análisis completo de la arquitectura"""
    overview: str
    components: Dict[str, str]
    patterns: List[str]
    multi_tenant: Dict[str, Any]
    vibecoding_features: List[str] = None

    def __post_init__(self):
        if self.vibecoding_features is None:
            self.vibecoding_features = []


# Type aliases para compatibilidad
TenantCreate = Dict[str, Any]
TenantUpdate = Dict[str, Any]
UserCreate = Dict[str, Any]
UserUpdate = Dict[str, Any]