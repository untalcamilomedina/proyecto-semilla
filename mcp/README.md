# 🔌 MCP Server - Proyecto Semilla

Este directorio contiene el **Model Context Protocol (MCP) Server** oficial para Proyecto Semilla, que permite la integración nativa con Claude Code y otras herramientas AI.

## 🎯 ¿Qué es el MCP Server?

El MCP Server de Proyecto Semilla actúa como un puente entre Claude Code y las instancias de Proyecto Semilla, permitiendo:

- 🛠️ **Tools**: Ejecutar operaciones CRUD directamente desde Claude
- 📊 **Resources**: Acceder a información contextual del sistema
- 💡 **Prompts**: Asistencia especializada por dominio de negocio
- 🔍 **Auto-discovery**: Detección automática de capabilities

## 🏗️ Arquitectura del MCP Server

```
mcp/
├── README.md                 # Este archivo
├── server.py                 # Servidor MCP principal
├── config.py                 # Configuración y settings
├── auth/                     # Autenticación y permisos
│   ├── __init__.py
│   ├── middleware.py         # Middleware de autenticación
│   └── permissions.py        # Verificación de permisos
├── tools/                    # MCP Tools
│   ├── __init__.py
│   ├── base.py              # Clase base para tools
│   ├── users.py             # Tools de gestión de usuarios
│   ├── tenants.py           # Tools de gestión de tenants
│   ├── roles.py             # Tools de gestión de roles
│   └── analytics.py         # Tools de analytics (futuro)
├── resources/               # MCP Resources
│   ├── __init__.py
│   ├── base.py              # Clase base para resources
│   ├── tenant_info.py       # Información del tenant
│   ├── user_profiles.py     # Perfiles de usuarios
│   └── system_stats.py      # Estadísticas del sistema
├── prompts/                 # MCP Prompts
│   ├── __init__.py
│   ├── base.py              # Clase base para prompts
│   ├── user_assistant.py    # Asistente para gestión de usuarios
│   ├── tenant_setup.py      # Asistente para setup de tenants
│   └── troubleshooting.py   # Asistente para troubleshooting
├── modules/                 # Extensiones por módulos
│   ├── __init__.py
│   ├── inventory/           # Herramientas de inventario
│   │   ├── tools.py
│   │   ├── resources.py
│   │   └── prompts.py
│   └── crm/                 # Herramientas de CRM (futuro)
│       ├── tools.py
│       ├── resources.py
│       └── prompts.py
├── utils/                   # Utilidades
│   ├── __init__.py
│   ├── validators.py        # Validadores de input
│   ├── formatters.py        # Formateo de responses
│   └── cache.py             # Sistema de cache
├── tests/                   # Tests del MCP server
│   ├── test_tools.py
│   ├── test_resources.py
│   └── test_prompts.py
└── examples/                # Ejemplos de configuración
    ├── claude-code-config.json
    └── custom-tools-example.py
```

## 🛠️ MCP Tools Disponibles

### 👥 **User Management Tools**

```python
@mcp_tool("list_users")
async def list_users(tenant_id: str, limit: int = 10, search: str = "") -> list:
    """
    Lista usuarios de un tenant específico.
    
    Args:
        tenant_id: ID del tenant
        limit: Número máximo de usuarios a retornar
        search: Término de búsqueda (opcional)
    
    Returns:
        Lista de usuarios con información básica
    """
```

```python
@mcp_tool("create_user")
async def create_user(tenant_id: str, user_data: dict) -> dict:
    """
    Crea un nuevo usuario en el tenant especificado.
    
    Args:
        tenant_id: ID del tenant
        user_data: Datos del usuario (email, first_name, last_name, etc.)
    
    Returns:
        Información del usuario creado
    """
```

```python
@mcp_tool("update_user")
async def update_user(user_id: str, updates: dict) -> dict:
    """
    Actualiza información de un usuario existente.
    
    Args:
        user_id: ID del usuario a actualizar
        updates: Campos a actualizar
    
    Returns:
        Información actualizada del usuario
    """
```

### 🏢 **Tenant Management Tools**

```python
@mcp_tool("get_tenant_info")
async def get_tenant_info(tenant_id: str) -> dict:
    """
    Obtiene información detallada de un tenant.
    
    Args:
        tenant_id: ID del tenant
    
    Returns:
        Información completa del tenant incluyendo estadísticas
    """
```

