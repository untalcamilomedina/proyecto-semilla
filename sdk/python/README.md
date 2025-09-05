# Proyecto Semilla SDK

**SDK Python para desarrollo Vibecoding-native con Proyecto Semilla**

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/proyecto-semilla/proyecto-semilla)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🚀 Características

- ✅ **Type-Safe**: Modelos Pydantic con validación automática
- ✅ **Async/Await**: Operaciones asíncronas con httpx
- ✅ **Auto-Auth**: JWT tokens con refresh automático
- ✅ **Error Handling**: Excepciones específicas y descriptivas
- ✅ **Vibecoding-Ready**: Optimizado para uso con LLMs
- ✅ **Production-Ready**: Tests completos y documentación

## 📦 Instalación

```bash
# Instalar desde el repositorio local
pip install -e ./sdk/python

# O instalar dependencias manualmente
pip install pydantic httpx pyjwt pytest pytest-asyncio
```

## 🏁 Inicio Rápido

```python
import asyncio
from proyecto_semilla import ProyectoSemillaClient

async def main():
    async with ProyectoSemillaClient() as client:
        # Login
        user = await client.login("admin@example.com", "password")
        print(f"Logged in as: {user.full_name}")

        # Listar tenants
        tenants = await client.get_tenants()
        print(f"Available tenants: {len(tenants)}")

        # Generar módulo (Vibecoding core feature)
        from proyecto_semilla.models import ModuleSpec, ModuleCategory

        spec = ModuleSpec(
            name="ecommerce",
            display_name="E-commerce Module",
            description="Complete e-commerce solution",
            category=ModuleCategory.ECOMMERCE,
            features=["products", "cart", "checkout", "payments"],
            entities=[
                {
                    "name": "Product",
                    "fields": [
                        {"name": "name", "type": "string", "required": True},
                        {"name": "price", "type": "float", "required": True},
                        {"name": "description", "type": "text"}
                    ]
                }
            ]
        )

        result = await client.generate_module(spec)
        print(f"Module generated: {result.module_name}")
        print(f"Files created: {result.files_created}")

asyncio.run(main())
```

## 📚 Documentación

### Cliente Principal

```python
from proyecto_semilla import ProyectoSemillaClient

# Inicialización
client = ProyectoSemillaClient(
    base_url="http://localhost:7777",  # URL de tu instancia
    api_key="your-api-key",            # O usa email/password
    timeout=30.0,                      # Timeout en segundos
    auto_refresh=True                  # Auto-refresh tokens
)

# Context manager (recomendado)
async with ProyectoSemillaClient() as client:
    # Tu código aquí
    pass
```

### Autenticación

```python
# Login con email/password
user = await client.login("user@example.com", "password")
print(f"Welcome {user.full_name}!")

# Verificar autenticación
if client.is_authenticated():
    print("Authenticated!")

# Logout
await client.logout()
```

### Gestión de Tenants

```python
# Listar todos los tenants
tenants = await client.get_tenants()
for tenant in tenants:
    print(f"{tenant.name} ({tenant.slug})")

# Obtener tenant específico
tenant = await client.get_tenant("tenant-id")

# Crear nuevo tenant
from proyecto_semilla.models import TenantCreate
new_tenant = await client.create_tenant(
    TenantCreate(name="Mi Empresa", slug="mi-empresa")
)
```

### Gestión de Usuarios

```python
# Listar usuarios
users = await client.get_users()
# O filtrar por tenant
users = await client.get_users(tenant_id="tenant-1")

# Crear usuario
from proyecto_semilla.models import UserCreate
new_user = await client.create_user(
    UserCreate(
        email="newuser@example.com",
        password="securepassword",
        first_name="Juan",
        last_name="Pérez",
        tenant_id="tenant-1"
    )
)
```

### Generación de Módulos (Vibecoding Core)

```python
from proyecto_semilla.models import ModuleSpec, ModuleCategory, EntityField

# Definir especificación del módulo
spec = ModuleSpec(
    name="inventory_system",
    display_name="Sistema de Inventario",
    description="Gestión completa de inventario y stock",
    version="1.0.0",
    category=ModuleCategory.INVENTORY,
    features=[
        "Product management",
        "Stock tracking",
        "Inventory reports",
        "Low stock alerts"
    ],
    entities=[
        {
            "name": "Product",
            "description": "Productos en inventario",
            "fields": [
                EntityField(
                    name="name",
                    type="string",
                    required=True,
                    max_length=100
                ),
                EntityField(
                    name="sku",
                    type="string",
                    required=True,
                    max_length=50
                ),
                EntityField(
                    name="price",
                    type="float",
                    required=True
                ),
                EntityField(
                    name="stock_quantity",
                    type="integer",
                    required=True,
                    default=0
                )
            ]
        }
    ],
    apis=[
        {
            "path": "/api/v1/products",
            "method": "GET",
            "description": "Listar productos"
        },
        {
            "path": "/api/v1/products",
            "method": "POST",
            "description": "Crear producto"
        }
    ],
    ui_components=[
        "dashboard",
        "product_list",
        "product_form",
        "inventory_reports"
    ]
)

# Generar módulo completo
result = await client.generate_module(spec)
print(f"✅ Módulo '{result.module_name}' generado exitosamente!")
print(f"📁 Archivos creados: {result.files_created}")
print(f"🔌 APIs generadas: {result.apis_generated}")
print(f"🖥️ Componentes UI: {result.ui_components_created}")
```