```python
@mcp_tool("list_tenant_modules")
async def list_tenant_modules(tenant_id: str) -> list:
    """
    Lista módulos activos en un tenant.
    
    Args:
        tenant_id: ID del tenant
    
    Returns:
        Lista de módulos con su estado y configuración
    """
```

### 🔐 **Role Management Tools**

```python
@mcp_tool("assign_role")
async def assign_role(user_id: str, role_id: str) -> dict:
    """
    Asigna un rol a un usuario.
    
    Args:
        user_id: ID del usuario
        role_id: ID del rol a asignar
    
    Returns:
        Confirmación de asignación de rol
    """
```

## 📊 MCP Resources Disponibles

### 🏢 **Tenant Information Resource**

```python
@mcp_resource("tenant/{tenant_id}")
async def get_tenant_resource(tenant_id: str) -> dict:
    """
    Resource que proporciona información contextual completa del tenant.
    
    Incluye:
    - Información básica del tenant
    - Estadísticas de usuarios activos
    - Módulos habilitados
    - Configuraciones personalizadas
    - Métricas de uso recientes
    """
```

### 👤 **User Profile Resource**

```python
@mcp_resource("user/{user_id}/profile")
async def get_user_profile_resource(user_id: str) -> dict:
    """
    Resource que proporciona perfil completo del usuario.
    
    Incluye:
    - Información personal
    - Roles y permisos
    - Actividad reciente
    - Configuraciones personalizadas
    - Atributos custom
    """
```

### 📈 **System Statistics Resource**

```python
@mcp_resource("system/stats")
async def get_system_stats_resource() -> dict:
    """
    Resource que proporciona estadísticas del sistema.
    
    Incluye:
    - Total de tenants activos
    - Usuarios registrados
    - Módulos más utilizados
    - Performance metrics
    - Health status
    """
```

## 💡 MCP Prompts Especializados

### 🆘 **Troubleshooting Assistant**

```python
@mcp_prompt("troubleshoot_user_issue")
async def troubleshoot_user_issue() -> dict:
    """
    Asistente especializado para diagnosticar problemas de usuarios.
    
    Proporciona:
    - Guía paso a paso para diagnóstico
    - Comandos específicos para verificar estado
    - Soluciones comunes a problemas frecuentes
    """
```

### 🏗️ **Tenant Setup Assistant**

```python
@mcp_prompt("setup_new_tenant")
async def setup_new_tenant() -> dict:
    """
    Asistente para configurar nuevos tenants.
    
    Guía a través de:
    - Configuración inicial del tenant
    - Creación de roles básicos
    - Setup de primer usuario administrador
    - Activación de módulos recomendados
    """
```

### 👥 **User Management Assistant**

```python
@mcp_prompt("user_management_help")
async def user_management_help() -> dict:
    """
    Asistente especializado en gestión de usuarios.
    
    Ayuda con:
    - Mejores prácticas para estructura de roles
    - Configuración de permisos granulares
    - Bulk operations para usuarios
    - Troubleshooting de accesos
    """
```

## ⚙️ Configuración e Instalación

### 📋 **Prerrequisitos**
- Python 3.11+
- Acceso a una instancia de Proyecto Semilla
- API Key válida con permisos administrativos

### 🚀 **Instalación**

```bash
# Clonar repositorio
git clone https://github.com/proyecto-semilla/proyecto-semilla.git
cd proyecto-semilla/mcp

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu configuración
```

### 🔧 **Configuración para Claude Code**

```json
{
  "mcpServers": {
    "proyecto-semilla": {
      "command": "python",
      "args": ["/path/to/proyecto-semilla/mcp/server.py"],
      "env": {
        "PROYECTO_SEMILLA_API_URL": "https://api.tu-instancia.com",
        "PROYECTO_SEMILLA_API_KEY": "tu-api-key-aqui",
        "PROYECTO_SEMILLA_DEFAULT_TENANT": "tenant-uuid-opcional"
      }
    }
  }
}
```

### 🔐 **Variables de Entorno**

```bash
# .env
PROYECTO_SEMILLA_API_URL=https://api.tu-instancia.com
PROYECTO_SEMILLA_API_KEY=ps_abc123...
PROYECTO_SEMILLA_DEFAULT_TENANT=tenant-uuid-opcional

# Configuración opcional
MCP_LOG_LEVEL=INFO
MCP_CACHE_TTL=300
MCP_MAX_REQUESTS_PER_MINUTE=100
```

## 🔒 Seguridad y Permisos

### 🛡️ **Autenticación**
- **API Key Validation**: Validación automática de API keys
- **Permission Checking**: Verificación de permisos antes de cada operación
- **Tenant Context**: Operaciones limitadas al contexto del tenant
- **Rate Limiting**: Protección contra abuso

### 🔐 **Principio de Menor Privilegio**
```python
# Ejemplo de verificación de permisos
@require_permissions(["users:read"])
async def list_users_tool(tenant_id: str) -> list:
    # Solo ejecuta si el usuario tiene permisos users:read
    pass

@require_permissions(["users:create"])
async def create_user_tool(tenant_id: str, user_data: dict) -> dict:
    # Solo ejecuta si el usuario tiene permisos users:create
    pass
```

## 🧪 Testing del MCP Server

### 🔧 **Setup de Testing**
```bash
# Ejecutar tests unitarios
pytest tests/

# Tests con coverage
pytest --cov=mcp tests/

# Tests de integración (requiere instancia de PS)
pytest tests/integration/
```

### 🧪 **Mock Server para Testing**
```python
# tests/conftest.py
import pytest
from mcp.testing import MockProyectoSemillaAPI

@pytest.fixture
def mock_api():
    return MockProyectoSemillaAPI()

def test_list_users_tool(mock_api):
    # Test aislado sin dependencias externas
    pass
```

## 🔄 Extensión con Módulos

### 🧩 **Agregar Tools para Módulos Personalizados**

```python
# modules/inventory/tools.py
from mcp.tools.base import BaseTool

class InventoryTools(BaseTool):
    @mcp_tool("list_inventory")
    async def list_inventory(self, tenant_id: str, category: str = None) -> list:
        """Lista items del inventario."""
        # Implementación específica del módulo
        pass
    
    @mcp_tool("update_stock")
    async def update_stock(self, item_id: str, quantity: int) -> dict:
        """Actualiza stock de un item."""
        pass
```

### 📋 **Registro Dinámico de Tools**
```python
# server.py - Registro automático de módulos
class ProyectoSemillaMCPServer(Server):
    async def discover_and_register_modules(self):
        """Descubre y registra tools de módulos activos."""
        active_modules = await self.get_active_modules()
        
        for module in active_modules:
            module_tools = await self.load_module_tools(module.name)
            self.register_tools(module_tools)
```

## 📊 Métricas y Monitoring

### 📈 **Métricas Disponibles**
- **Tool Usage**: Frecuencia de uso de cada tool
- **Response Times**: Tiempo de respuesta promedio
- **Error Rates**: Tasa de errores por tool
- **User Activity**: Actividad por usuario/tenant

### 🔍 **Logging Estructurado**
```python
import structlog

logger = structlog.get_logger("mcp.tools")

@mcp_tool("create_user")
async def create_user(tenant_id: str, user_data: dict) -> dict:
    logger.info("Creating user", tenant_id=tenant_id, email=user_data.get("email"))
    # Implementación
    logger.info("User created", tenant_id=tenant_id, user_id=result.id)
```

## 🗺️ Roadmap del MCP Server

### ✅ **Fase 1 (v0.1.0-v0.3.0)**: Fundación
- [ ] MCP Server básico con tools core
- [ ] Autenticación y permisos básicos
- [ ] Documentación y ejemplos

### 🔮 **Fase 2 (v0.4.0-v0.6.0)**: Expansión
- [ ] Resources contextuales avanzados
- [ ] Prompts especializados por dominio
- [ ] Sistema de cache inteligente
- [ ] Métricas y monitoring

### 🚀 **Fase 3 (v0.7.0-v0.9.0)**: Ecosistema
- [ ] Auto-discovery de módulos
- [ ] Tools dinámicos por tenant
- [ ] Webhooks y eventos en tiempo real
- [ ] Integración con otros MCP servers

## 📞 Soporte y Contribución

### 🤝 **Contribuir**
- **Issues**: Reporta bugs o solicita features
- **Pull Requests**: Contribuye código siguiendo las guías
- **Documentación**: Mejora docs y ejemplos
- **Testing**: Ayuda con cobertura de tests

### 📧 **Contacto**
- **Discord**: Canal #mcp-support
- **Email**: mcp-support@proyectosemilla.dev
- **GitHub**: [Issues](https://github.com/proyecto-semilla/proyecto-semilla/issues)

---

*El MCP Server es lo que hace que Proyecto Semilla sea verdaderamente potente con Claude Code. ¡Hagámoslo increíble juntos!*