## 🧪 Testing

```bash
# Ejecutar tests
pytest sdk/python/tests/

# Con coverage
pytest --cov=proyecto_semilla --cov-report=html

# Tests específicos
pytest sdk/python/tests/test_client.py -v
```

## 📋 Modelos de Datos

### Core Models

| Model | Descripción |
|-------|-------------|
| `Tenant` | Información de tenant multi-tenant |
| `User` | Datos de usuario con tenant association |
| `ModuleSpec` | Especificación para generar módulos |
| `ModuleStatus` | Estado de módulos generados |
| `GenerationResult` | Resultado de generación de módulos |

### Enums

| Enum | Valores |
|------|---------|
| `ModuleCategory` | cms, inventory, crm, finance, analytics, etc. |
| `UIComponent` | dashboard, list_view, form, detail_view, etc. |

## 🚨 Manejo de Errores

```python
from proyecto_semilla.exceptions import (
    AuthenticationError,
    APIError,
    ValidationError,
    ProyectoSemillaError
)

try:
    result = await client.generate_module(spec)
except AuthenticationError:
    print("Error: No autenticado")
except ValidationError as e:
    print(f"Error de validación: {e.message}")
    if e.details.get('field'):
        print(f"Campo problemático: {e.details['field']}")
except APIError as e:
    print(f"Error de API: {e.status_code} - {e.message}")
except ProyectoSemillaError as e:
    print(f"Error general: {e.message}")
```

## 🔧 Configuración Avanzada

### Custom Headers

```python
# Headers personalizados
client.client.headers.update({
    'X-Custom-Header': 'value',
    'User-Agent': 'My-App/1.0'
})
```

### Timeout Configuration

```python
# Timeout personalizado
client = ProyectoSemillaClient(timeout=60.0)
```

### API Key Authentication

```python
# Usar API key en lugar de login
client = ProyectoSemillaClient(api_key="your-api-key")
```

## 🤖 Integración con LLMs

El SDK está optimizado para uso con LLMs como Claude:

```python
# Claude puede ejecutar esto automáticamente
"""
Genera un módulo de CRM con las siguientes características:
- Gestión de contactos
- Seguimiento de leads
- Dashboard de ventas
- Reportes de conversión
"""

# El LLM puede escribir código como este:
from proyecto_semilla import ProyectoSemillaClient, ModuleSpec, ModuleCategory

async def generate_crm_module():
    spec = ModuleSpec(
        name="crm_system",
        display_name="CRM System",
        description="Customer Relationship Management",
        category=ModuleCategory.CRM,
        features=["contacts", "leads", "sales_dashboard", "reports"],
        # ... resto de la configuración
    )

    async with ProyectoSemillaClient() as client:
        await client.login("admin@example.com", "password")
        result = await client.generate_module(spec)
        return result
```

## 📈 Métricas y Monitoreo

```python
# Health check
health = await client.health_check()
print(f"Status: {health['status']}")
print(f"Version: {health['version']}")
print(f"Response time: {health['response_time']:.2f}s")

# Información de autenticación
if client.is_authenticated():
    user = client.get_current_user()
    tenant = client.get_current_tenant()
    print(f"Usuario: {user.full_name}")
    print(f"Tenant: {tenant}")
```

## 🛠️ Desarrollo y Contribución

### Estructura del Proyecto

```
sdk/python/
├── proyecto_semilla/
│   ├── __init__.py      # Exports principales
│   ├── client.py        # Cliente principal
│   ├── models.py        # Modelos Pydantic
│   ├── auth.py          # Gestión de autenticación
│   ├── exceptions.py    # Excepciones personalizadas
│   └── utils.py         # Utilidades
├── tests/
│   ├── __init__.py
│   ├── test_client.py   # Tests del cliente
│   └── test_models.py   # Tests de modelos
├── README.md            # Esta documentación
├── setup.py            # Configuración de paquete
└── requirements.txt    # Dependencias
```

### Agregar Nuevas Features

1. **Modelos**: Agregar a `models.py` con validaciones Pydantic
2. **Métodos**: Agregar al cliente en `client.py`
3. **Tests**: Crear tests en `tests/`
4. **Documentación**: Actualizar este README

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](../LICENSE) para más detalles.

## 🆘 Soporte

- 📧 **Email**: dev@proyectosemilla.dev
- 💬 **Discord**: [Proyecto Semilla Community](https://discord.gg/proyecto-semilla)
- 📖 **Docs**: [Documentación Completa](https://docs.proyectosemilla.dev)

---

**🌱 Proyecto Semilla - La primera plataforma SaaS Vibecoding-native** 🚀